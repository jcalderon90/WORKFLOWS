import json

file = r"E:\1TRABAJO\PROGRAMMING\Proyectos\WORKFLOWS\SPECTRUM AGENTE\workflows\Send Media.json"
with open(file, encoding="utf-8") as f:
    data = json.load(f)

# --- 1. Actualizar Map Media Resources ---
map_node = next(n for n in data["nodes"] if n["name"] == "Map Media Resources")
js = map_node["parameters"]["jsCode"]

# Reemplazar la función getObjectType + return por la nueva lógica con messages array
old_footer = """function getObjectType(url, canal) {
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

new_footer = """function buildMessages(url, canal) {
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

const messages = buildMessages(url, canal);

return [{
  json: {
    manychat_id: $input.item.json.manychat_id,
    canal: canal,
    proyecto: proyecto,
    media_disponible: url !== null,
    messages: messages
  }
}];"""

if old_footer in js:
    js = js.replace(old_footer, new_footer)
    map_node["parameters"]["jsCode"] = js
    print("  Map Media Resources: OK")
else:
    print("  Map Media Resources: NO MATCH")

# --- 2. Actualizar Send API ManyChat ---
send_node = next(n for n in data["nodes"] if n["name"] == "Send API ManyChat")
params = send_node["parameters"]

# Cambiar specifyBody a string y usar JSON.stringify con el array messages
params["specifyBody"] = "string"
params["body"] = "={{ JSON.stringify({ subscriber_id: $('Map Media Resources').item.json.manychat_id, data: { version: 'v2', content: { type: $('Map Media Resources').item.json.canal, messages: $('Map Media Resources').item.json.messages } } }) }}"
if "jsonBody" in params:
    del params["jsonBody"]
print("  Send API ManyChat: OK")

with open(file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Archivo guardado.")
