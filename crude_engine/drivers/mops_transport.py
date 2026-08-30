"""
mops_transport.py — MOPS transport for crude-engine.

Layer: Transport. Owns HTTPS session and raw MIB operations via XML.
Cannot: interpret data meaning, decide what to gather, know about features.
Talks to: device (mops_client.py). Called by: MOPS driver (MOPS.py).
"""

import logging
from typing import Dict, List, Any, Optional

from napalm.base.exceptions import ConnectionException
from crude_engine.drivers.mops_client import MOPSClient, MOPSError

logger = logging.getLogger(__name__)

class MOPSHIOS:
    """MOPS (MIB Operations over HTTPS) transport for HiOS."""

    def __init__(self, hostname, username, password, timeout, port=443):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout
        self.port = port
        self.client = MOPSClient(hostname, username, password, port=port, timeout=timeout)
        
        self._staging_mode = False
        self._staged_mutations = [] # List of (mib, node, values, index)

    def open(self):
        """Verify connectivity."""
        try:
            self.client.get('SNMPv2-MIB', 'system', attributes=['sysUpTime'])
        except Exception as e:
            raise ConnectionException(f"MOPS connection failed: {str(e)}")

    def close(self):
        self.client.close()

    def is_alive(self) -> bool:
        return self.client.is_alive()

    def is_factory_default(self) -> bool:
        return self.client.is_factory_default()

    # --- Synchronous Engine Primitives ---

    def _get_path(self, path: str, attributes: List[str],
                  decode_strings: bool = False) -> List[Dict[str, Any]]:
        """Fetch a MIB node path (e.g. 'SNMPv2-MIB/system')."""
        if '/' not in path:
            return []
        mib, node = path.split('/', 1)
        try:
            return self.client.get(mib, node, attributes=attributes,
                                   decode_strings=decode_strings)
        except MOPSError:
            return []

    def _walk_columns(self, mib: str, table: str, attributes: List[str],
                       decode_strings: bool = True) -> List[Dict[str, Any]]:
        """Fetch all rows for given columns in a MIB table."""
        try:
            return self.client.get(mib, table, attributes=attributes,
                                   decode_strings=decode_strings)
        except MOPSError:
            return []

    def _get_with_ifindex(self, *queries: List, decode_strings=False):
        """Atomic multi-table fetch with interface name mapping.
        
        Each query is a list: [mib, table, attrs]
        Returns (mibs_dict, ifindex_map).
        """
        all_queries = list(queries)
        
        # v2.9: Only append ifXEntry if not already being fetched
        has_ifx = any(q[1] == 'ifXEntry' for q in all_queries if isinstance(q, (list, tuple)) and len(q) > 1)
        if not has_ifx:
            all_queries.append(['IF-MIB', 'ifXEntry', ['ifName']])
        
        try:
            mibs = self.client.get_multi(all_queries, decode_strings=decode_strings)
            # Build ifindex map
            ifmap = {}
            ifX = mibs.get('IF-MIB', {}).get('ifXEntry', [])
            for entry in ifX:
                idx = entry.get('ifIndex')
                name = entry.get('ifName')
                if idx and name: ifmap[str(idx)] = name
            return mibs, ifmap
        except MOPSError as e:
            logger.error(f"MOPS multi-get failed: {e}")
            return {}, {}

    # --- Mutators and Staging ---

    def start_staging(self):
        self._staging_mode = True
        self._staged_mutations = []

    def commit_staging(self):
        if not self._staged_mutations:
            self._staging_mode = False
            return
        
        try:
            self._apply_mutations(self._staged_mutations)
        finally:
            self._staged_mutations = []
            self._staging_mode = False

    def discard_staging(self):
        self._staged_mutations = []
        self._staging_mode = False

    def get_staged_mutations(self) -> List:
        return self._staged_mutations

    def _apply_set(self, mib: str, node: str, values: Dict[str, Any], index: Optional[Dict] = None):
        """Queue or execute a MIB set operation."""
        mutation = (mib, node, values, index)
        if self._staging_mode:
            self._staged_mutations.append(mutation)
        else:
            self._apply_mutations([mutation])

    def _apply_mutations(self, mutations: List):
        """Execute one or more mutations in a single atomic POST if possible."""
        try:
            self.client.set_multi(mutations)
        except MOPSError as e:
            raise ConnectionException(f"MOPS set failed: {e}")

    def save_config(self, dest: str = "nvm"):
        """Save running config to NVM/ENVM."""
        return self.client.save_config(dest=dest)

    def onboard(self, new_password: str) -> bool:
        """Onboard a factory-fresh device by changing default password."""
        return self.client.change_password(new_password)

    def clear_config(self, keep_ip: bool = False):
        """Clear running config via MOPS."""
        return self.client.clear_config(keep_ip=keep_ip)

    def clear_factory(self, erase_all: bool = False):
        """Factory reset via MOPS."""
        return self.client.clear_factory(erase_all=erase_all)

    def load_config(self, xml_data: str, profile: str = None, destination: str = 'nvm'):
        """Upload config XML to a profile."""
        return self.client.upload_config(xml_data, profile, destination=destination)
