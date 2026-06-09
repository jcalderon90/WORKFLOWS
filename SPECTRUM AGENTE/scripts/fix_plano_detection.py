import json

file = r"E:\1TRABAJO\PROGRAMMING\Proyectos\WORKFLOWS\SPECTRUM AGENTE\workflows\Send Media.json"
with open(file, encoding="utf-8") as f:
    data = json.load(f)

node = next(n for n in data["nodes"] if n["name"] == "Map Media Resources")
js = node["parameters"]["jsCode"]

old = """function buildMessages(url, canal) {
  if (!url) return [{ type: 'image', url: null }];
  const isVideo = /\\.(mp4|mov|avi|webm)/i.test(url);
  const isPdf = /\\.pdf/i.test(url);
  if (isVideo && canal === 'whatsapp') {
    const thumbnail = url.replace(/\\.(mp4|mov|avi|webm)$/i, '.jpg');
    return [
      { type: 'image', url: thumbnail },
      { type: 'text', text: 'Ver video completo: ' + url }
    ];
  }
  if (isVideo) return [{ type: 'video', url: url }];
  if (isPdf) return [{ type: 'file', url: url }];
  return [{ type: 'image', url: url }];
}

const messages = buildMessages(url, canal);"""

new = """function buildMessages(url, canal, tipo) {
  if (!url) return [{ type: 'image', url: null }];
  const isVideo = /\\.(mp4|mov|avi|webm)/i.test(url);
  const isPdf = tipo === 'plano' || /\\.pdf/i.test(url);
  if (isVideo && canal === 'whatsapp') {
    const thumbnail = url.replace(/\\.(mp4|mov|avi|webm)$/i, '.jpg');
    return [
      { type: 'image', url: thumbnail },
      { type: 'text', text: 'Ver video completo: ' + url }
    ];
  }
  if (isVideo) return [{ type: 'video', url: url }];
  if (isPdf) return [{ type: 'file', url: url }];
  return [{ type: 'image', url: url }];
}

const messages = buildMessages(url, canal, tipo);"""

if old in js:
    js = js.replace(old, new)
    node["parameters"]["jsCode"] = js
    print("  buildMessages: OK")
else:
    print("  buildMessages: NO MATCH")

with open(file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Archivo guardado.")
