import os
from flask import Flask, request, jsonify
from google.cloud import vision
import io
from datetime import datetime

app = Flask(__name__)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\ScriptWF\ocr\keygoogle.json"
client = vision.ImageAnnotatorClient()

SAVE_FOLDER = r"C:\ScriptWF\documenti"
os.makedirs(SAVE_FOLDER, exist_ok=True)

def estrai_testo_da_bytes(content):
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    return texts[0].description if texts else ""

@app.route("/processa", methods=["POST"])
def processa():
    fronte = request.files.get("fronte")
    retro = request.files.get("retro")

    if not fronte or not retro:
        return jsonify({"errore": "Fronte o retro mancanti"}), 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_file_fronte = os.path.join(SAVE_FOLDER, f"{timestamp}_fronte.jpg")
    nome_file_retro = os.path.join(SAVE_FOLDER, f"{timestamp}_retro.jpg")

    fronte.save(nome_file_fronte)
    retro.save(nome_file_retro)

    with open(nome_file_fronte, "rb") as f:
        testo_fronte = estrai_testo_da_bytes(f.read())

    with open(nome_file_retro, "rb") as f:
        testo_retro = estrai_testo_da_bytes(f.read())

    testo_completo = testo_fronte + "\n" + testo_retro

    return jsonify({
        "estratti": testo_completo,
        "fronte": nome_file_fronte,
        "retro": nome_file_retro
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
