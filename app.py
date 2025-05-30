from flask import Flask, request, jsonify
from google.cloud import vision
import os
import io
import re

app = Flask(__name__)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keygoogle.json"

client = vision.ImageAnnotatorClient()

SAVE_FOLDER = "estratti"
os.makedirs(SAVE_FOLDER, exist_ok=True)

def estrai_dati(text):
    nome = re.search(r"Nome[:\s]+([A-ZÀ-Ù][a-zà-ù]+)", text)
    cognome = re.search(r"Cognome[:\s]+([A-ZÀ-Ù][a-zà-ù]+)", text)
    cf = re.search(r"[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]", text)

    return {
        "nome": nome.group(1) if nome else "",
        "cognome": cognome.group(1) if cognome else "",
        "codice_fiscale": cf.group(0) if cf else "",
        "raw_text": text
    }

def ocr_google(image_bytes):
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    return texts[0].description if texts else ""

@app.route('/processa', methods=['POST'])
def processa_documenti():
    documento_fronte = request.files.get("documento_fronte")
    documento_retro = request.files.get("documento_retro")
    cf_fronte = request.files.get("cf_fronte")
    cf_retro = request.files.get("cf_retro")

    if not all([documento_fronte, documento_retro, cf_fronte, cf_retro]):
        return jsonify({"errore": "Tutti e 4 i file (documento fronte/retro, CF fronte/retro) sono obbligatori."}), 400

    testo_doc_fronte = ocr_google(documento_fronte.read())
    testo_doc_retro = ocr_google(documento_retro.read())
    testo_cf_fronte = ocr_google(cf_fronte.read())
    testo_cf_retro = ocr_google(cf_retro.read())

    testo_completo = "\n".join([testo_doc_fronte, testo_doc_retro, testo_cf_fronte, testo_cf_retro])

    dati = estrai_dati(testo_completo)

    if not all([dati["nome"], dati["cognome"], dati["codice_fiscale"]]):
        return jsonify({"estratti": testo_completo, "errore": "Immagini non leggibili o dati mancanti"}), 200

    nomefile = f"{dati['nome']}_{dati['cognome']}_{dati['codice_fiscale']}.txt"
    pathfile = os.path.join(SAVE_FOLDER, nomefile)

    with open(pathfile, "w", encoding="utf-8") as f:
        f.write(testo_completo)

    return jsonify({
        "successo": True,
        "estratti": testo_completo,
        "file_salvato": nomefile
    })

if __name__ == "__main__":
    app.run(debug=True)
