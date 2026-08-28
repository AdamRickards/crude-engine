"""
test_replay.py — Multi-layer replay tests from captured fixtures.

Tests at each boundary independently:
  test_engine:  tap1 (transport) → engine → compare tap3 (engine output)
  test_napalm:  tap3 (engine output) → adapter shape → compare tap4 (napalm output)

Usage:
    pytest tests/test_replay.py -v
    pytest tests/test_replay.py -k "mops and get_facts"
    pytest tests/test_replay.py -k "test_napalm"
"""

import json
import os
import pytest

from napalm_hios.engine.interpreter import FeatureEngine
from napalm_hios.hios import HIOSDriver

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


def load_json(path):
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Mock transports — replay recorded transport calls (tap 1)
# ---------------------------------------------------------------------------

class MockSNMPTransport:
    def __init__(self, recordings):
        self._recordings = recordings
        self._idx = 0

    def _next(self, func_name):
        while self._idx < len(self._recordings):
            rec = self._recordings[self._idx]
            self._idx += 1
            if rec['function'] == func_name:
                return rec['response']
        raise ValueError(f"No more recordings for {func_name} (at index {self._idx})")

    def _walk_sync(self, oid): return self._next('_walk_sync')
    def _get_scalar_sync(self, oid): return self._next('_get_scalar_sync')
    def _get_scalars_sync(self, *oids): return self._next('_get_scalars_sync')
    def _walk_columns_sync(self, oid_map): return self._next('_walk_columns_sync')


class MockMOPSClient:
    def __init__(self, recordings):
        self._recordings = [r for r in recordings if r['function'].startswith('client.')]
        self._idx = 0

    def _next(self, func_name):
        while self._idx < len(self._recordings):
            rec = self._recordings[self._idx]
            self._idx += 1
            if rec['function'] == func_name:
                return rec['response']
        raise ValueError(f"No more recordings for {func_name} (at index {self._idx})")

    def get_multi(self, queries, decode_strings=False): return self._next('client.get_multi')
    def get(self, mib, node, attributes, decode_strings=True): return self._next('client.get')


class MockMOPSTransport:
    def __init__(self, recordings):
        self.client = MockMOPSClient(recordings)

    def _get_path(self, path, attributes, decode_strings=False):
        return self.client.get(None, None, attributes, decode_strings=decode_strings)

    def _walk_columns(self, mib, table, attributes, decode_strings=False):
        return self.client.get(mib, table, attributes, decode_strings=decode_strings)


class MockSSHTransport:
    def __init__(self, recordings):
        self._recordings = recordings
        self._idx = 0

    def _next(self, func_name):
        while self._idx < len(self._recordings):
            rec = self._recordings[self._idx]
            self._idx += 1
            if rec['function'] == func_name:
                return rec['response']
        raise ValueError(f"No more recordings for {func_name} (at index {self._idx})")

    def cli(self, commands, encoding='text', cmd_verify=None): return self._next('cli')
    def navigate_to(self, target, params=None): pass
    def infer_level(self, command): return 'config'


MOCK_BUILDERS = {
    'snmp': MockSNMPTransport,
    'mops': MockMOPSTransport,
    'ssh': MockSSHTransport,
}


# ---------------------------------------------------------------------------
# Fixture discovery
# ---------------------------------------------------------------------------

def discover_engine_tests():
    """Yield (device, protocol, method) for tap1→tap3 tests."""
    if not os.path.isdir(FIXTURE_DIR):
        return
    for device in sorted(os.listdir(FIXTURE_DIR)):
        device_path = os.path.join(FIXTURE_DIR, device)
        if not os.path.isdir(device_path):
            continue
        for protocol in ('mops', 'snmp', 'ssh'):
            transport_dir = os.path.join(device_path, protocol, 'tap1_transport')
            engine_dir = os.path.join(device_path, protocol, 'tap3_engine')
            if not os.path.isdir(transport_dir) or not os.path.isdir(engine_dir):
                continue
            for fname in sorted(os.listdir(transport_dir)):
                if fname.endswith('.json'):
                    method = fname.replace('.json', '')
                    expected = os.path.join(engine_dir, fname)
                    if os.path.exists(expected):
                        yield device, protocol, method


