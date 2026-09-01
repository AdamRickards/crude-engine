#!/usr/bin/env python3
"""Offline proof for issues 137/138/139: SSH overlay key_column + token cells."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402
from crude_engine.drivers.ssh_driver import SSHGatherDriver  # noqa: E402
from crude_engine.engine.crude import to_bool, to_num  # noqa: E402

SHOW_VLAN = (
    "Port    Acceptable   Ingress     \n"
    "Interface VLAN ID Frame Types  Filtering Priority\n"
    "--------- ------- ------------ --------- --------\n"
    "1/1       1       admit all    disable   0        \n"
    "3/8       1       admit all    disable   0        \n"
)

SHOW_STORM = (
    "Broadcasts              Multicasts              Unknown Unicasts\n"
    "Intf    Mode      Level         Mode      Level         Mode      Level\n"
    "------  ----------------------  ----------------------  ----------------------\n"
    "1/1     disabled            0%  disabled            0%  disabled            0%\n"
    "3/8     disabled            0%  disabled            0%  disabled            0%\n"
)

SHOW_IPSG = (
    "Interface  IP Source Guard  MAC Verify\n"
    "---------  ---------------  ----------\n"
    "1/1        no               no\n"
    "3/8        no               no\n"
)


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def ok(msg):
    print(f"PASS  {msg}")
    return 0


def _drv():
    drv = SSHGatherDriver.__new__(SSHGatherDriver)
    drv._driver_config = {}
    drv.attr_types = {}
    drv.attr_syntaxes = {}
    drv.context = {}
    return drv


def _read(overlay_file, name):
    overlay = yaml.safe_load(
        (ROOT / "crude_engine" / "wire" / "ssh" / overlay_file).read_text()
    )
    return overlay["attributes"][name]["sources"]["ssh"]["read"]


def main() -> int:
    rc = 0
    drv = _drv()

    for name, col in (
        ("dot1qpvid", 1),
        ("dot1qportacceptableframetypes", 2),
        ("dot1qportingressfiltering", 3),
    ):
        read = _read("q-bridge.yaml", name)
        if read.get("key_column") != 0 or read.get("column") != col:
            rc |= fail(f"q-bridge {name} read {read}")
        else:
            rc |= ok(f"q-bridge {name} column={col} key_column=0")

    vlan = drv._parse_table(
        SHOW_VLAN, {"parser": "table", "column": 2, "key_column": 0}
    )
    if list(vlan.keys()) != ["1/1", "3/8"] or vlan.get("1/1") != "admit all":
        rc |= fail(f"vlan keyed frame types {vlan}")
    else:
        rc |= ok("show vlan port keys by ifName; admit all is one cell")

    vmap = yaml.safe_load(
        (ROOT / "crude_engine" / "schemas" / "vlan.yaml").read_text()
    )["attributes"]["acceptable_frame_types"]["value_map"]
    if vmap.get("admit all") != "admitAll":
        rc |= fail(f"vlan schema value_map missing admit all: {vmap}")
    else:
        rc |= ok("schema maps SSH 'admit all' to admitAll")

    storm_mode = _read("trafficmgmt.yaml", "hm2trafficmgmtifingressstormctlbcastmode")
    storm_th = _read("trafficmgmt.yaml", "hm2trafficmgmtifingressstormctlbcastthreshold")
    mcast_mode = _read("trafficmgmt.yaml", "hm2trafficmgmtifingressstormctlmcastmode")
    if (
        storm_mode.get("key_column") != 0
        or storm_mode.get("column") != 1
        or storm_th.get("column") != 1
        or mcast_mode.get("column") != 2
        or not storm_mode.get("regex")
        or not storm_th.get("regex")
    ):
        rc |= fail(f"trafficmgmt reads {storm_mode} {storm_th} {mcast_mode}")
    else:
        rc |= ok("storm overlay key_column=0; B blob col 1; M blob col 2")

    keyed = drv._parse_table(
        SHOW_STORM, {"parser": "table", "column": 1, "key_column": 0}
    )
    if list(keyed.keys()) != ["1/1", "3/8"]:
        rc |= fail(f"storm keys {keyed}")
    else:
        rc |= ok("show storm-control ingress keys by Intf")

    mode = {
        k: drv._apply_pipeline(v, storm_mode, "", None) for k, v in keyed.items()
    }
    th = {
        k: drv._apply_pipeline(v, storm_th, "", None) for k, v in keyed.items()
    }
    if mode.get("1/1") != "disabled" or to_bool(mode["1/1"]) is not False:
        rc |= fail(f"storm mode {mode}")
    elif th.get("1/1") != "0" or to_num(th["1/1"]) != 0:
        rc |= fail(f"storm threshold {th}")
    else:
        rc |= ok("storm blob splits to disabled / 0")

    for name, col in (
        ("hm2agentipsgifverifysource", 1),
        ("hm2agentipsgifportsecurity", 2),
    ):
        read = _read("platform-switching.yaml", name)
        if read.get("key_column") != 0 or read.get("column") != col:
            rc |= fail(f"ipsg {name} read {read}")
        elif "type" in yaml.safe_load(
            (ROOT / "crude_engine" / "wire" / "ssh" / "platform-switching.yaml").read_text()
        )["attributes"][name]:
            rc |= fail(f"ipsg {name} still overrides type")
        else:
            rc |= ok(f"ipsg {name} column={col} key_column=0, no type override")

    ipsg = drv._parse_table(
        SHOW_IPSG, {"parser": "table", "column": 1, "key_column": 0}
    )
    if list(ipsg.keys()) != ["1/1", "3/8"] or ipsg.get("1/1") != "no":
        rc |= fail(f"ipsg keyed {ipsg}")
    elif to_bool(ipsg["1/1"]) is not False:
        rc |= fail(f"ipsg to_bool {ipsg}")
    else:
        rc |= ok("show ip source-guard interfaces keys by ifName; no → False")

    return rc


if __name__ == "__main__":
    sys.exit(main())
