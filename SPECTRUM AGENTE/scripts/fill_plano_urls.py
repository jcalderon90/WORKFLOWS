import json

file = r"E:\1TRABAJO\PROGRAMMING\Proyectos\WORKFLOWS\SPECTRUM AGENTE\workflows\Send Media.json"
with open(file, encoding="utf-8") as f:
    data = json.load(f)

node = next(n for n in data["nodes"] if n["name"] == "Map Media Resources")
js = node["parameters"]["jsCode"]

plano_urls = {
    "PVV":  "https://drive.google.com/uc?export=download&id=1m7-eXU3Lw1xVRRsDvJ0B5Czxda4hFvGX",
    "PMAR": "https://drive.google.com/uc?export=download&id=1fT3tPv0dYkzuJcnD8LJHC1GtDAyXbszN",
    "PPO":  "https://drive.google.com/uc?export=download&id=1FbmQA96iJW6uosODYPHWbzGXPxUoUlD-",
    "PPOL": "https://drive.google.com/uc?export=download&id=1oQwk1TxDwwat9PgZPPPbUOqzrMLRUcOu",
    "PSB":  "https://drive.google.com/uc?export=download&id=1SfUniFrWxiaLcwKNV8nVxFK38vQADjbp",
}

for proyecto, url in plano_urls.items():
    marker = f'"{proyecto}": {{'
    idx = js.find(marker)
    if idx == -1:
        print(f"  {proyecto}: NO ENCONTRADO proyecto")
        continue
    block_end = js.find('}', idx)
    block = js[idx:block_end]
    old = '"plano":       null'
    new = f'"plano":       "{url}"'
    if old in block:
        js = js[:idx] + block.replace(old, new, 1) + js[block_end:]
        print(f"  {proyecto}: OK")
    else:
        print(f"  {proyecto}: NO MATCH")

node["parameters"]["jsCode"] = js

with open(file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Archivo guardado.")
