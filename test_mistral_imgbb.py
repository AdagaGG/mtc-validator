"""
Test OCR con Mistral + imgbb
"""

import sys
sys.path.insert(0, r"c:\Users\adria\Desktop\Proyectos Personales\Validador MTC")

import fitz
from PIL import Image
import requests
import json
import io

pdf_path = r"C:\Users\adria\Downloads\Mill_test_Certificate_1_.pdf"

print("=" * 80)
print("TEST MISTRAL OCR + IMGBB Upload")
print("=" * 80)

api_key_mistral = "kSh23thqlPbBtR1A0EKhm7qvmk8t32gr"
# Aquí irá tu API key de imgbb (obtén una gratis en https://api.imgbb.com/)
api_key_imgbb = "daa2afcd0165786e57e9b73bcba26de6"

try:
    print(f"\n1. Loading PDF...")
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    print(f"   ✓ PDF loaded: {len(pdf_bytes)} bytes")
    
    print(f"\n2. Converting PDF to image...")
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
    
    img_data = pix.tobytes("ppm")
    img = Image.open(io.BytesIO(img_data))
    img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
    img = img.convert('RGB')
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=80, optimize=True)
    img_byte_arr.seek(0)
    print(f"   ✓ Image created: {len(img_byte_arr.getvalue())} bytes")
    
    print(f"\n3. Uploading image to imgbb...")
    files = {'image': img_byte_arr.getvalue()}
    data = {'key': api_key_imgbb, 'expiration': '600'}
    
    upload_resp = requests.post(
        "https://api.imgbb.com/1/upload",
        files=files,
        data=data,
        timeout=30
    )
    upload_resp.raise_for_status()
    upload_result = upload_resp.json()
    
    if not upload_result.get('success'):
        print(f"   ❌ imgbb upload failed: {upload_result}")
    else:
        image_url = upload_result['data']['url']
        print(f"   ✓ Image URL: {image_url}")
        
        print(f"\n4. Calling Mistral API with public URL...")
        payload = {
            "model": "pixtral-12b",
            "max_tokens": 1000,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract all chemical composition values and mechanical properties "
                            "from this Mill Test Certificate. "
                            "Return ONLY JSON: [{\"elemento\": \"C_%\", \"valor\": 0.22}]"
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            }]
        }
        
        resp = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key_mistral}", "Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        
        print(f"   ✓ Status: {resp.status_code}")
        content = resp.json()['choices'][0]['message']['content']
        print(f"   Content preview: {content[:300]}...")
        
        # Try to parse JSON
        content_clean = content.replace('```json', '').replace('```', '').strip()
        try:
            data = json.loads(content_clean)
            print(f"\n5. Parsed JSON: {len(data)} items")
            for item in data[:5]:
                print(f"   - {item}")
        except json.JSONDecodeError as e:
            print(f"   Could not parse JSON: {e}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    if "YOUR_IMGBB_API_KEY" in str(api_key_imgbb):
        print("\n⚠️  You need to get an API key from https://api.imgbb.com/")
        print("   1. Go to https://api.imgbb.com/")
        print("   2. Register for free (email only)")
        print("   3. Copy your API key")
        print("   4. Paste it in the script above")
    import traceback
    traceback.print_exc()
