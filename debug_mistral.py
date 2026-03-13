"""
Debug Mistral API call with PyMuPDF + PIL
"""

import sys
sys.path.insert(0, r"c:\Users\adria\Desktop\Proyectos Personales\Validador MTC")

import fitz
from PIL import Image
import base64
import requests
import json
import io

pdf_path = r"C:\Users\adria\Downloads\Mill_test_Certificate_1_.pdf"

print("=" * 80)
print("DEBUG MISTRAL API CALL (PyMuPDF + PIL)")
print("=" * 80)

try:
    api_key = "kSh23thqlPbBtR1A0EKhm7qvmk8t32gr"  # API key que configuramos
    
    print(f"\n1. API Key configured: {'✓' if api_key else '❌'}")
    
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    print(f"2. PDF loaded: {len(pdf_bytes)} bytes")
    
    # Convert to image using PyMuPDF + PIL
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    print(f"3. PDF opened with PyMuPDF: {len(doc)} page(s)")
    
    if len(doc) < 1:
        print("   ❌ No pages in PDF")
    else:
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
        
        # Convert via PIL
        img_data = pix.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))
        
        # Resize
        img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        img_byte_arr = io.BytesIO()
        img = img.convert('RGB')
        img.save(img_byte_arr, format='JPEG', quality=60, optimize=True)
        img_byte_arr.seek(0)
        img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        print(f"4. Converted to PNG base64: {len(img_b64)} chars")
        
        # Build payload
        payload = {
            "model": "pixtral-12b",
            "max_tokens": 1000,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_b64[:50]}..."}  # truncated for display
                    },
                    {
                        "type": "text",
                        "text": (
                            "Extract all chemical composition values and mechanical properties "
                            "from this Mill Test Certificate. "
                            "Return ONLY a valid JSON array, no markdown, no explanation. "
                            "Format: [{\"elemento\": \"C_%\", \"valor\": 0.22}] "
                            "Use ONLY these element names: "
                            "Si_%, Fe_%, Cu_%, Mn_%, Mg_%, Cr_%, Zn_%, Ti_%, Al_%, "
                            "C_%, P_%, S_%, Ni_%, Mo_%, V_%, "
                            "YS_MPa, UTS_MPa, Elong_% "
                            "Skip elements with value '-' or missing."
                        )
                    }
                ]
            }]
        }
        
        print(f"5. Payload created, sending to Mistral API...")
        print(f"   Model: {payload['model']}")
        print(f"   Max tokens: {payload['max_tokens']}")
        
        # Call API
        resp = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"\n6. API Response:")
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"   ✓ Success!")
            content = result['choices'][0]['message']['content']
            print(f"   Content preview: {content[:500]}...")
            
            # Parse JSON
            content = content.replace('```json', '').replace('```', '').strip()
            data = json.loads(content)
            print(f"\n   Parsed JSON: {len(data)} items")
            for item in data:
                print(f"     - {item}")
        else:
            print(f"   ❌ Error: {resp.status_code}")
            print(f"   Response: {resp.text[:300]}")

except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()
