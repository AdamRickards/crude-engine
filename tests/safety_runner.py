"""safety_runner.py — CLAMPS-style pre/post hooks for ring-touching methods.

Reads tests/safety_protocols.yaml and applies declared pre/post protocols
around method calls. Used by:

  - test_setter_pairs.py (via SafetyRunner.run_with_safety)
  - test_crud_pairs.py   (same)
  - tests/release_matrix.py worker

The engine knows nothing about safety protocols. They are a TEST
infrastructure concern. See docs/RELEASE_GATE.md § "Safety protocols".

Capture/restore pattern matches test_setter_pairs.py: read the field's
current value before applying `must_equal`, restore after the wrapped
method returns (or fails). If the captured value already equals
must_equal, no change is made and no restore is needed.
"""

from __future__ import annotations

import os
import re
from typing import Any, Callable

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROTOCOLS_PATH = os.path.join(HERE, "safety_protocols.yaml")
DEVICE_STATE_PATH = os.path.join(HERE, "device_state.json")


class SafetyError(RuntimeError):
    """Raised when a safety protocol cannot be satisfied or restored."""


class SafetyPrerequisiteMissing(SafetyError):
    """A required device_state variable was not populated by the gather phase."""


_VAR_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def _resolve_var(template: Any, device_state: dict) -> Any:
    """Substitute {var} placeholders against device_state. Pass-through non-strings."""
    if not isinstance(template, str):
        return template

    def replace(match: re.Match) -> str:
        key = match.group(1)
        if key not in device_state:
            raise SafetyPrerequisiteMissing(
                f"safety protocol references {{{key}}} but device_state has no such key"
            )
        val = device_state[key]
        if val is None or val == "":
            raise SafetyPrerequisiteMissing(
                f"safety protocol references {{{key}}} but value is empty"
            )
        return str(val)

    return _VAR_RE.sub(replace, template)


def _resolve_args(spec: dict, device_state: dict) -> dict:
    """Recursively resolve all {var} placeholders in a dict of args."""
    out = {}
    for k, v in spec.items():
        if isinstance(v, dict):
            out[k] = _resolve_args(v, device_state)
        elif isinstance(v, list):
            out[k] = [_resolve_var(item, device_state) for item in v]
        else:
            out[k] = _resolve_var(v, device_state)
    return out


def _read_field(device, read_method: str, index: Any, field: str) -> Any:
    """Call the named getter and dig out the field for the indexed row.

    For table getters: result[index][field].
    For flat getters: result[field].
    """
    fn = getattr(device, read_method)
    result = fn()
    if isinstance(result, tuple):
        result = result[0]
    if not isinstance(result, dict):
        raise SafetyError(
            f"{read_method} returned {type(result).__name__}, not dict"
        )
    if index is None:
        if field not in result:
            raise SafetyError(
                f"{read_method} result has no field {field!r}; got keys: "
                f"{list(result.keys())[:8]}"
            )
        return result[field]
    # Table — try the index, then str(index)
    row = result.get(index, result.get(str(index)))
    if row is None:
        raise SafetyError(
            f"{read_method} result has no row [{index!r}]; got keys: "
            f"{list(result.keys())[:8]}"
        )
    if not isinstance(row, dict):
        raise SafetyError(
            f"{read_method}[{index!r}] is {type(row).__name__}, not dict"
        )
    if field not in row:
        raise SafetyError(
            f"{read_method}[{index!r}] has no field {field!r}; got keys: "
            f"{list(row.keys())[:8]}"
        )
    return row[field]


def _write_field(device, write_method: str, index: Any, field: str, value: Any) -> None:
    """Call the named setter to apply a single field change."""
    fn = getattr(device, write_method)
    if index is None:
        fn(**{field: value})
    else:
        # test_setter_pairs convention: index goes positional or as 'interface'
        try:
            fn(index, **{field: value})
        except TypeError:
            fn(interface=index, **{field: value})


class SafetyRunner:
    """Loads safety_protocols.yaml and applies the declared protocols."""

    def __init__(self, protocols_path: str = PROTOCOLS_PATH):
        self.protocols_path = protocols_path
        self._cache: dict | None = None

    @property
    def protocols(self) -> dict:
        if self._cache is None:
            if not os.path.exists(self.protocols_path):
                self._cache = {}
            else:
                with open(self.protocols_path) as f:
                    data = yaml.safe_load(f) or {}
                self._cache = data.get("protocols", {}) or {}
        return self._cache

    def has_protocol(self, method_name: str) -> bool:
        return method_name in self.protocols

    def run_with_safety(
        self,
        device,
        method_name: str,
        wrapped: Callable[[], Any],
        device_state: dict | None = None,
    ) -> Any:
        """Apply the safety protocol for `method_name` around `wrapped()`.

        - If no protocol is declared for the method, just calls wrapped().
        - If a protocol is declared but its required state vars are missing
          from device_state, raises SafetyPrerequisiteMissing.
        - Captures pre-values, applies must_equal, runs wrapped, restores.
        - Restore is best-effort: if restore fails, the error is attached to
          the SafetyError raised after wrapped() returned successfully.

        device_state defaults to {} (no variables available — fine for
        methods with no requires_state).
        """
        proto = self.protocols.get(method_name)
        if not proto:
            return wrapped()

        device_state = device_state or {}

        # 0. Check prerequisites
        for var in proto.get("requires_state", []) or []:
            if var not in device_state:
                raise SafetyPrerequisiteMissing(
                    f"safety protocol for {method_name} requires "
                    f"device_state[{var!r}] but it is not set"
                )

        # 1. Capture + apply require_during entries
        captured: list[tuple[dict, Any]] = []  # (entry, original_value)
        for entry in proto.get("require_during", []) or []:
            target = _resolve_args(entry["target"], device_state)
            must_equal = _resolve_var(entry["must_equal"], device_state)

            current = _read_field(
                device,
                target["read_method"],
                target.get("index"),
                target["field"],
            )

            if current == must_equal:
                # Already in safe state — no change, no restore needed.
                captured.append((entry, current))
                continue

            _write_field(
                device,
                target["write_method"],
                target.get("index"),
                target["field"],
                must_equal,
            )
            captured.append((entry, current))

        # 2. Run the wrapped method
        wrapped_error: Exception | None = None
        result = None
        try:
            result = wrapped()
        except Exception as e:
            wrapped_error = e

        # 3. Restore in reverse order. Best-effort.
        restore_errors: list[str] = []
        for entry, original in reversed(captured):
            target = _resolve_args(entry["target"], device_state)
            must_equal = _resolve_var(entry["must_equal"], device_state)
            if original == must_equal:
                continue  # nothing changed, nothing to restore
            try:
                _write_field(
                    device,
                    target["write_method"],
                    target.get("index"),
                    target["field"],
                    original,
                )
            except Exception as e:
                restore_errors.append(
                    f"{target['write_method']}({target.get('index')}, "
                    f"{target['field']}={original!r}): {e}"
                )

        if restore_errors:
            msg = "; ".join(restore_errors)
            if wrapped_error:
                raise SafetyError(
                    f"wrapped {method_name} failed AND safety restore failed: "
                    f"wrapped={wrapped_error}; restore=[{msg}]"
                ) from wrapped_error
            raise SafetyError(f"safety restore failed: {msg}")

        if wrapped_error:
            raise wrapped_error

        return result


# Module-level singleton for convenience
_default_runner: SafetyRunner | None = None


def default_runner() -> SafetyRunner:
    global _default_runner
    if _default_runner is None:
        _default_runner = SafetyRunner()
    return _default_runner