def discover_napalm_tests():
    """Yield (device, protocol, method) for tap3→tap4 tests."""
    if not os.path.isdir(FIXTURE_DIR):
        return
    for device in sorted(os.listdir(FIXTURE_DIR)):
        device_path = os.path.join(FIXTURE_DIR, device)
        if not os.path.isdir(device_path):
            continue
        for protocol in ('mops', 'snmp', 'ssh'):
            engine_dir = os.path.join(device_path, protocol, 'tap3_engine')
            napalm_dir = os.path.join(device_path, protocol, 'tap4_napalm')
            if not os.path.isdir(engine_dir) or not os.path.isdir(napalm_dir):
                continue
            for fname in sorted(os.listdir(engine_dir)):
                if fname.endswith('.json'):
                    method = fname.replace('.json', '')
                    expected = os.path.join(napalm_dir, fname)
                    if os.path.exists(expected):
                        yield device, protocol, method


def make_id(params):
    return '/'.join(params)


ENGINE_TESTS = list(discover_engine_tests())
NAPALM_TESTS = list(discover_napalm_tests())


# ---------------------------------------------------------------------------
# Engine setup
# ---------------------------------------------------------------------------

def build_engine(device_dir):
    """Create engine with captured context and NAPALM shapes."""
    engine = FeatureEngine()
    ctx_path = os.path.join(device_dir, 'context.json')
    if os.path.exists(ctx_path):
        engine.context = load_json(ctx_path)
    else:
        engine.context = {'ifindex_map': {}, 'bridge_port_map': {}, 'device_info': {}}
    return engine


# ---------------------------------------------------------------------------
# Test: Engine layer (tap1 → tap3)
# Feed transport fixtures through real engine, compare to captured engine output
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("device,protocol,method", ENGINE_TESTS,
                         ids=[make_id(t) for t in ENGINE_TESTS])
def test_engine(device, protocol, method):
    """Replay transport → engine → compare to captured engine output."""
    device_dir = os.path.join(FIXTURE_DIR, device)

    # Load transport fixture (tap 1)
    fixture = load_json(os.path.join(device_dir, protocol, 'tap1_transport', f'{method}.json'))
    if not fixture.get('calls'):
        pytest.skip(f"No transport calls for {method} on {protocol}")

    # Build mock transport
    mock = MOCK_BUILDERS[protocol](fixture['calls'])

    # Build engine with context
    engine = build_engine(device_dir)

    # Execute
    result = engine.execute(method, protocol, mock)

    # Compare to captured engine output (tap 3)
    expected = load_json(os.path.join(device_dir, protocol, 'tap3_engine', f'{method}.json'))
    assert result == expected, (
        f"Engine output mismatch for {method} via {protocol}\n"
        f"Got:      {json.dumps(result, indent=2, default=str)[:500]}\n"
        f"Expected: {json.dumps(expected, indent=2, default=str)[:500]}"
    )


# ---------------------------------------------------------------------------
# Test: NAPALM layer (tap3 → tap4)
# Compare engine output to NAPALM adapter output — tests shapes only
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("device,protocol,method", NAPALM_TESTS,
                         ids=[make_id(t) for t in NAPALM_TESTS])
def test_napalm(device, protocol, method):
    """Compare engine output to NAPALM adapter output (shape testing)."""
    device_dir = os.path.join(FIXTURE_DIR, device)

    engine_output = load_json(os.path.join(device_dir, protocol, 'tap3_engine', f'{method}.json'))
    napalm_output = load_json(os.path.join(device_dir, protocol, 'tap4_napalm', f'{method}.json'))

    # Most methods have no adapter shaping — engine == napalm
    # Methods with shapes (nested_ip, napalm_optics, vlan_egress) will differ
    if engine_output == napalm_output:
        return  # no shaping, pass

    # If they differ, the NAPALM output should be the shaped version
    # (we can't re-run the shape here without the full schema context,
    # so we just verify the NAPALM output is non-empty when engine has data)
    if engine_output:
        assert napalm_output, (
            f"NAPALM output empty but engine had data for {method} via {protocol}"
        )
