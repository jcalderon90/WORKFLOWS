import json

file = r"E:\1TRABAJO\PROGRAMMING\Proyectos\WORKFLOWS\SPECTRUM AGENTE\workflows\Send Media.json"
with open(file, encoding="utf-8") as f:
    data = json.load(f)

node = next(n for n in data["nodes"] if n["name"] == "Map Media Resources")
js = node["parameters"]["jsCode"]

# Reemplazos: (proyecto, tipo, nueva_url)
updates = [
    ("PVV",  "avance_obra", "https://res.cloudinary.com/dtmw4kwfo/video/upload/v1780972932/PVV_MAR_IG_OBRA_hbazgx.mp4"),
    ("PPO",  "avance_obra", "https://res.cloudinary.com/dtmw4kwfo/video/upload/v1780972938/PPO_ABR_IG_OBRA_vwtfhw.mp4"),
]

for proyecto, tipo, url in updates:
    old = f'"{tipo}": null'
    new = f'"{tipo}": "{url}"'
    # Buscar dentro del bloque del proyecto correcto
    marker = f'"{proyecto}": {{'
    idx = js.find(marker)
    if idx == -1:
        print(f"  {proyecto}/{tipo}: NO ENCONTRADO proyecto")
        continue
    block_end = js.find('}', idx)
    block = js[idx:block_end]
    if old in block:
        js = js[:idx] + block.replace(old, new, 1) + js[block_end:]
        print(f"  {proyecto}/{tipo}: OK")
    else:
        print(f"  {proyecto}/{tipo}: NO MATCH")

node["parameters"]["jsCode"] = js

with open(file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Archivo guardado.")
