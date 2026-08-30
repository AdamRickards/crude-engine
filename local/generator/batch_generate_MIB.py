# Leftover v26/monolith one-shot. Not live law.
# Kept (not deleted) as archive. Do not write crude_engine/wire.
# Isolated temp emit only: python batch_generate_MIB.py --isolated --outdir /tmp/...
# Live generators: generate_docs.py, generate_method_ref.py, generate_protocols.py.
# Live schema check: validate_schemas.py. See local/generator/README.md.
#
# Version: 2.6.2 - AUGMENTS index, BITS TC unwrap, composite INDEX, SFlowReceiver
import os
import argparse
import xml.etree.ElementTree as ET
import json
import re
import yaml

# Historical monolith default (dead). Isolated --outdir retargets the RUN.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASE_DIR = '/home/adamr/obsidian-vault/Projects/napalm-hios-v2'
captured_dir = os.path.join(BASE_DIR, 'local/reference/captured')
xml_schema_path = os.path.join(_REPO_ROOT, 'local/reference/MOPS/mops_hios.xml')
master_schema_path = os.path.join(_REPO_ROOT, 'docs/napalm-hios-2-6-schema.md')
output_dir = os.path.join(BASE_DIR, 'local/reference/webUI')
overrides_path = os.path.join(_REPO_ROOT, 'local/generator/overrides.yaml')

def _refuse_live_wire(path):
    ap = os.path.abspath(path).replace("\\", "/")
    if "crude_engine/wire" in ap:
        raise SystemExit("leftover batch_generate_MIB refuses to write live crude_engine/wire")

def load_overrides():
    if not os.path.exists(overrides_path): return {}
    with open(overrides_path, "r") as f:
        return yaml.safe_load(f) or {}

