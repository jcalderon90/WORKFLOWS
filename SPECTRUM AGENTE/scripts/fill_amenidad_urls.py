import json

file = r"E:\1TRABAJO\PROGRAMMING\Proyectos\WORKFLOWS\SPECTRUM AGENTE\workflows\Send Media.json"
with open(file, encoding="utf-8") as f:
    data = json.load(f)

node = next(n for n in data["nodes"] if n["name"] == "Map Media Resources")
js = node["parameters"]["jsCode"]

replacements = {
    "PVV":  ("https://res.cloudinary.com/dtmw4kwfo/video/upload/v1780971425/PVV_ABR_IG_CUR_AMND_exz4bc.mp4",
              "https://res.cloudinary.com/dtmw4kwfo/video/upload/v1780976014/pvv_amenidades_mtxjzk.mp4"),
    "PMAR": ("https://res.cloudinary.com/dtmw4kwfo/video/upload/v1780970987/En_Parque_Mariscal_tendr%C3%A1s_m%C3%A1s_diversi%C3%B3n_y_espacio_para_crear_recuerdos_inolvidables_sin_complic_vlqtev.mp4",
              "https://res.cloudinary.com/dtmw4kwfo/video/upload/v1780975779/pmar_amenidades_nzlzct.mp4"),
    "PPO":  ("https://res.cloudinary.com/dtmw4kwfo/video/upload/v1780971130/En_Parque_Portales_hemos_dise%C3%B1ado_m%C3%A1s_de_diez_ambientes_exclusivos_pensados_para_que_conectes_1_wkmhgx.mp4",
              "https://res.cloudinary.com/dtmw4kwfo/video/upload/v1780975716/ppo_amenidades_ojrp36.mp4"),
    "PPOL": ("https://res.cloudinary.com/dtmw4kwfo/video/upload/v1780971186/Amenidades_dise%C3%B1adas_para_vivirse_exclusivamente_En_Polanco_Parque_Boutique_cada_espacio_est%C3%A1_p_nflcci.mp4",
              "https://res.cloudinary.com/dtmw4kwfo/video/upload/v1780975777/ppol_amenidades_nzvq50.mp4"),
    "PSB":  ("https://res.cloudinary.com/dtmw4kwfo/video/upload/v1780971160/Parque_Sotobosque_combina_lujo_y_funcionalidad_en_cada_amenidad_Coworking_gourmet_kitchen_e_ckf32q.mp4",
              "https://res.cloudinary.com/dtmw4kwfo/video/upload/v1780975780/psb_amenidades_e0bjkz.mp4"),
}

for proyecto, (old_url, new_url) in replacements.items():
    if old_url in js:
        js = js.replace(old_url, new_url)
        print(f"  {proyecto}: OK")
    else:
        print(f"  {proyecto}: NO MATCH")

node["parameters"]["jsCode"] = js

with open(file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Archivo guardado.")
