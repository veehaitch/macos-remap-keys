#!/usr/bin/env python3

import json, yaml
import textwrap
from typing import Dict, Any
import re


def load_keytables() -> Dict[str, Any]:
    with open("./keytables.yaml", "r") as f:
        return yaml.safe_load(f)


def load_config() -> Dict[str, Any]:
    with open("./config.yaml", "r") as f:
        return yaml.safe_load(f)


def key_id(usage_id: int) -> str:
    return 0x700000000 | usage_id


def remap(src_key_id: int, dst_key_id: int) -> str:
    mapping = {
        "HIDKeyboardModifierMappingSrc": hex(src_key_id),
        "HIDKeyboardModifierMappingDst": hex(dst_key_id),
    }

    return mapping


def hex_str_to_literal(s: str) -> str:
    return re.sub(r"\"(0x[0-9a-fA-F]+)\"", r"\1", s)


def create_property(
    config: Dict[str, Dict[str, str]], keytables: Dict[str, Dict[str, int]]
) -> str:
    res = []
    for keyinput, mappings in config.items():
        for src_key_name, dst_key_name in mappings.items():
            src_key_id = key_id(keytables[keyinput][src_key_name])
            dst_key_id = key_id(keytables[keyinput][dst_key_name])
            res.append(remap(src_key_id, dst_key_id))

    res = {"UserKeyMapping": res}

    s = json.dumps(res, separators=(",", ":"))

    return hex_str_to_literal(s)


def launchd_definition(hidutil_property: str, outpath: str) -> str:
    with open("./launchd-template.plist", "r") as f:
        template = f.read()

    res = template.replace("$REPLACEME$", hidutil_property)
    with open(outpath, "w") as f:
        f.write(res)

    return res


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--hidutil-property",
        "-p",
        action="store_true",
        help="Emit a definition to use with `hidutil property --set`",
    )
    group.add_argument(
        "--launchd-plist",
        "-l",
        type=str,
        help="Create a launchd definition at the given location; also printed to stdout",
    )
    args = parser.parse_args()

    keytables = load_keytables()
    config = load_config()

    if args.hidutil_property:
        print(create_property(config, keytables))
    else:
        print(
            launchd_definition(create_property(config, keytables), args.launchd_plist)
        )