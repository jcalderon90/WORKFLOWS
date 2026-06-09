import json

file = r"E:\1TRABAJO\PROGRAMMING\Proyectos\WORKFLOWS\SPECTRUM AGENTE\workflows\Send Media.json"
with open(file, encoding="utf-8") as f:
    data = json.load(f)

node = next(n for n in data["nodes"] if n["name"] == "Map Media Resources")
js = node["parameters"]["jsCode"]

# Reemplazar drive.google.com/uc?export=download&id= por drive.usercontent.google.com/download?id=
import re
old_pattern = r'https://drive\.google\.com/uc\?export=download&id=([A-Za-z0-9_\-]+)'
new_template = r'https://drive.usercontent.google.com/download?id=\1&export=download'

new_js = re.sub(old_pattern, new_template, js)

if new_js != js:
    node["parameters"]["jsCode"] = new_js
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Reemplazadas {len(re.findall(old_pattern, js))} URLs. Archivo guardado.")
else:
    print("  NO MATCH")