def load_master_meta():
    meta_db = {}
    if not os.path.exists(master_schema_path): return {}
    with open(master_schema_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        if "|" in line and "::" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 5:
                full_field = parts[1].lower()
                meta = {
                    "syntax": parts[3],
                    "access": parts[4],
                    "constraints": parts[5] if len(parts) > 5 else "",
                    "oid": parts[2]
                }
                meta_db[full_field] = meta
    return meta_db

def parse_constraints(raw, syntax, mib_range=None):
    v = {}
    # Priority 1: real MIB <Range> from XML (most accurate)
    if mib_range:
        v = dict(mib_range)
    # Priority 2: master schema markdown constraints
    if not v and raw:
        rm = re.search(r"Range: (\d+)\.\.(\d+)", raw)
        if rm: v["min"] = int(rm.group(1)); v["max"] = int(rm.group(2))
        em = re.search(r"Enums: \[(.*)\]", raw)
        if em:
            pairs = em.group(1).split(", "); v["allowed"] = [p.split(":")[1] for p in pairs if ":" in p]
    # Priority 3: only emit validation for types with meaningful constraints
    # Skip generic Integer32/Unsigned32 full-range — it's noise
    if not v:
        s = str(syntax)
        if "VlanIndex" in s: v = {"min": 1, "max": 4094}
        elif "TruthValue" in s or "HmEnabledStatus" in s: v = {"allowed": [True, False]}
    return v

def syntax_to_type(syntax, enumerations=None, tc_info=None):
    s = str(syntax).strip()
    if any(x in s for x in ("TruthValue", "HmEnabledStatus", "EnabledStatus")): return "boolean"
    # INTEGER{enabled(1),disabled(2)} — same semantics as HmEnabledStatus, inline enum
    if enumerations:
        pairs = {(e.get("name"), str(e.get("value"))) for e in enumerations}
        if pairs == {("enabled", "1"), ("disabled", "2")}:
            return "boolean"
    if s == "INTEGER" or any(x in s for x in ("Counter", "Gauge", "Integer", "Unsigned", "RowStatus", "Index", "Percent", "TimeTicks", "Number", "StorageType", "TimeStamp", "TimeInterval", "TimeFilter", "InetAddressPrefixLength", "InetAddressType", "InetPortNumber", "InetVersion", "Timeout", "Metric", "VlanId", "RouterID", "AreaID", "LacpKey", "DesignatedRouterPriority", "SFlowReceiver")): return "integer"
    if any(x in s for x in ("BITS", "PortList")): return "list"
    # TextualConvention whose base syntax is BITS (LldpSystemCapabilitiesMap, …)
    if tc_info and tc_info.get("syntax") == "BITS":
        return "list"
    # Hm2* BITS types have bit_map in their MIB definition — handled by bit_map detection
    # Don't blanket-classify all Hm2* as list — many are integer enums
    return "string"

def get_default_for_type(stype):
    if stype == "integer": return 0
    if stype == "boolean": return False
    if stype == "list": return []
    return ""

def build_lookup_tables(root):
    obj_by_name = {}
    for obj in root.findall('.//ObjectType'):
        name = obj.get('name')
        if name: obj_by_name[name] = obj

    node_by_name = {}
    for node in root.findall('.//*'):
        if node.tag in ('ObjectIdentifier', 'ObjectType', 'ModuleIdentity'):
            name = node.get('name')
            if name:
                node_by_name[name] = {
                    'oid': node.get('OID', ''),
                    'parent': node.get('Parent', ''),
                    'tag': node.tag,
                    'node': node,
                }

    table_for_entry = {}
    for obj in root.findall('.//ObjectType'):
        syntax = obj.find('Syntax')
        if syntax is not None:
            entry_name = syntax.get('name', '')
            if entry_name:
                table_for_entry[entry_name] = {
                    'oid': obj.get('OID', ''),
                    'parent': obj.get('Parent', ''),
                    'name': obj.get('name', ''),
                }

    obj_to_mib = {}
    for mib in root.findall('MIB'):
        for definition in mib.findall('Definition'):
            def_name = definition.get('name', '')
            for child in definition:
                child_name = child.get('name', '')
                if child_name: obj_to_mib[child_name] = def_name

    index_fields = {}
    index_meta = {}  # entry_name → [{name, implied, syntax}]
    for obj in root.findall('.//ObjectType'):
        idx_node = obj.find('Index')
        if idx_node is not None:
            entry_name = obj.get('name', '')
            idx_names = [i.get('name', '') for i in idx_node.findall('Value')]
            if idx_names: index_fields[entry_name] = idx_names
            # Capture implied flag per index value
            idx_detail = []
            for iv in idx_node.findall('Value'):
                iv_name = iv.get('name', '')
                iv_implied = iv.get('implied', '').lower() == 'true'
                # Look up syntax of the index column
                iv_syntax = ''
                iv_obj = obj_by_name.get(iv_name)
                if iv_obj is not None:
                    iv_sn = iv_obj.find('Syntax')
                    if iv_sn is not None:
                        iv_syntax = iv_sn.get('name', '')
                idx_detail.append({'name': iv_name, 'implied': iv_implied, 'syntax': iv_syntax})
            if idx_detail:
                index_meta[entry_name] = idx_detail

    # AUGMENTS entries have no INDEX child — inherit from the augmented Entry
    # (ifXEntry augments ifEntry, dot1qPortVlanEntry augments dot1dBasePortEntry, …)
    for obj in root.findall('.//ObjectType'):
        aug = obj.get('augments')
        if not aug:
            continue
        entry_name = obj.get('name', '')
        if not entry_name:
            continue
        seen = set()
        cur = aug
        while cur and cur not in seen:
            seen.add(cur)
            if cur in index_fields:
                index_fields[entry_name] = list(index_fields[cur])
                if cur in index_meta:
                    index_meta[entry_name] = list(index_meta[cur])
                break
            cur_obj = obj_by_name.get(cur)
            cur = cur_obj.get('augments') if cur_obj is not None else None

    tc_by_name = {}
    for tc in root.findall('.//TextualConvention'):
        name = tc.get('name')
        syn = tc.find('Syntax')
        if not name or syn is None:
            continue
        info = {"syntax": syn.get("name", ""), "bit_map": {}}
        for enum in syn.findall('Enumeration'):
            try:
                info["bit_map"][int(enum.get("value"))] = enum.get("name")
            except (TypeError, ValueError):
                pass
        if not info["bit_map"]:
            info.pop("bit_map")
        tc_by_name[name] = info

    return obj_by_name, node_by_name, table_for_entry, obj_to_mib, index_fields, index_meta, tc_by_name

def resolve_meta(target_name, master_db, obj_by_name, node_by_name, table_for_entry, obj_to_mib, index_fields, index_meta, root, tc_by_name=None):
    tc_by_name = tc_by_name or {}
    found_meta = {"mib": "Unknown", "table": "Unknown", "oid": "N/A", "syntax": "Unknown", "access": "r", "constraints": "", "is_table": False, "index_field": ""}
    
    target_obj = obj_by_name.get(target_name)
    if target_obj is not None:
        found_meta["mib"] = obj_to_mib.get(target_name, "Unknown")
        parent_name = target_obj.get('Parent', '')
        found_meta["table"] = parent_name

        if parent_name and parent_name.endswith('Entry'):
            found_meta["is_table"] = True
            idx_cols = index_fields.get(parent_name, [])
            if idx_cols:
                found_meta["index_field"] = idx_cols[-1]
                if len(idx_cols) > 1:
                    found_meta["index_fields"] = idx_cols
            # Check if index needs hex decode for MOPS (implied string indices)
            idx_detail = index_meta.get(parent_name, [])
            if idx_detail:
                for d in idx_detail:
                    if d['implied'] or d['syntax'] in ('SnmpAdminString', 'OCTET STRING', 'SnmpEngineID'):
                        found_meta["key_decode"] = True
                        break
        elif parent_name and parent_name in node_by_name:
            pnode = node_by_name[parent_name]
            if pnode.get('tag') == 'ObjectType' and pnode['node'].find('Index') is not None:
                found_meta["is_table"] = True
                idx_cols = index_fields.get(parent_name, [])
                if idx_cols:
                    found_meta["index_field"] = idx_cols[-1]
                    if len(idx_cols) > 1:
                        found_meta["index_fields"] = idx_cols

        oid_parts = []
        curr_oid = target_obj.get('OID', '')
        p = parent_name
        
        if curr_oid.startswith("1.3.6.1"):
            full_oid = curr_oid
        else:
            oid_parts.append(curr_oid)
            seen = {target_name}
            while p and p not in seen:
                seen.add(p)
                info = node_by_name.get(p)
                if not info: info = table_for_entry.get(p)
                if info:
                    p_oid = info['oid']
                    if p_oid.startswith("1.3.6.1"):
                        oid_parts.insert(0, p_oid)
                        p = None
                    else:
                        oid_parts.insert(0, p_oid)
                        p = info['parent']
                else: break
            
            full_oid = ".".join(part for part in oid_parts if part)
            if full_oid.startswith("1.3.6.1"): pass
            elif full_oid.startswith("3.6.1"): full_oid = "1." + full_oid
            else:
                if found_meta["mib"].startswith("HM2"): full_oid = "1.3.6.1.4.1.248.11." + full_oid
                else: full_oid = "1.3.6.1.2.1." + full_oid
                
        if "1.3.6.1" in full_oid[1:]:
            parts = full_oid.split(".")
            root_indices = [i for i, x in enumerate(parts) if parts[i:i+4] == ["1", "3", "6", "1"]]
            if root_indices: full_oid = ".".join(parts[root_indices[-1]:])

        found_meta["oid"] = full_oid
        syntax_node = target_obj.find('Syntax')
        found_meta["syntax"] = syntax_node.get('name') if syntax_node is not None else "Unknown"
        # Extract real <Range> from MIB XML (e.g. <Range value="1" upperValue="4"/>)
        if syntax_node is not None:
            range_node = syntax_node.find('Range')
            if range_node is not None:
                rv = range_node.get('value', '')
                ruv = range_node.get('upperValue', '')
                if rv and ruv:
                    found_meta["mib_range"] = {"min": int(rv), "max": int(ruv)}
                elif rv:
                    # Fixed-size OCTET STRING: <Range value="8"/> (not useful for integer validation)
                    pass
        mib_access = target_obj.get('access', 'read-only').lower().replace(' ', '-')
        if "read-create" in mib_access or "read-write" in mib_access: found_meta["access"] = "ru"
        if found_meta["syntax"] == "RowStatus":
            found_meta["access"] = "crud"
            found_meta["create_method"] = "createAndWait"
            # Detect index_type from parent entry's INDEX declaration
            idx_detail = index_meta.get(parent_name, [])
            if idx_detail:
                syntaxes = [d['syntax'] for d in idx_detail]
                any_implied = any(d['implied'] for d in idx_detail)
                if 'InetAddressType' in syntaxes and 'InetAddress' in syntaxes:
                    found_meta["index_type"] = "inet_address"
                elif any_implied or any(s in ('SnmpAdminString', 'OCTET STRING', 'SnmpEngineID') for s in syntaxes):
                    found_meta["index_type"] = "implied_string"
                elif len(idx_detail) > 1:
                    # multi-field INDEX with mixed types (ip_source_guard 4-part, …)
                    found_meta["index_type"] = "composite"

    lookup_keys = []
    if found_meta["mib"] != "Unknown":
        lookup_keys.append(f"{found_meta['mib']}::{target_name}".lower())
    for k in master_db:
        if k.split("::")[-1] == target_name.lower():
            lookup_keys.append(k)
            break

    for key in lookup_keys:
        if key in master_db:
            meta = master_db[key]
            found_meta["syntax"] = meta["syntax"]
            found_meta["access"] = meta["access"]
            found_meta["constraints"] = meta["constraints"]
            if found_meta["oid"] == "N/A" or "1.3.6.1" not in str(found_meta["oid"]): found_meta["oid"] = meta["oid"]
            if found_meta["mib"] == "Unknown": found_meta["mib"] = key.split("::")[0]
            break

    if target_obj is not None:
        syntax_node = target_obj.find('Syntax')
        if syntax_node is not None:
            enums = list(syntax_node.findall('Enumeration'))
            if enums:
                found_meta["enumerations"] = enums

    if found_meta["syntax"] == "BITS" and target_obj is not None:
        bit_map = {}
        syntax_node = target_obj.find('Syntax')
        if syntax_node is not None:
            for enum in syntax_node.findall('Enumeration'):
                bit_map[int(enum.get('value'))] = enum.get('name')
        if bit_map: found_meta["bit_map"] = bit_map
    else:
        tc = tc_by_name.get(found_meta["syntax"])
        if tc and tc.get("syntax") == "BITS" and tc.get("bit_map"):
            found_meta["bit_map"] = tc["bit_map"]
            found_meta["tc"] = tc
        elif tc:
            found_meta["tc"] = tc

    return found_meta

def process_captured_pages():
    _refuse_live_wire(output_dir)
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    tree = ET.parse(xml_schema_path); root = tree.getroot()
    master_db = load_master_meta()
    overrides = load_overrides()
    obj_by_name, node_by_name, table_for_entry, obj_to_mib, index_fields, index_meta, tc_by_name = build_lookup_tables(root)

    mib_features = {}
    for name, obj in obj_by_name.items():
        mib = obj_to_mib.get(name, "Unknown")
        feature = mib.replace("HM2-", "").replace("-MIB", "").lower()
        if feature not in mib_features: mib_features[feature] = []
        mib_features[feature].append(name)

    count = 0
    all_mib_features = sorted(mib_features.keys())
    for mib_id in all_mib_features:
        attrs_found = {attr: True for attr in mib_features[mib_id]}
        feature_data = {"version": "2.6.0", "feature": mib_id, 
                        "schemas": {f"read_{mib_id}": {"type": "dict", "defaults": {}}}, "attributes": {}}
        for attr_name in sorted(attrs_found.keys()):
            meta = resolve_meta(attr_name, master_db, obj_by_name, node_by_name, table_for_entry, obj_to_mib, index_fields, index_meta, root, tc_by_name)
            if meta:
                access = meta['access'].strip(); syntax = meta['syntax'].strip()
                stype = syntax_to_type(syntax, enumerations=meta.get("enumerations"), tc_info=meta.get("tc"))
                validation = parse_constraints(meta['constraints'], syntax, meta.get('mib_range'))
                clean_name = attr_name.lower()
                feature_data["schemas"][f"read_{mib_id}"]["defaults"][clean_name] = get_default_for_type(stype)
                snmp_read = {"oid": meta['oid'], "method": "walk" if meta["is_table"] else "get"}
                mops_read = {"mib": meta['mib'], "table": meta['table'], "field": attr_name}
                if meta["is_table"] and meta["index_field"]:
                    mops_read["index_field"] = meta["index_field"]
                    if "index_fields" in meta:
                        mops_read["index_fields"] = meta["index_fields"]
                    if meta.get("key_decode"):
                        mops_read["key_tag"] = "to_hex_decode"
                attr_entry = {"syntax": syntax, "type": stype, "access": access, "sources": {"snmp": {"read": snmp_read}, "mops": {"read": mops_read}}}
                if validation: attr_entry["validation"] = validation
                if "bit_map" in meta:
                    attr_entry["bit_map"] = meta["bit_map"]
                    attr_entry["type"] = "list"  # BITS fields → list output
                if "create_method" in meta: attr_entry["create_method"] = meta["create_method"]
                if "index_type" in meta: attr_entry["index_type"] = meta["index_type"]
                # Apply overrides from overrides.yaml
                cm_override = overrides.get("create_method", {}).get(clean_name)
                if cm_override: attr_entry["create_method"] = cm_override
                type_override = overrides.get("type", {}).get(clean_name)
                if type_override: attr_entry["type"] = type_override
                src_ov = (overrides.get("sources") or {}).get(clean_name) or {}
                if src_ov.get("oid"):
                    attr_entry["sources"]["snmp"]["read"]["oid"] = src_ov["oid"]
                if src_ov.get("table"):
                    attr_entry["sources"]["mops"]["read"]["table"] = src_ov["table"]
                if src_ov.get("field"):
                    attr_entry["sources"]["mops"]["read"]["field"] = src_ov["field"]
                feature_data["attributes"][clean_name] = attr_entry
        with open(os.path.join(output_dir, f"{mib_id}.yaml"), 'w') as f:
            yaml.dump(feature_data, f, sort_keys=False, default_flow_style=False)
        count += 1
    # Always output context-sources.yaml — engine infrastructure
    # These are RFC standard MIB objects needed for ifindex_map and bridge_port_map
    context_data = {
        "version": "2.6.0",
        "feature": "context-sources",
        "description": "Standard MIB attributes for engine context building",
        "attributes": {
            "ifname": {
                "syntax": "DisplayString", "type": "string", "access": "r",
                "sources": {
                    "snmp": {"read": {"oid": "1.3.6.1.2.1.31.1.1.1.1", "method": "walk"}},
                    "mops": {"read": {"mib": "IF-MIB", "table": "ifXEntry", "field": "ifName"}}
                }
            },
            "dot1dbaseportifindex": {
                "syntax": "Integer32", "type": "integer", "access": "r",
                "sources": {
                    "snmp": {"read": {"oid": "1.3.6.1.2.1.17.1.4.1.2", "method": "walk"}},
                    "mops": {"read": {"mib": "BRIDGE-MIB", "table": "dot1dBasePortEntry",
                                       "field": "dot1dBasePortIfIndex"}}
                }
            }
        }
    }
    with open(os.path.join(output_dir, "context-sources.yaml"), 'w') as f:
        yaml.dump(context_data, f, sort_keys=False, default_flow_style=False)

    print(f"Generated {count} + 1 context-sources v2.6 Wire YAMLs using MIB-based naming.")

def _cli(argv=None):
    global xml_schema_path, overrides_path, master_schema_path, output_dir
    parser = argparse.ArgumentParser(
        description="Leftover MIB→wire generator. Not live law. Temp outdir only."
    )
    parser.add_argument("--isolated", action="store_true",
                        help="Required. Leftover is dead as live law; isolated temp emit only.")
    parser.add_argument("--outdir", required=True,
                        help="TEMP directory for YAML emit. Never crude_engine/wire.")
    parser.add_argument("--xml", default=xml_schema_path,
                        help="mops_hios.xml path (in-tree local/reference/MOPS/)")
    parser.add_argument("--overrides", default=overrides_path)
    parser.add_argument("--master", default=master_schema_path)
    args = parser.parse_args(argv)
    if not args.isolated:
        raise SystemExit("leftover batch_generate_MIB is not live law; pass --isolated --outdir /tmp/...")
    xml_schema_path = args.xml
    overrides_path = args.overrides
    master_schema_path = args.master
    output_dir = args.outdir
    _refuse_live_wire(output_dir)
    process_captured_pages()

if __name__ == "__main__":
    _cli()