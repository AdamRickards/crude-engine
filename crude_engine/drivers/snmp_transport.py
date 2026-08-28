"""
snmp_transport.py — SNMP transport for napalm-hios.

Layer: Transport. Owns session, auth, and raw OID GET/SET/WALK.
Cannot: interpret data meaning, decide what to gather, know about features.
Talks to: device (pysnmp). Called by: SNMP driver (SNMP.py).
"""

import asyncio
import logging
from typing import Dict, List, Tuple, Any

from pysnmp.hlapi.asyncio import (
    SnmpEngine, CommunityData, UsmUserData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity,
    usmHMACMD5AuthProtocol, usmDESPrivProtocol,
)
# pysnmp 5.x uses camelCase, 7.x uses snake_case
try:
    from pysnmp.hlapi.asyncio import get_cmd, set_cmd, bulk_cmd
except ImportError:
    from pysnmp.hlapi.asyncio import getCmd as get_cmd, setCmd as set_cmd, bulkCmd as bulk_cmd
try:
    from pysnmp.entity.config import USM_KEY_TYPE_MASTER
except ImportError:
    from pysnmp.entity.config import usmKeyTypeMaster as USM_KEY_TYPE_MASTER
try:
    from pysnmp.proto.secmod.rfc3414.localkey import hash_passphrase_md5
except ImportError:
    from pysnmp.proto.secmod.rfc3414.localkey import hashPassphraseMD5 as hash_passphrase_md5
from pysnmp.proto.rfc1902 import Integer32, Unsigned32, OctetString, IpAddress
from napalm.base.exceptions import ConnectionException

logger = logging.getLogger(__name__)

