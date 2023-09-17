import json
new = []
with open("token.json") as f:
    cookies = json.load(f)
for cookie in cookies:
    pp = {}
    pp["name"] = cookie["name"]
    pp["value"] = cookie["value"]
    new.append(pp)
with open("token.json", 'w') as f:
    json.dump(new, f)