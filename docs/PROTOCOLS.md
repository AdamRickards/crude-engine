# Protocol Reference

Auto-generated from `transport_registry.py` + protocol YAMLs. Per-attribute wire sources are in [API_REFERENCE.md](API_REFERENCE.md).

## Connection

**Default order:** MOPS > SNMP > SSH

```python
# Use default order (MOPS > SNMP > SSH)
device = driver("192.168.1.4", "admin", "private")

# Force specific protocol
device = driver("192.168.1.4", "admin", "private",
                optional_args={"protocol": "snmp"})

# Offline (config XML file)
device = driver("config.xml", "", "")
```

| Protocol | Transport | Port | Port Override |
| :--- | :--- | :--- | :--- |
| **MOPS** | HTTPS | 443 | `mops_port` |
| **SNMP** | UDP/SNMPv3 | 161 | `snmp_port` |
| **SSH** | TCP/SSH | 22 | `ssh_port` |
| **OFFLINE** | XML file | — | — |

---

## MOPS

Protocol YAML: `drivers/MOPS.yaml`

**Index encodings:**
- `inet_address` → `field_dict`
- `implied_string` → `hex_string`
- `compound` → `field_dict`

**Create method:** `createAndWait`

**Execute methods (10):** `save_config()`, `load_config()`, `onboard()`, `clear_config()`, `clear_factory()`, `start_staging()`, `commit_staging()`, `discard_staging()`, `get_staged_mutations()`, `is_factory_default()`

**Configuration:**
- `decode_strings`: `False`

---

## SNMP

Protocol YAML: `drivers/SNMP.yaml`

**Index encodings:**
- `inet_address` → `oid_suffix`
- `implied_string` → `oid_suffix`
- `compound` → `oid_suffix`

**Create method:** `createAndWait`

**Execute methods (3):** `save_config()`, `clear_config()`, `clear_factory()`

**Configuration:**
- `method`: `walk`
- `scalar_suffix`: `.0`
- `unsigned_syntaxes`: `6 types`

---

## SSH

Protocol YAML: `drivers/SSH.yaml`

**Index encodings:**
- `inet_address` → `raw`
- `implied_string` → `raw`
- `compound` → `raw`

**Create method:** `createAndWait`

**Execute methods (7):** `save_config()`, `clear_config()`, `clear_factory()`, `onboard()`, `cli()`, `ping()`, `is_factory_default()`

**Configuration:**
- `parser`: `dot_keys`
- `cmd_verify`: `True`
- `column_overflow`: `flexible`
- `empty_table_sentinels`: `['No entry', 'No entries']`

---

## OFFLINE

Config XML file acts as a device. Uses MOPS engine protocol internally. Auto-detected when hostname ends with `.xml`.

---

## Wire Overlays

- **SSH**: `wire/ssh/` (13 overlay files)

---

## Coverage

| Protocol | Wire Attrs | Methods | Method % |
| :--- | :--- | :--- | :--- |
| MOPS | 7927 / 7927 | 174 / 174 | 100% |
| SNMP | 7927 / 7927 | 174 / 174 | 100% |
| SSH | 61 / 7927 | 53 / 174 | 30% |