class SNMPHIOS:
    """SNMPv2c/v3 transport for HiOS."""

    def __init__(self, hostname, username, password, timeout, port=161):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout
        self.port = port
        self._auth_cached = None
        self._loop = None
        self._engine = None
        self._transport = None

    def _build_auth(self):
        """Return SNMPv3 USM or SNMPv2c Community auth object."""
        if self._auth_cached:
            return self._auth_cached

        if not self.password:
            self._auth_cached = CommunityData(self.username or 'public', mpModel=1) # v2c
        else:
            # v2.9: Short-password workaround
            master_key = hash_passphrase_md5(self.password.encode())
            self._auth_cached = UsmUserData(
                self.username,
                authKey=master_key,
                privKey=master_key,
                authProtocol=usmHMACMD5AuthProtocol,
                privProtocol=usmDESPrivProtocol,
                authKeyType=USM_KEY_TYPE_MASTER,
                privKeyType=USM_KEY_TYPE_MASTER
            )
        return self._auth_cached

    def _ensure_loop(self):
        """Create persistent event loop if needed."""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
        return self._loop

    async def _ensure_session(self):
        """Create or reuse SnmpEngine + UdpTransportTarget."""
        if self._engine is None:
            self._engine = SnmpEngine()
        if self._transport is None:
            if hasattr(UdpTransportTarget, 'create'):
                self._transport = await UdpTransportTarget.create(
                    (self.hostname, self.port), timeout=self.timeout, retries=1
                )
            else:
                self._transport = UdpTransportTarget(
                    (self.hostname, self.port), timeout=self.timeout, retries=1
                )
        return self._engine, self._transport

    def _run(self, coro):
        """Run async coroutine on persistent event loop."""
        loop = self._ensure_loop()
        return loop.run_until_complete(coro)

    def open(self):
        """Verify connectivity."""
        try:
            self._get_scalar_sync('1.3.6.1.2.1.1.3.0') # sysUpTime
        except Exception as e:
            raise ConnectionException(f"SNMP connection failed: {str(e)}")

    def close(self):
        """Clean up SNMP session and event loop."""
        self._engine = None
        self._transport = None
        if self._loop and not self._loop.is_closed():
            self._loop.close()
            self._loop = None

    def is_factory_default(self) -> bool:
        return False

    # --- Execute methods (advisory lock pattern) ---

    _ACTION_KEY_OID = '1.3.6.1.4.1.248.11.21.1.2.18.0'
    _ACTION_OIDS = {
        'save_config':    '1.3.6.1.4.1.248.11.21.1.2.1.1.5.2.10.10.2',
        'clear_config':   '1.3.6.1.4.1.248.11.21.1.2.1.1.5.3.10.10.10',
        'clear_factory':  '1.3.6.1.4.1.248.11.21.1.2.1.1.5.3.10.2.2',
    }

    def _execute_action(self, action):
        """Read advisory lock key, write to action OID."""
        key = self._get_scalar_sync(self._ACTION_KEY_OID)
        oid = self._ACTION_OIDS[action]
        self._set_oids_sync((oid, int(key)))

    def save_config(self, dest='nvm'):
        self._execute_action('save_config')

    def clear_config(self, keep_ip=False):
        self._execute_action('clear_config')

    def clear_factory(self, erase_all=False):
        self._execute_action('clear_factory')

    # --- Wire normalization ---

    @staticmethod
    def _normalize(val):
        """Normalize pysnmp value to finite wire output types.

        V2.5 transport normalization: three paths.
        - Integer types → str of integer (e.g. '128')
        - ObjectIdentifier → dotted string (e.g. '1.3.6.1.2.1.26.4.16')
        - Everything else (OctetString, IpAddress, DisplayString) → hex-spaced bytes
          (e.g. 'c0 a8 01 04', '42 52 53 35 30')

        This makes SNMP wire output identical to MOPS: all non-integer data
        arrives as hex-spaced bytes. Transforms (to_ip, to_hex_decode, etc.)
        handle the decode uniformly across protocols.
        """
        if not hasattr(val, 'prettyPrint'):
            return val

        type_name = type(val).__name__

        # SNMP error values → None (driver skips these)
        if 'NoSuch' in type_name or 'EndOfMib' in type_name:
            return None

        # Integer types (Integer32, Counter32, Gauge32, TimeTicks, Counter64)
        if type_name in ('Integer', 'Integer32', 'Counter32', 'Counter64',
                         'Gauge32', 'TimeTicks', 'Unsigned32'):
            return str(int(val))

        # ObjectIdentifier → dotted string (not bytes — OIDs are structural, not content)
        if type_name == 'ObjectIdentifier':
            return val.prettyPrint()

        # Everything else → hex-spaced bytes (same format as MOPS)
        raw = bytes(val)
        if not raw:
            return ""
        return ' '.join(f'{b:02x}' for b in raw)

    # --- Synchronous Wrappers for Engine ---

    def _get_scalar_sync(self, oid: str) -> Any:
        results = self._run(self._get_scalar(oid))
        val = results.get(oid)
        return self._normalize(val)

    def _get_scalars_sync(self, *oids: str) -> Dict[str, Any]:
        """Batch scalar GET (sync). Returns {oid: normalized_value} dict."""
        raw = self._run(self._get_scalar(*oids))
        return {k: self._normalize(v) for k, v in raw.items()}

    @staticmethod
    def _encode(val):
        """Wrap Python value into pysnmp type for SET.

        Transport container wrapping — the reverse of _normalize().
        Crude functions return wire-ready Python values, transport wraps
        them into protocol containers.
        """
        if isinstance(val, (Integer32, Unsigned32, OctetString, IpAddress)):
            return val  # already a pysnmp type (from legacy SET tags)
        if isinstance(val, bool):
            return Integer32(int(val))
        if isinstance(val, int):
            if val < 0 or val <= 2147483647:
                return Integer32(val)
            return Unsigned32(val)
        if isinstance(val, (bytes, bytearray)):
            return OctetString(val)
        if isinstance(val, str):
            # Detect numeric strings from crude_numeric(set) → "128", "-1"
            # These must become Integer32/Unsigned32, not OctetString
            if val.lstrip('-').isdigit() and val:
                n = int(val)
                if n < 0 or n <= 2147483647:
                    return Integer32(n)
                return Unsigned32(n)
            # Detect hex-spaced format from crude_* SET (e.g. '0a 58 58 58')
            # This is the reverse of _normalize() which produces hex-spaced
            parts = val.split()
            if parts and all(len(p) == 2 for p in parts):
                try:
                    return OctetString(bytes.fromhex(''.join(parts)))
                except ValueError:
                    pass
            return OctetString(val.encode('utf-8'))
        return Integer32(int(val))

    def _set_oids_sync(self, *oid_value_pairs: Tuple[str, Any]):
        if not oid_value_pairs: return
        encoded = [(oid, self._encode(val)) for oid, val in oid_value_pairs]
        self._run(self._set_oids(*encoded))

    def _walk_sync(self, oid: str) -> Dict[str, Any]:
        data = self._run(self._walk(oid))
        return {idx: self._normalize(val) for idx, val in data.items()}

    def _walk_columns_sync(self, oid_map: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        raw = self._run(self._walk_columns(oid_map))
        return {idx: {col: self._normalize(v) for col, v in cols.items()}
                for idx, cols in raw.items()}

    # --- Async Primitives ---

    async def _get_scalar(self, *oids: str) -> Dict[str, Any]:
        engine, transport = await self._ensure_session()
        auth = self._build_auth()

        objs = []
        norm_oids = []
        for oid in oids:
            if oid.count('.') < 12 and not oid.endswith('.0'): oid += '.0'
            norm_oids.append(oid)
            objs.append(ObjectType(ObjectIdentity(oid)))

        err_ind, err_stat, err_idx, var_binds = await get_cmd(engine, auth, transport, ContextData(), *objs)
        if not err_ind and not err_stat:
            return {str(v[0]): v[1] for v in var_binds}
        # Batch failed — fall back to individual gets
        results = {}
        for oid in norm_oids:
            try:
                ei, es, _, vb = await get_cmd(engine, auth, transport, ContextData(), ObjectType(ObjectIdentity(oid)))
                if not ei and not es and vb:
                    results[str(vb[0][0])] = vb[0][1]
            except Exception as e:
                logger.warning("SNMP GET fallback failed for %s: %s", oid, e)
        return results

    async def _set_oids(self, *oid_value_pairs: Tuple[str, Any]):
        engine, transport = await self._ensure_session()
        auth = self._build_auth()

        objs = [ObjectType(ObjectIdentity(oid), val) for oid, val in oid_value_pairs]
        err_ind, err_stat, err_idx, var_binds = await set_cmd(engine, auth, transport, ContextData(), *objs)
        if err_ind: raise ConnectionException(f"SNMP SET error: {err_ind}")
        if err_stat: raise ConnectionException(f"SNMP SET error: {err_stat.prettyPrint()} at {err_idx}")

    async def _walk(self, base_oid: str) -> Dict[str, Any]:
        engine, transport = await self._ensure_session()
        auth = self._build_auth()

        results = {}
        start_oid = base_oid
        while True:
            err_ind, err_stat, err_idx, var_binds = await bulk_cmd(
                engine, auth, transport, ContextData(), 0, 50,
                ObjectType(ObjectIdentity(start_oid)),
                lexicographicMode=False
            )
            if err_ind or err_stat:
                break
            if not var_binds:
                break
            last_oid = None
            for row in var_binds:
                var_bind = row[0] if isinstance(row, list) else row
                oid_str = str(var_bind[0])
                if not oid_str.startswith(base_oid):
                    return results
                suffix = oid_str[len(base_oid):].lstrip('.')
                results[suffix] = var_bind[1]
                last_oid = oid_str
            if last_oid is None or last_oid == start_oid:
                break
            start_oid = last_oid
        return results

    async def _walk_columns(self, oid_map: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        results = {}
        for name, base_oid in oid_map.items():
            column_data = await self._walk(base_oid)
            for idx, val in column_data.items():
                if idx not in results: results[idx] = {}
                results[idx][name] = val
        return results
