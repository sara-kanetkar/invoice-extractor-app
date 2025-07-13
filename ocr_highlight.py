import os
import cv2
import easyocr
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import uuid

def highlight_field(image_path, key, value):
    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(image_path)

    matched_boxes = []
    for bbox, text, conf in results:
        if key.lower() in text.lower() or value.lower() in text.lower():
            matched_boxes.append(bbox)

    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    fig, ax = plt.subplots()
    ax.imshow(img_rgb)

    for box in matched_boxes:
        (tl, tr, br, bl) = box
        width = np.linalg.norm(np.array(tr) - np.array(tl))
        height = np.linalg.norm(np.array(bl) - np.array(tl))
        rect = patches.Rectangle(tl, width, height, linewidth=2, edgecolor='red', facecolor='none')
        ax.add_patch(rect)

    ax.axis("off")

    # Ensure output folder exists
    output_dir = "static/extracted_images"
    os.makedirs(output_dir, exist_ok=True)

    # Create and return a relative path
    filename = f"highlighted_{uuid.uuid4().hex}.png"
    out_path = os.path.join(output_dir, filename)
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0)
    plt.close()

    return f"static/extracted_images/{filename}"
