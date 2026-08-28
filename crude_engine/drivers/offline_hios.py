"""
offline_hios.py — Offline transport for napalm-hios.

Layer: Transport. Loads config XML files via MOPS interface.
Inherits MOPSHIOS — offline uses the same driver/engine path as MOPS.
Cannot: interpret data meaning, decide what to gather, know about features.
"""

import logging
from typing import Dict, List, Any

from crude_engine.drivers.mops_transport import MOPSHIOS
from crude_engine.drivers.offline_client import OfflineClient

logger = logging.getLogger(__name__)

class OfflineHIOS(MOPSHIOS):
    """Offline transport for HiOS. Inherits MOPS logic but uses file storage."""

    def __init__(self, hostname, username, password, timeout):
        # In offline mode, 'hostname' is the path to the XML data file
        super().__init__(hostname, username, password, timeout)
        self.client = OfflineClient(hostname)

    def open(self):
        """Load data from file."""
        self.client.open()

    def close(self):
        self.client.close()

    def is_alive(self) -> bool:
        return True
