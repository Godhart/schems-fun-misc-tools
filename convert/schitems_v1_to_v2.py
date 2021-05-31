import yaml
import json
import sys
import os


def convert_schitems_v1_to_v2(source_path, output_path):
    print(f"Processing file {source_path}")
    try:
        with open(source_path, "r") as f:
            data = json.loads(f.read())
    except:
        return

    fallback_defaults = {
        "Bool": False,
        "Bits": "0",
        "int": 0,
        "numeric": 0.0
    }

    for item, data in data.get("data", {}).items():
        print(f"Converting {item}")
        result = {
            "format_version": [1, 0, 0],
            "name": data["name"],
            "ref_name": data.get("ref_name", "U"),
            "origin": "schedo",
            "kind": data["kind"],
            "version": [1, 0, 1, 0, 0],
            "hash": 0,
            "spec": [1, 0, 0],
            "signature": [0, 0, 0, 0],
            "version_history": {"1.0.1.0.0": "Initial version"},
            "thumbnail": "",
            "hints": {
                "text_hint": [data["text_hint"]],
                "text_short": [data["text_short"]],
                "text_long": [data.get("text_long", "")],
                "go_deep_ref": [data.get("go_deep_ref", "")],
                "go_broad_ref": [data.get("go_wide_ref", "")],
            },
            "customizable": [{"name": "general", "short_text": "", "long_text": "", "items": []}],
            "generics": {},
            "constants": [{"part_number": f"'{data['name'].upper()}'"}],
            "io": {},
            "context": {},
            "creator_actions": {},
            "runner_actions": {},
            "sounds_sets": {},
            "functions": {},
            "views": {"schematic": {
                "customizable": [],
                "generics": {},
                "constants": [],
                "items": {},
                "io": [],
                "areas": {},
                "sounds": {},
                "functions": {},
                "states": {},
                "images_sets": {},
                "sounds_sets": {}
            }},
        }

        width = data.get("graphics_options", {}).get("width", None)
        height = data.get("graphics_options", {}).get("height", None)
        result["views"]["schematic"]["width"] = width
        result["views"]["schematic"]["height"] = height

        sim = {
            "item": f"{result['origin']}:{result['name']}:{result['version']}"
        }
        for core, core_data in data.get("functors", {}).items():
            for field in core_data:
                sim[field] = core_data[field]

        context = result["context"]
        groups = {}
        customized_types = {}
        customizable_pins = {}
        index = 1000
        for group_name, group_data in data.get("io_list", {}).items():
            if group_name == "_non_functional_":
                continue
            index += 1
            group_index = group_data.get("group_index", index)
            group = groups[f"gr {group_index:4}-{group_name}"] = {}

            pindex = 1000
            for direction in ("in", "out"):
                for pin_name, pin_data in group_data.get(direction, {}).items():
                    pindex += 1
                    pin_index = pin_data.get("index", pindex)
                    if pin_name[0] == "_":
                        is_context = True
                        iopin = {}
                        vipin = {}
                    else:
                        is_context = False
                        iopin = group[f"io {pindex:4}-{pin_name}"] = {"direction": direction}
                        vipin = group[f"vi {pindex:4}-{pin_name}"] = {"pin": pin_name}
                        if pin_index <= 1000:
                            vipin["_index_"] = pin_index

                    stype = pin_data.get("type", "Bits")
                    sdefault = None
                    if stype[:5] == "copy:":
                        g, p = stype[5:].split(".")
                        px = None
                        if p not in customized_types:
                            stype = data.get("io_list", {}).get(g, {}).get("in", {}).get(p, {}).get("type", None)
                            sdefault = data.get("io_list", {}).get(g, {}).get("in", {}).get(p, {}).get("default", None)
                            if stype is None:
                                stype = data.get("io_list", {}).get(g, {}).get("out", {}).get(p, {}).get("type", None)
                                sdefault = data.get("io_list", {}).get(g, {}).get("out", {}).get(p, {}).get("default", None)
                            if stype is None:
                                for suffix in ("%i", "%e"):
                                    if p[-1] == "0":
                                        px = p[:-1]+suffix
                                    stype = data.get("io_list", {}).get(g, {}).get("in", {}).get(px, {}).get("type", None)
                                    sdefault = data.get("io_list", {}).get(g, {}).get("in", {}).get(px, {}).get("default", None)
                                    if stype is None:
                                        stype = data.get("io_list", {}).get(g, {}).get("out", {}).get(px, {}).get("type", None)
                                        sdefault = data.get("io_list", {}).get(g, {}).get("out", {}).get(px, {}).get("default", None)
                                    if stype is not None:
                                        break

                            if stype is None:
                                assert stype is not None, "Something went wrong on type copy"
                            for old, new in (("bit", "Bits"), ("bool", "Bool")):
                                if stype == old:
                                    stype = new
                                    break
                            assert stype in fallback_defaults, f"Unknown type: {stype}"
                            if sdefault is None:
                                sdefault = fallback_defaults[stype]

                            customized_types[p] = {"type": stype, "default": sdefault, "pins": []}
                            if px is not None:
                                customized_types[p]["base_pin"] = px
                            if not is_context:
                                customized_types[p]["pins"].append(pin_name)
                        stype = "${"+p+"_type}"
                        sdefault = "${"+p+"_default}"

                    for old, new in (("bit", "Bits"), ("bool", "Bool")):
                        if stype == old:
                            stype = new
                            break
                    if stype[0] != "$":
                        assert stype in fallback_defaults, f"Unknown type: {stype}"
                    default = pin_data.get("default", sdefault)
                    if default is None:
                        default = fallback_defaults[stype]

                    if is_context:
                        context[pin_name] = {}
                        value_descriptor = context[pin_name]["value"] = {"type": stype, "default": default}
                    else:
                        value_descriptor = iopin["signal"] = {"type": stype, "default": default}
                    if False:
                        if stype == "Bits":
                            value_descriptor["properties"] = {"width": None}
                        if stype == "Bool":
                            value_descriptor["properties"] = {"width": None}
                        if stype == "int":
                            value_descriptor["properties"] = {"from": None, "to": None, "wrap": None}
                        if stype == "numeric":
                            value_descriptor["properties"] = {"from": None, "to": None, "wrap": None}

                    if "%i" in pin_name:
                        if is_context:
                            g_nodes = [context[pin_name]]
                        else:
                            g_nodes = [iopin, vipin]
                        for node in g_nodes:
                            node["generate"] = {
                                "range": {
                                    "from": 0,
                                    "count": pin_data.get("%i:count", 1)
                                }
                        }

                    if not is_context:
                        if pin_data.get("clk_symbol", False):
                            iopin["function"] = "clock"

                        if not pin_data.get("enabled", True):
                            iopin["enabled"] = "${"+pin_name+"_pin}"
                            result["generics"][pin_name+"_pin"] = False
                            if pin_name not in customizable_pins:
                                customizable_pins[pin_name] = {}
                            customizable_pins[pin_name]["enabled"] = pin_name+"_pin"

                        side = pin_data.get("side", None)
                        if side is not None:
                            vipin["side"] = side

                        pos = pin_data.get("pin_pos", None)
                        if pos is not None:
                            vipin["pos"] = pos
                            vipin["pos"][0] -= result["views"]["schematic"]["width"]//2
                            vipin["pos"][1] = result["views"]["schematic"]["height"]//2 - vipin["pos"][1]

                        pin_tap = pin_data.get("pin_tap", None)
                        if pin_tap is not None:
                            vipin["pin_tap"] = pin_tap

                        text_offset = pin_data.get("text_offset", None)
                        if text_offset is not None:
                            vipin["text_offset"] = text_offset

        for group in groups:
            vigroup = {
                "group": group[8:],
                "pins": []
            }
            index = int(group[3:7])
            if index <= 1000:
                vigroup["_index_"] = index
            for pin in groups[group]:
                if pin[:2] != "vi":
                    continue
                vigroup["pins"].append(groups[group][pin])
            result["views"]["schematic"]["io"].append(vigroup)

        for group in groups:
            for pin in groups[group]:
                if pin[:2] != "io":
                    continue
                result["io"][pin[8:]] = groups[group][pin]

        for name, v in customized_types.items():
            result["generics"][f"{name}_type"] = v["type"]
            result["generics"][f"{name}_default"] = v["default"]
            # TODO: append to customizable too
            base_pin = v.get("base_pin", name)
            if pin_name not in customizable_pins:
                customizable_pins[pin_name] = {}
            result["io"][base_pin]["signal"]["type"] = "${"+name+"_type}"
            customizable_pins[pin_name]["type"] = pin_name + "_type"
            result["io"][base_pin]["signal"]["default"] = "${" + name + "_default}"
            customizable_pins[pin_name]["default"] = pin_name + "_default"

        customizable = result["customizable"][0]

        def add_customizable_group(node, items):
            for name, data in items:
                if data["kind"] == "group":
                    subgroup_items = data.get("items", [])
                    if len(subgroup_items) > 0:
                        node["items"].append({
                            "name": name,
                            "short_text": data.get("short_text", name),
                            "long_text": data.get("long_text", ""),
                            "items": []
                        })
                        add_customizable_group(node["items"][-1], data.get("items", []))
                elif data["kind"] == "value":
                    node["items"].append({
                        "name": name,
                        "short_text": data.get("short_text", name),
                        "long_text": data.get("long_text", ""),
                        "properties": {}
                    })
                    properties = node["items"][-1]["properties"]
                    value_type = data.get("type", None)
                    if value_type is None:
                        assert value_type is not None, f"No value type for {name}"

                    multiline = False
                    if value_type == "string_multiline":
                        value_type = "string"   # TODO: add multiline property to string
                        multiline = True

                    if value_type not in ("bool", "int", "numeric", "string", "list", "map"):
                        assert False, f"Unexpected value type for '{name}': '{value_type}'"

                    if value_type == "bool":
                        properties["type"] = "bool"
                        properties["default"] = data.get("default", False)

                    elif value_type == "int" or value_type == "numeric":
                        if value_type == "int" or len(data.get("range", [])) == 3 and data["range"][2] == 1:
                            properties["type"] = "int"
                        else:
                            properties["type"] = "numeric"
                        properties["default"] = data.get("default", 0)
                        values_range = data.get("range", None)
                        if values_range is None:
                            values_range = [None, None, None]
                        if len(values_range) == 2:
                            values_range.append(None)
                        properties["values"] = {
                            "from": values_range[0],
                            "to": values_range[1],
                            "step": values_range[2]
                        }

                    elif value_type == "string":
                        properties["type"] = "string"
                        properties["default"] = data.get("default", "")
                        properties["multiline"] = multiline

                    elif value_type == "list":
                        properties["type"] = "list"
                        properties["values"] = data.get("values", [None])
                        if len(properties["values"]) == 0:
                            properties["values"].append(None)
                        properties["default"] = data.get("default", properties["values"][0])

                    elif value_type == "list":
                        properties["type"] = "list"
                        properties["values"] = data.get("values", [None])
                        if len(properties["values"]) == 0:
                            properties["values"].append(None)
                        properties["default"] = data.get("default", properties["values"][0])

                    elif value_type == "map":
                        properties["type"] = "map"
                        properties["values"] = data.get("values", ["None", None])
                        if len(properties["values"]) == 0:
                            properties["values"].append(["None", None])
                        properties["default"] = data.get("default", properties["values"][0][0])

                    if name not in result["generics"]:
                        result["generics"][name] = properties["default"]
                else:
                    assert False, f"Unexpected node kind for '{name}': '{data['kind']}'"

        if len(data.get("customizable", [])) > 0:
            add_customizable_group(customizable, data.get("customizable", []))

        output_name = data["name"]+".yaml.schitem"
        with open(os.path.join(output_path, output_name), "w") as f:
            data = {f"{result['origin']}:{result['name']}:{'.'.join([str(x) for x in result['version']])}": result}
            yaml.safe_dump(data, f, indent=2, default_flow_style=False, sort_keys=False)


if __name__ == "__main__":
    path = sys.argv[1]
    output_path = sys.argv[2]
    for root, dirs, files in os.walk(path):
        for f in files:
            if f[-9:].lower() == "schi.json":
                convert_schitems_v1_to_v2(os.path.join(root, f), output_path)
