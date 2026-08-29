"""Drain pending tasks on a private asyncio loop, then close it.

SNMPHIOS owns a private loop via asyncio.new_event_loop(). pysnmp can
leave a timeout Task on it. loop.close() without a drain prints
"Task was destroyed but it is pending!" and the next protocol in the
same process pays GC of that task. YAML does not declare this; it is
loop lifetime, not a protocol budget.
"""
from __future__ import annotations

import asyncio


def drain_and_close(loop) -> None:
    """Cancel pending tasks on loop, then close. No-op if loop is gone.

    Must pass loop= to all_tasks. Bare all_tasks() raises RuntimeError
    when close() is not running inside that loop.
    """
    if loop is None or loop.is_closed():
        return
    pending = asyncio.all_tasks(loop=loop)
    if pending:
        for task in pending:
            task.cancel()
        loop.run_until_complete(
            asyncio.gather(*pending, return_exceptions=True)
        )
    loop.close()
