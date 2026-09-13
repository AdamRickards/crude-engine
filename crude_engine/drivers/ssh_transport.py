"""
Vendor-agnostic SSH state machine transport.

Reads SSH_state.yaml for CLI level definitions, navigates between levels
automatically, and handles auth gates. The vendor specificity lives
in the YAML, not this code.
"""

import os
import re
import logging
import yaml
from collections import deque
from typing import Dict, List, Union, Any, Optional

from netmiko import ConnectHandler
from napalm.base.exceptions import ConnectionException

logger = logging.getLogger(__name__)

# Bounded append-only inspect session log (#222). Hang never returns last_cli;
# progress snaps this tail on phase=call timeout without waiting for the thread.
_SESSION_RING_MAX = 200
_SESSION_LOG_TAIL_CHARS = 8192


class SSHDriver:
    """SSH transport with YAML-driven CLI state machine."""

    def __init__(self, hostname, username, password, timeout, port=22,
                 state_yaml=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout
        self.port = port
        self.connection = None
        self._factory_default = False

        # State machine
        self._state = self._load_state(state_yaml)
        self._current_level = None
        self._setup_done = set()  # levels whose on_enter has run
        self._prompt_re = self._build_prompt_re()

        # Protocol defaults from registry-declared YAML
        from crude_engine.transport_registry import get_protocol_yaml_path
        proto_yaml = get_protocol_yaml_path('ssh')
        proto_defaults = {}
        if proto_yaml and os.path.exists(proto_yaml):
            with open(proto_yaml) as f:
                proto_defaults = yaml.safe_load(f).get('defaults', {})
        self._cmd_verify = proto_defaults.get('cmd_verify', True)

        # Append-only session ring for inspect hang diagnosis (#222).
        # Prefer Netmiko SessionLog on the live connection; ring always
        # records structured open/nav/send/recv so offline mocks still work.
        self._session_ring: deque = deque(maxlen=_SESSION_RING_MAX)
        self._netmiko_session_log = None

    # ------------------------------------------------------------------
    # YAML loading
    # ------------------------------------------------------------------

    def _load_state(self, state_yaml=None):
        if state_yaml is None:
            state_yaml = os.path.join(
                os.path.dirname(__file__), 'SSH_state.yaml'
            )
        with open(state_yaml) as f:
            return yaml.safe_load(f)

    def _build_prompt_re(self):
        """Build combined regex from all level prompt patterns."""
        patterns = []
        for level_def in self._state['levels'].values():
            patterns.append(level_def['prompt_pattern'])
        return '|'.join(f'(?:{p})' for p in patterns)

    # ------------------------------------------------------------------
    # Inspect session log (#222)
    # ------------------------------------------------------------------

    def _session_append(self, line: str) -> None:
        """Record one append-only session event; publish progress tail."""
        if not line:
            return
        # Never put credentials in the ring (auth password is noted as marker).
        self._session_ring.append(line)
        self._publish_session_log_tail()

    def session_log_tail(self, max_chars: int = _SESSION_LOG_TAIL_CHARS) -> str:
        """Bounded tail: structured ring + Netmiko SessionLog buffer if any.

        Safe to call from the harness poller while the worker thread is hung —
        StringIO.getvalue / deque copy are the snapshot surface.
        """
        parts = list(self._session_ring)
        buf = self._netmiko_session_log
        if buf is not None:
            raw = ""
            try:
                # netmiko.SessionLog keeps an in-memory slog_buffer
                slog = getattr(buf, "slog_buffer", None)
                if slog is not None:
                    raw = slog.getvalue() or ""
                elif hasattr(buf, "getvalue"):
                    raw = buf.getvalue() or ""
            except Exception:
                raw = ""
            if raw:
                parts.append("--- netmiko ---")
                parts.append(raw if len(raw) <= max_chars else raw[-max_chars:])
        text = "\n".join(parts)
        if len(text) > max_chars:
            text = text[-max_chars:]
        return text

    def _publish_session_log_tail(self) -> None:
        prog = getattr(self, "_inspect_progress", None)
        if not isinstance(prog, dict):
            return
        try:
            prog["session_log_tail"] = self.session_log_tail()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    def open(self):
        """Open SSH connection, detect factory gate, navigate to priv."""
        try:
            device = {
                'device_type': 'generic_termserver',
                'host': self.hostname,
                'username': self.username,
                'password': self.password,
                'port': self.port,
                'timeout': self.timeout,
                'fast_cli': False,
            }
            # Prefer Netmiko SessionLog (in-memory) on the same transport path.
            try:
                from netmiko.session_log import SessionLog
                no_log = {}
                if self.password:
                    no_log["password"] = self.password
                self._netmiko_session_log = SessionLog(
                    record_writes=True, no_log=no_log or None
                )
                device["session_log"] = self._netmiko_session_log
            except Exception as e:
                logger.debug("SSH session_log unavailable: %s", e)
                self._netmiko_session_log = None

            self._session_append("open")
            self.connection = ConnectHandler(**device)
            self.connection.set_base_prompt()

            output = self.connection.read_channel()
            self._session_append(
                f"open: read_channel {len(output or '')} bytes"
            )

            # Check factory default gate
            factory_gate = self._state.get('gates', {}).get('factory_default', {})
            if factory_gate and factory_gate.get('detect') in (output or ''):
                self._factory_default = True
                self._session_append("open: factory_default gate")
                return

            self._current_level = self._state['initial_level']
            self.navigate_to('priv')
            self._session_append("open: at priv")
        except ConnectionException:
            raise
        except Exception as e:
            raise ConnectionException(f"SSH connection failed: {str(e)}")

    def close(self):
        """Disconnect, handling logout gates from YAML.

        Gate `detect` strings in SSH_state.yaml are literal prompt fragments
        (e.g. ``Are you sure (Y/N)``). Netmiko ``read_until_pattern`` compiles
        them as regex, so parentheses must be escaped or the live logout
        confirm never matches and teardown hangs under the inspect call
        wall (#224).
        """
        if self.connection:
            try:
                # Navigate to user level first, then logout
                if self._current_level and self._current_level != 'user':
                    try:
                        self.navigate_to('user')
                    except Exception as e:
                        logger.warning("SSH close: navigate_to user failed: %s", e)

                user_def = self._state['levels'].get('user', {})
                exit_def = user_def.get('exit', {})
                gates = user_def.get('gates', [])

                if exit_def and exit_def.get('command'):
                    logout_cmd = exit_def['command']
                    # Publish logout as last_command so close hang receipts
                    # are not stuck on a stale show (#224).
                    self.last_command = logout_cmd
                    prog = getattr(self, "_inspect_progress", None)
                    if isinstance(prog, dict):
                        prog["last_command"] = logout_cmd
                    self._session_append(f"send: {logout_cmd}")
                    self.connection.write_channel(logout_cmd + '\n')
                    for gate in gates:
                        try:
                            detect = gate['detect']
                            gate_timeout = gate.get('read_timeout', 1)
                            output = self.connection.read_until_pattern(
                                re.escape(detect), read_timeout=gate_timeout
                            )
                            if detect in (output or ''):
                                self._session_append(
                                    f"close gate: {detect!r} -> "
                                    f"{gate.get('response')!r}"
                                )
                                self.connection.write_channel(
                                    gate['response'] + '\n'
                                )
                        except Exception:
                            break
            except Exception as e:
                logger.warning("SSH close: logout sequence failed: %s", e)
            finally:
                self.connection.disconnect()
                self.connection = None
                self._current_level = None
                self._setup_done.clear()

    # ------------------------------------------------------------------
    # Command execution
    # ------------------------------------------------------------------

    def onboard(self, new_password):
        """Set initial password on factory-fresh device via SSH."""
        import time
        if not self.connection:
            raise ConnectionException("SSH connection is not open")
        self.connection.write_channel(new_password + '\n')
        time.sleep(1)
        self.connection.write_channel(new_password + '\n')
        time.sleep(2)
        return True

    def save_config(self, dest='nvm'):
        """Save running config to NVM."""
        self.navigate_to('priv')
        self.connection.send_command_timing(f'copy config running-config {dest}')

    def clear_config(self, keep_ip=False):
        """Clear running config. Device warm-restarts."""
        self.navigate_to('priv')
        cmd = 'clear config keep-ip' if keep_ip else 'clear config'
        self.connection.send_command_timing(cmd)
        self.connection.send_command_timing('y')

    def clear_factory(self, erase_all=False):
        """Factory reset. Device reboots."""
        self.navigate_to('priv')
        cmd = 'clear factory erase-all' if erase_all else 'clear factory'
        self.connection.send_command_timing(cmd)
        self.connection.send_command_timing('y')

    def cli(self, commands: Union[List[str], str],
            encoding: str = 'text',
            cmd_verify: bool = None) -> Dict[str, str]:
        """Execute one or more commands and return output dict.

        Args:
            cmd_verify: Override per-command. None = use SSH.yaml default.
        """
        if not self.connection:
            raise ConnectionException("SSH connection is not open")

        if isinstance(commands, str):
            commands = [commands]

        verify = cmd_verify if cmd_verify is not None else self._cmd_verify
        results = {}
        for cmd in commands:
            # Inspect hang never returns, so last_cli is empty on call-timeout.
            # Publish last_command + session_log_tail before send so the
            # harness can snapshot from shared progress without waiting
            # for this thread (#218 / #222).
            self.last_command = cmd
            prog = getattr(self, "_inspect_progress", None)
            if isinstance(prog, dict):
                prog["last_command"] = cmd
            self._session_append(f"send: {cmd}")
            output = self.connection.send_command(
                cmd, expect_string=self._prompt_re, read_timeout=10,
                cmd_verify=verify
            )
            # Recv note (only reached if prompt matched / send returned).
            preview = (output or "").strip().replace("\n", " ")[:160]
            self._session_append(
                f"recv: {len((output or '').strip())}B {preview!r}"
            )
            results[cmd] = output.strip()
        return results

    # ------------------------------------------------------------------
    # State machine navigation
    # ------------------------------------------------------------------

    def navigate_to(self, target: str, params: Optional[Dict] = None):
        """Navigate from current level to target level.

        Computes path via parent chains: find LCA, exit up to LCA,
        enter down to target. Runs on_enter setup commands once per
        session.
        """
        if params is None:
            params = {}

        levels = self._state['levels']
        if target not in levels:
            raise ValueError(f"Unknown level: {target}")

        # For parameterized levels (config_interface), always re-enter
        # if params differ — but we don't track params, so always
        # re-navigate for parameterized levels
        target_def = levels[target]
        is_parameterized = bool(target_def.get('enter', {}).get('params'))

        if self._current_level == target and not is_parameterized:
            return

        self._session_append(
            f"navigate: {self._current_level} -> {target}"
        )

        # For parameterized levels at the same level, exit first so we
        # re-enter with new params (e.g. switching from interface 1/1
        # to interface 1/2)
        if self._current_level == target and is_parameterized:
            exit_def = target_def.get('exit', {})
            if exit_def and exit_def.get('command'):
                self._session_append(f"nav exit: {exit_def['command']}")
                self.connection.send_command(
                    exit_def['command'],
                    expect_string=self._prompt_re,
                    read_timeout=5
                )
            self._current_level = target_def.get('parent')

        # Build ancestor chains
        current_ancestors = self._ancestors(self._current_level)
        target_ancestors = self._ancestors(target)

        # Find LCA (lowest common ancestor)
        current_set = set(current_ancestors)
        lca = None
        for ancestor in target_ancestors:
            if ancestor in current_set:
                lca = ancestor
                break

        if lca is None:
            raise ValueError(
                f"No common ancestor between {self._current_level} and {target}"
            )

        # Exit from current up to LCA
        exit_path = []
        for level in current_ancestors:
            if level == lca:
                break
            exit_path.append(level)

        for level in exit_path:
            level_def = levels[level]
            exit_def = level_def.get('exit', {})
            if exit_def and exit_def.get('command'):
                self._session_append(f"nav exit: {exit_def['command']}")
                self.connection.send_command(
                    exit_def['command'],
                    expect_string=self._prompt_re,
                    read_timeout=5
                )
            self._current_level = exit_def.get('to', level_def.get('parent'))

        # Enter from LCA down to target
        enter_path = []
        for level in target_ancestors:
            if level == lca:
                break
            enter_path.append(level)
        enter_path.reverse()  # top-down order

        for level in enter_path:
            level_def = levels[level]
            enter_def = level_def.get('enter', {})
            if not enter_def:
                continue

            cmd = enter_def['command']
            # Substitute params into command
            for key, val in params.items():
                cmd = cmd.replace('{' + key + '}', str(val))

            if enter_def.get('auth'):
                # Auth transition: send command, wait for password prompt,
                # send password (never log the password itself).
                auth_pattern = enter_def.get('auth_pattern', 'Password:')
                self._session_append(f"nav enter: {cmd} (auth)")
                output = self.connection.send_command(
                    cmd,
                    expect_string=f'{auth_pattern}|{self._prompt_re}',
                    read_timeout=5
                )
                if auth_pattern in output:
                    self._session_append("nav enter: (password)")
                    self.connection.send_command(
                        self.password,
                        expect_string=self._prompt_re,
                        read_timeout=5
                    )
            else:
                self._session_append(f"nav enter: {cmd}")
                self.connection.send_command(
                    cmd,
                    expect_string=self._prompt_re,
                    read_timeout=5
                )

            self._current_level = level

            # Run on_enter setup commands (once per session)
            if level not in self._setup_done:
                for setup_cmd in level_def.get('on_enter', []):
                    self._session_append(f"nav on_enter: {setup_cmd}")
                    self.connection.send_command(
                        setup_cmd,
                        expect_string=self._prompt_re,
                        read_timeout=5
                    )
                self._setup_done.add(level)

    def _ancestors(self, level: str) -> List[str]:
        """Return ancestor chain: [level, parent, grandparent, ...]."""
        levels = self._state['levels']
        chain = []
        current = level
        while current:
            chain.append(current)
            current = levels.get(current, {}).get('parent')
        return chain

    # ------------------------------------------------------------------
    # Level inference
    # ------------------------------------------------------------------

    def infer_level(self, command: str) -> str:
        """Infer target level from command string using YAML patterns."""
        inference = self._state.get('level_inference', {})
        for level, pattern in inference.get('patterns', {}).items():
            if re.search(pattern, command):
                return level
        return inference.get('default', 'config')

    # ------------------------------------------------------------------
    # Backward-compat wrappers (used by existing code)
    # ------------------------------------------------------------------

    def _enable(self):
        self.navigate_to('priv')

    def _disable(self):
        self.navigate_to('user')

    def _config_mode(self):
        self.navigate_to('config')

    def _exit_config_mode(self):
        self.navigate_to('priv')

    def _config_interface_mode(self, interface: str):
        self.navigate_to('config_interface', params={'interface': interface})

    def _vlan_database_mode(self):
        self.navigate_to('vlan_database')

    def disable_pagination(self):
        """No-op: handled by on_enter in priv level."""
        pass

    def is_factory_default(self) -> bool:
        return self._factory_default
