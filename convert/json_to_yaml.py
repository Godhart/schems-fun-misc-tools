import yaml
import json
import sys
import re

if __name__ == "__main__":
    path = sys.argv[1]
    with open(path, "r") as f:
        data = json.load(f)
    opath = re.sub(".json", ".json-to.yaml", path)
    if opath == path:
        opath = path + ".json-to.yaml"
    with open(opath, "w") as f:
        f.write(yaml.dump(data, indent=2))
    