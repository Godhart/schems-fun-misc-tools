import yaml
import json
import sys
import re

if __name__ == "__main__":
    path = sys.argv[1]
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    opath = re.sub(".yaml", ".json", path)
    if opath == path:
        opath = path + ".json"
    with open(opath, "w") as f:
        f.write(json.dumps(data, indent=2))
    