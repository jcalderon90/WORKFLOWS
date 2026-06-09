import json

file = r"E:\1TRABAJO\PROGRAMMING\Proyectos\WORKFLOWS\SPECTRUM AGENTE\workflows\Send Media.json"
with open(file, encoding="utf-8") as f:
    data = json.load(f)

node = next(n for n in data["nodes"] if n["name"] == "Map Media Resources")

old_footer = """function getObjectType(url) {
  if (!url) return 'image';
  if (/\\.(mp4|mov|avi|webm)/i.test(url)) return 'video';
  if (/\\.pdf/i.test(url)) return 'file';
  return 'image';
}

return [{
  json: {
    manychat_id: $input.item.json.manychat_id,
    canal: canal,
    proyecto: proyecto,
    url: url,
    media_disponible: url !== null,
    objectType: getObjectType(url)
  }
}];"""

new_footer = """function getObjectType(url, canal) {
  if (!url) return 'image';
  const isVideo = /\\.(mp4|mov|avi|webm)/i.test(url);
  if (isVideo && canal === 'whatsapp') return 'image';
  if (isVideo) return 'video';
  if (/\\.pdf/i.test(url)) return 'file';
  return 'image';
}

const objectType = getObjectType(url, canal);
const resolvedUrl = (objectType === 'image' && url && /\\.(mp4|mov|avi|webm)/i.test(url))
  ? url.replace(/\\.(mp4|mov|avi|webm)$/i, '.jpg')
  : url;

return [{
  json: {
    manychat_id: $input.item.json.manychat_id,
    canal: canal,
    proyecto: proyecto,
    url: resolvedUrl,
    media_disponible: url !== null,
    objectType: objectType
  }
}];"""

js = node["parameters"]["jsCode"]
if old_footer in js:
    js = js.replace(old_footer, new_footer)
    print("  Reemplazado OK")
else:
    print("  NO MATCH — verifica el footer del jsCode")

node["parameters"]["jsCode"] = js

with open(file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Archivo guardado.")
