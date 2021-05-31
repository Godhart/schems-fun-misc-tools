import sys
import re


def parse(path):
    current_class = None
    current_comments = []
    classes = {}
    with open(path, "r") as f:
        line_n = 0
        while True:
            line_n += 1
            line = f.readline()
            if line == "":
                break
            ls = line.strip()

            if ls == "":
                current_comments = []
                continue
            if ls == "---":
                current_comments = []
                current_class = None
                continue
            if line[0:2] == "# ":
                if current_class is not None:
                    continue
                current_comments.append(ls[2:])
                continue
            if current_class is None:
                m = re.match(r"^(\w+)\s*:\s*#?.*", line)
                if m is None:
                    raise ValueError(f"Unexpected string at line {line_n} (#1).\nExpecting class name")
                current_class = m.groups()[0]
                classes[current_class] = {
                    "description": current_comments,    # Description from comments
                    "members": {},                      # Class members
                    "uses": [],                         # Other classes that are referenced from this one   # TODO:
                    "used_by": [],                      # Other classes that are using this one             # TODO:
                }
                continue

            if ls[0:2] == "# ":
                continue

            m = re.match(r"^\s\s(\w+):\s*([^#]+)(?:#\s(.*))?", line)
            if m is None:
                raise ValueError(f"Unexpected string at line {line_n} (#2).\nExpecting member name")

            member_name, typedef, description = m.groups()
            classes[current_class]["members"][member_name] = {
                "typedef": typedef.strip(),     # Type as it defined in yamale schema
                "description": description,     # Description from comments
                "clss": [],                     # Reference to other class, is set later    # TODO:
                "kind": None,                   # scalar/map/list                           # TODO:
                "optional": False,              # True if may be omitted or have None as value
                "type": None,                   # Data type
                "default": None,                # Default value for optional fields
            }
    return classes


def analyze(classes):
    missing = {

    }
    for name, data in classes.items():
        for member, mdata in data["members"].items():
            refs = re.findall(r"include\('(\w+)'\)", mdata["typedef"])
            for ref in refs:
                mdata["clss"].append(ref)
                data["uses"].append(ref)
                if ref not in classes:
                    missing[ref] = {
                        "description": "Definition is Missing",           # Description from comments
                        "members": {},                      # Class members
                        "uses": [],                         # Other classes that are referenced from this one   # TODO:
                        "used_by": [],                      # Other classes that are using this one             # TODO:
                    }
                    print(f"Definition of '{ref}' is missing!")
                    missing[ref]["used_by"].append(name)
                else:
                    classes[ref]["used_by"].append(name)

            m = re.search(r"required=False", mdata["typedef"])
            if m is not None:
                mdata["optional"] = None
                m = re.search(r"none=False", mdata["typedef"])
                if m is not None:
                    mdata["optional"] = True
                m = re.search(r"\[default:(.+?)\]", mdata['description'])
                if m is not None:
                    mdata["default"] = m.groups()[0]
                    if mdata["default"][0] == "(" and mdata["default"][-1] == ")":  # Tuple to list conversion
                        mdata["default"] = "["+mdata["default"][1:-1]+"]"
                    mdata['description'] = re.sub(r"\[default:(.+?)\]", "", mdata['description']).strip()

            m = re.search(r"\b(map|list)\(", mdata["typedef"])
            if m is not None:
                if m.groups()[0] == "map":
                    mdata["kind"] = "map"
                else:
                    mdata["kind"] = "list"
            else:
                mdata["kind"] = "scalar"

            if len(mdata["clss"]) > 0:
                mdata["type"] = "cls"
                continue

            m = re.search(r"[^=]\bnum\(", mdata["typedef"])
            if m is not None:
                mdata["type"] = "num"
                continue

            m = re.search(r"[^=]\bint\(", mdata["typedef"])
            if m is not None:
                mdata["type"] = "int"
                continue

            m = re.search(r"[^=]\bbool\(", mdata["typedef"])
            if m is not None:
                mdata["type"] = "bool"
                continue

            m = re.search(r"[^=]\bstr\(", mdata["typedef"])
            if m is not None:
                mdata["type"] = "str"
                continue
    for m in missing.keys():
        classes[m] = missing[m]


def to_uml(classes):
    result = []
    result.append("@startuml")
    for name, data in classes.items():
        result.append(f"map {name} {{")
        for member, mdata in data["members"].items():
            member_type = str(mdata['type'])

            if mdata["kind"] == "map":
                member_type = '{'+member_type+'}'
            elif mdata["kind"] == "list":
                member_type = '['+member_type+']'

            optional = ""
            if mdata["optional"] is True:
                optional = "*"
            elif mdata["optional"] is None:
                optional = "**"
            # result.append(f"  {mdata['type']}{optional} => {member}")
            result.append(f"  {member} => {member_type}{optional}")
        result.append("}")
        result.append("")

    for name, data in classes.items():
        for member, mdata in data["members"].items():
            if mdata["type"] != "cls":
                continue
            for ref in mdata["clss"]:
                kind = ""
                # if mdata["kind"] == "map":
                #     kind = '"{}"'
                # elif mdata["kind"] == "list":
                #     kind = '"[]"'
                result.append(f"{name}::{member} {kind} => {ref}")

    result.append("@enduml")
    return "\n".join(result)


if __name__ == "__main__":
    classes = parse(sys.argv[1])
    analyze(classes)
    uml = to_uml(classes)
    a = 1
