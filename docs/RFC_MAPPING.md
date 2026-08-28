# RFC Syntax → Transform Mapping

> Reference only. Source of truth is `crude_matrix.yaml` + `crude.py` in `crude_engine/engine/`.

Maps MIB SYNTAX types to the transform function used by the CRUDE_MATRIX.

## Boolean

| Syntax | Transform |
|--------|-----------|
| TruthValue | to_bool |
| HmEnabledStatus | to_bool |
| EnabledStatus | to_bool |

## Network

| Syntax | Transform |
|--------|-----------|
| MacAddress | crude_octet |
| PhysAddress | crude_octet |
| IpAddress | crude_address |
| InetAddressIPv4 | crude_address |
| InetAddressIPv6 | crude_address |
| InetAddress | crude_address |
| TAddress | crude_taddress |

## Temporal

| Syntax | Transform |
|--------|-----------|
| DateAndTime | crude_timestamp |
| HmTimeSeconds1970 | crude_timestamp |
| TimeTicks | crude_numeric |

## Numeric

| Syntax | Transform |
|--------|-----------|
| Counter32 | crude_numeric |
| Counter64 | crude_numeric |
| Gauge32 | crude_numeric |
| Integer32 | crude_numeric |
| Unsigned32 | crude_numeric |
| RowStatus | crude_numeric |
| INTEGER | crude_numeric |
| InetAddressPrefixLength | crude_numeric |
| InetAddressType | crude_numeric |
| InetPortNumber | crude_numeric |
| VlanIndex | crude_numeric |
| VlanIdOrNone | crude_numeric |
| InterfaceIndex | to_port_name |
| InterfaceIndexOrZero | to_port_name |
| Percent | crude_numeric |

## String

| Syntax | Transform |
|--------|-----------|
| DisplayString | crude_text |
| SnmpAdminString | crude_text |
| HmLargeDisplayString | crude_text |
| OCTET STRING | crude_octet |
| OBJECT IDENTIFIER | crude_text |

## Bitmask

| Syntax | Transform |
|--------|-----------|
| PortList | hex_portlist |
| BITS | crude_bits |
| Hm2SshEncryptionAlgorithms | crude_bits |
| Hm2SshHostKeyAlgorithms | crude_bits |
| Hm2SshKexAlgorithms | crude_bits |
| Hm2SshHmacAlgorithms | crude_bits |
| Hm2TlsVersions | crude_bits |
| Hm2TlsCipherSuites | crude_bits |

## Enum

| Syntax | Transform |
|--------|-----------|
| INTEGER_ENUM | crude_enum |
| HmSntpClientServerStatus | crude_enum |
