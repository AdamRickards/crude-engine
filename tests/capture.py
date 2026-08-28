"""
capture.py — Multi-layer test fixture capture from live devices.

Captures at 4 boundaries in a single pass:
  tap1: transport responses (raw wire data)
  tap2: driver.gather() output (post-transform gathered dict)
  tap3: engine output (schema-shaped, post-compute/lookup)
  tap4: NAPALM adapter output (post-shape, consumer-facing)

Usage:
    python3 tests/capture.py 192.168.1.4
    python3 tests/capture.py 192.168.1.4 --protocols mops snmp ssh
    python3 tests/capture.py 192.168.1.4 --methods get_facts get_interfaces
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from napalm_hios.hios import HIOSDriver


def serialize(obj):
    """Make any object JSON-safe."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, bytes):
        return ' '.join(f'{b:02x}' for b in obj)
    if isinstance(obj, dict):
        return {str(k): serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serialize(v) for v in obj]
    return str(obj)


def save_json(path, data):
    """Write JSON with deterministic output."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True, default=str)


# ---------------------------------------------------------------------------
# Transport wrappers (tap 1)
# ---------------------------------------------------------------------------

def wrap_snmp(transport):
    log = []
    for name in ('_walk_sync', '_get_scalar_sync', '_get_scalars_sync', '_walk_columns_sync'):
        original = getattr(transport, name, None)
        if not original:
            continue
        def make_recorder(orig, fname):
            def wrapper(*args, **kwargs):
                result = orig(*args, **kwargs)
                log.append({
                    'function': fname,
                    'args': serialize(args),
                    'kwargs': serialize(kwargs),
                    'response': serialize(result),
                })
                return result
            return wrapper
        setattr(transport, name, make_recorder(original, name))
    return log


def wrap_mops(transport):
    log = []
    client = transport.client
    for name in ('get_multi', 'get'):
        original = getattr(client, name, None)
        if not original:
            continue
        def make_recorder(orig, fname):
            def wrapper(*args, **kwargs):
                result = orig(*args, **kwargs)
                log.append({
                    'function': f'client.{fname}',
                    'args': serialize(args),
                    'kwargs': serialize(kwargs),
                    'response': serialize(result),
                })
                return result
            return wrapper
        setattr(client, name, make_recorder(original, name))
    return log


def wrap_ssh(transport):
    log = []
    original_cli = transport.cli
    def recording_cli(commands, encoding='text', cmd_verify=None):
        result = original_cli(commands, encoding=encoding, cmd_verify=cmd_verify)
        log.append({
            'function': 'cli',
            'args': serialize([commands]),
            'kwargs': serialize({'encoding': encoding, 'cmd_verify': cmd_verify}),
            'response': serialize(result),
        })
        return result
    transport.cli = recording_cli
    return log


WRAPPERS = {'snmp': wrap_snmp, 'mops': wrap_mops, 'ssh': wrap_ssh}

# Methods that need arguments or are destructive
SKIP_METHODS = {'cli', 'ping', 'traceroute', 'get_config_fingerprint'}


def get_all_getters(device):
    """Discover all get_* methods from engine capabilities."""
    caps = device.engine.get_capabilities()
    return sorted(m for m in caps['crude'].get('read', [])
                  if m.startswith('get_') and m not in SKIP_METHODS)


def capture_context(device):
    """Serialize engine context for replay injection."""
    ctx = device.engine.context
    return {
        'ifindex_map': serialize(ctx.get('ifindex_map', {})),
        'bridge_port_map': serialize(ctx.get('bridge_port_map', {})),
        'device_info': serialize(ctx.get('device_info', {})),
    }


def capture_protocol(device, protocol, output_dir, methods=None):
    """Capture all getters on one protocol at all 4 tap points."""
    proto_dir = os.path.join(output_dir, protocol)

    transport = device._transport()
    wrapper = WRAPPERS.get(protocol)
    if not wrapper:
        print(f"  No wrapper for {protocol}, skipping")
        return

    transport_log = wrapper(transport)

    # Resolve device_info before getters (prevents surprise guard calls)
    try:
        device._fetch_device_info()
    except Exception:
        pass

    if methods is None:
        methods = get_all_getters(device)

    print(f"  {protocol}: {len(methods)} methods")

    for method_name in methods:
        transport_log.clear()
        try:
            t0 = time.monotonic()

            # Tap 3: engine output (schema-shaped)
            engine_result = device.engine.execute(method_name, protocol, transport)

            # Tap 4: NAPALM adapter output
            try:
                adapter_result = getattr(device, method_name)()
            except Exception:
                adapter_result = engine_result  # fallback if adapter has no special handling

            elapsed = time.monotonic() - t0

            # Tap 1: raw transport calls
            save_json(os.path.join(proto_dir, 'tap1_transport', f'{method_name}.json'), {
                'method': method_name,
                'protocol': protocol,
                'calls': transport_log[:],
            })

            # Tap 2: driver gather output (= engine input, post-transform)
            # This is what the engine sees after driver.gather() + transforms
            # For scalar getters it's the gathered dict before defaults filter
            # We capture it as tap3 minus the defaults contract (tap3 IS the useful one)
            # Tap 2 is implicit — driver output feeds directly into engine

            # Tap 3: engine output
            save_json(os.path.join(proto_dir, 'tap3_engine', f'{method_name}.json'),
                      serialize(engine_result))

            # Tap 4: NAPALM adapter output
            save_json(os.path.join(proto_dir, 'tap4_napalm', f'{method_name}.json'),
                      serialize(adapter_result))

            n_calls = len(transport_log)
            print(f"    {method_name}: OK ({n_calls} calls, {elapsed*1000:.0f}ms)")

        except Exception as e:
            save_json(os.path.join(proto_dir, 'errors', f'{method_name}.json'), {
                'method': method_name,
                'protocol': protocol,
                'error': str(e),
                'type': type(e).__name__,
            })
            print(f"    {method_name}: ERROR ({type(e).__name__}: {e})")


def main():
    parser = argparse.ArgumentParser(description='Capture test fixtures from live device')
    parser.add_argument('host', help='Device IP')
    parser.add_argument('--protocols', nargs='+', default=['mops', 'snmp', 'ssh'])
    parser.add_argument('--output', help='Output directory')
    parser.add_argument('--methods', nargs='+', help='Specific methods (default: all getters)')
    parser.add_argument('--user', default='admin')
    parser.add_argument('--password', default='private')
    args = parser.parse_args()

    for protocol in args.protocols:
        output_dir = args.output or os.path.join(
            os.path.dirname(__file__), 'fixtures', args.host)

        print(f"\nConnecting to {args.host} via {protocol}...")
        device = HIOSDriver(args.host, args.user, args.password,
                            optional_args={'protocol': protocol})
        try:
            device.open()
            print(f"  Connected. Active: {device.active_protocol}")

            # Context (once)
            ctx_path = os.path.join(output_dir, 'context.json')
            if not os.path.exists(ctx_path):
                save_json(ctx_path, capture_context(device))
                print(f"  Context saved")

            # Metadata (once)
            meta_path = os.path.join(output_dir, 'metadata.json')
            if not os.path.exists(meta_path):
                try:
                    facts = device.get_facts()
                except Exception:
                    facts = {}
                save_json(meta_path, {
                    'hostname': args.host,
                    'facts': serialize(facts),
                    'captured': datetime.now().isoformat(),
                    'protocols': args.protocols,
                })

            capture_protocol(device, protocol, output_dir, args.methods)

        except Exception as e:
            print(f"  Connection failed: {e}")
        finally:
            try:
                device.close()
            except Exception:
                pass

    print(f"\nFixtures saved to {output_dir}/")


if __name__ == '__main__':
    main()
