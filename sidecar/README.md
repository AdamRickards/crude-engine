# Sidecar (read-only named tests)

Thin HTTP over the existing harness. Not a second test suite.

    POST /v1/run  {"name": "get_dns.read"}

maps to

    python3 tests/release_matrix.py --inspect --method get_dns --device <pool ip>

Same Python function: `tests/release_matrix.py::run_inspect`.
Documented in `tests/README_TESTS.md` (use `--inspect`, never throwaway
`get_*` scripts). `--inspect` is read-only by design.

## Name → CLI

| catalog name | call |
| `get_dns.read` | `--inspect --method get_dns --kind read` |
| `set_dns.roundtrip` | HTTP 400 `bad_name` (not called) |
| `dns.lifecycle.mops` | HTTP 400 `bad_name` (not called) |
| `save_config.execute` | HTTP 400 `bad_name` (not called) |
| unknown well-formed | HTTP 404 `unknown_name` |

Device IP comes from the sidecar machine's gitignored
`tests/device_pool.yaml`. Never from the request body. Never from git.
Example pool host is TEST-NET `192.0.2.10` in
`tests/device_pool.yaml.example`. Passwords from the environment
(`CRUDE_DEVICE_PASSWORD`).

Sync: iterate tests on a PC, merge to GitHub, sidecar machine git pull.

## Run

From the crude-engine root:

    python3 -m sidecar --help
    python3 -m sidecar --host 127.0.0.1 --port 8765

Default `CRUDE_SIDECAR_MODE=read-only`. Default transport is `fake`
(mocked inspect, no switch). Operator LAN: set `CRUDE_SIDECAR_TRANSPORT`
to `live` and keep the pool file local.

Bind loopback. Bot VM must not WireGuard and must not SSH switches.

Put `SIDECAR_URL` in a gitignored `.env` on the operator machine.
`servers.url` in `openapi.yaml` stays `/`.

## Offline proofs

    python3 tests/test_sidecar_readonly.py
