"""python -m sidecar — thin HTTP over tests/release_matrix.py --inspect."""
from __future__ import annotations

import argparse
import os
import sys


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="python -m sidecar",
        description=(
            "POST /v1/run {name} maps catalog *.read to "
            "tests/release_matrix.py --inspect --method <getter>. "
            "Default mode is read-only."
        ),
    )
    p.add_argument("--host", default=os.environ.get("CRUDE_SIDECAR_HOST", "127.0.0.1"))
    p.add_argument("--port", type=int, default=int(os.environ.get("CRUDE_SIDECAR_PORT", "8765")))
    args = p.parse_args(argv)
    from sidecar.app import make_server, mode

    print(
        f"sidecar mode={mode()!r} POST /v1/run on {args.host}:{args.port} "
        f"inspect=tests/release_matrix.py::run_inspect",
        file=sys.stderr,
    )
    httpd = make_server(args.host, args.port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
