import base64

with open("sample.pdf", "rb") as f:
    pdf_bytes = f.read()
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

print(pdf_base64)