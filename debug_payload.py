"""
Debug del payload JSON que se envía
"""

import sys
sys.path.insert(0, r"c:\Users\adria\Desktop\Proyectos Personales\Validador MTC")

import fitz
from PIL import Image
import base64
import json
import io

pdf_path = r"C:\Users\adria\Downloads\Mill_test_Certificate_1_.pdf"

with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

doc = fitz.open(stream=pdf_bytes, filetype="pdf")
page = doc[0]
pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))

img_data = pix.tobytes("ppm")
img = Image.open(io.BytesIO(img_data))

if img.width > 2048 or img.height > 2048:
    img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)

img_byte_arr = io.BytesIO()
img = img.convert('RGB')
img.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
img_byte_arr.seek(0)
img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

# Build the exact payload
payload = {
    "model": "pixtral-12b-2409",
    "max_tokens": 1000,
    "messages": [{
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
            },
            {
                "type": "text",
                "text": "Extract elements and values. Return JSON only."
            }
        ]
    }]
}

# Print the structure
print("Payload structure:")
print(f"- Model: {payload['model']}")
print(f"- Max tokens: {payload['max_tokens']}")
print(f"- Messages: {len(payload['messages'])}")
msg = payload['messages'][0]
print(f"  - Role: {msg['role']}")
print(f"  - Content items: {len(msg['content'])}")
for i, item in enumerate(msg['content']):
    if item['type'] == 'image_url':
        url = item['image_url']['url']
        print(f"    [{i}] Type: image_url")
        print(f"        URL starts with: {url[:50]}...")
        print(f"        URL length: {len(url)}")
        print(f"        Valid base64 prefix: {url.startswith('data:image/png;base64,')}")
    else:
        print(f"    [{i}] Type: {item['type']}, Content length: {len(item['text'])}")

# Try to validate the JSON
json_str = json.dumps(payload)
print(f"\n✓ Payload is valid JSON ({len(json_str)} bytes)")

# Count the actual image bytes
print(f"✓ Image PNG size: {len(img_byte_arr.getvalue())} bytes")
