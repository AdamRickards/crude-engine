# Wire YAML Specification

> Generated from device MIBs. Never hand-edited. The raw truth layer.

## Generation & Location

Wire YAMLs are **machine-generated** from MIB XML + MOPS webUI proxy captures. They are NOT committed to git — they're regenerated per firmware version.

| Artifact | Path | Notes |
|----------|------|-------|
| Generated wire YAMLs | `local/reference/webUI/*.yaml` | 134 files, 4,058 attributes. Not in git |
| Active wire YAMLs | `crude_engine/wire/*.yaml` | Copied from reference after validation |
| Generator | `local/generator/batch_generate_webui.py` | Reads MIB XML + proxy captures |
| Overrides | `local/generator/overrides.yaml` | Manual corrections (create_method, type) |
| MIB source | `local/reference/MIBs/` | 66 firmware MIB files |
| MIB schema | `local/reference/MOPS/mops_hios.xml` | MOPS MIB tree for OID/table resolution |
| Master schema doc | `docs/napalm-hios-2-6-schema.md` | 4,058 attribute reference (1.3M) |

## The Three-File Model

| Layer | Responsibility | Generation | Path |
|---|---|---|---|
| **Wire** | Raw OIDs, MIB fields, and Syntax | **Automated** (generator) | `crude_engine/wire/*.yaml` |
| **Schema** | Functional grouping, mapping to Wire | **Authored** (human intent) | `crude_engine/schemas/*.yaml` |
| **Adapter** | Consumer-specific shaping | **Authored** (API contract) | Per-consumer package (e.g. napalm-hios, gNMI) |

---

## 3. Wire YAML Specification (`wire/*.yaml`)

Wire files are the "Pure Truth" layer. They describe what the switch speaks on the wire.

### 3.1 Metadata
```yaml
version: 2.6.0
feature: systemInformation
```

### 3.2 Schemas (The Promise)
Defines the raw output structure of a Wire read.
```yaml
schemas:
  read_systemInformation:
    type: dict
    defaults:
      sysname: ""
      syscontact: ""
```

### 3.3 Attributes (The Source)
Each attribute maps a Wire field to its physical sources.

#### Terminology
*   **`read:`**: Replaces legacy `get:`. Defines the path for data retrieval.
*   **`write:`**: Replaces legacy `set:`. Defines the path for data mutation.

#### Access-Driven Destiny (Minimalism)
The `access:` tag dictates the requirement for a `write:` block:
*   **`access: r`**: Read-only. Only `read:` block allowed.
*   **`access: ru`**: Read-Write. The engine **implicitly** uses the `read:` path for writes. **Minimalist Rule**: Do not define a `write:` block if the path is identical to `read:`.
*   **`access: crud`**: Create-Read-Update-Delete. Implicitly maps `read:` to all mutation operations.

#### Example Attribute
```yaml
  syscontact:
    syntax: DisplayString
    type: string
    access: ru
    sources:
      snmp:
        read:
          oid: 1.3.6.1.2.1.1.4
      mops:
        read:
          mib: SNMPv2-MIB
          table: system
          field: sysContact
```

---

## 4. Schema YAML Specification (`schemas/*.yaml`)

Schema files are the "Switchboard". They map stable human names to unstable Wire names.

### 4.1 Mapping Strategy
A Schema attribute points to a Wire attribute. If the Wire attribute changes (e.g., a firmware update changes an OID), only the **Wire YAML** needs regeneration; the **Schema YAML** remains stable.

```yaml
# schemas/system.yaml
attributes:
  contact_person:
    wire: syscontact
    source: systemInformation
```

---

## 5. Data Lineage (The "How")

1.  **UI Proxy Capture**: User clicks through the Web UI. All XML traffic is saved to `/captured`.
2.  **MIB Resolution**: `batch_generate_webui.py` reads the XML, identifies attributes, and walks the MIB tree in `mops_schema.xml` to find OIDs and Tables.
3.  **Schema Enrichment**: `enrich_schema_v26.py` extracts high-fidelity syntax (e.g., `Integer32 (0..7)`) and access rules directly from the MIB XML.
4.  **Wire Generation**: The final v2.6 Wire YAML is produced, 100% compliant and ready for the `interpreter.py` engine.

---

## 6. Testing & Validation
*   **Compliance**: `cross_validate_v26.py` ensures all 134 Wire YAMLs match the Master Schema and follow the Minimalism/Terminology rules.
*   **Round-trip**: The `access: ru` flag enables automated testing of write operations by using the `read:` path as the validation baseline.
