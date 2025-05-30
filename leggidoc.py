from google.cloud import vision
import io
import os

# ✅ CORRETTO: usa r"..." per indicare una raw string
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\ScriptWF\ocr\keygoogle.json"

# Inizializza il client Vision
client = vision.ImageAnnotatorClient()

# Percorso dell'immagine da analizzare
image_path = "documento_cliente.jpg"

with io.open(image_path, 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)

# Riconoscimento del testo
response = client.text_detection(image=image)
texts = response.text_annotations

if texts:
    print("📄 Testo trovato nel documento:")
    print(texts[0].description)
else:
    print("❌ Nessun testo rilevato.")
    
input("\nPremi INVIO per uscire...")


