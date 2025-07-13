from flask import Flask, render_template, request, redirect, url_for
import os
from utils.extractor import extract_text_and_fields
from utils.ocr_highlight import highlight_field

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        images = request.files.getlist("images")

        print("Uploaded files:", images)
        print("Count:", len(images))

        if not images or len(images) != 3:
            return render_template("index.html", error="Please upload exactly 3 images.")

        extracted_items = []

        for img in images:
            filename = img.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            img.save(filepath)

            extracted_data = extract_text_and_fields(filepath)

            for key, item in extracted_data.items():
                if isinstance(item, dict):
                    extracted_items.append({
                        "key": key,
                        "value": item.get("value", "N/A"),
                        "confidence": item.get("confidence", "N/A"),
                        "source": "Gemini",
                        "image": filepath
                    })
                elif isinstance(item, list):
                    for subitem in item:
                        extracted_items.append({
                            "key": key,
                            "value": str(subitem),
                            "confidence": "N/A",
                            "source": "Gemini",
                            "image": filepath
                        })
                else:
                    extracted_items.append({
                        "key": key,
                        "value": str(item),
                        "confidence": "N/A",
                        "source": "Gemini",
                        "image": filepath
                    })

        return render_template("results.html", fields=extracted_items)

    return render_template("index.html")


@app.route("/highlight", methods=["POST"])
def highlight():
    key = request.form.get("key")
    value = request.form.get("value")
    image_path = request.form.get("image")

    highlighted_image_path = highlight_field(image_path, key, value)

    # Pass path to template to render image
    return render_template("highlight_view.html", image_path=highlighted_image_path)


if __name__ == "__main__":
    app.run(debug=True)
