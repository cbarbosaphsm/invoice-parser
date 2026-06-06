from flask import Flask, request, jsonify
import pdfplumber
import base64
import tempfile
import os
import re

app = Flask(__name__)

def extract_text(pdf_path):
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=3, y_tolerance=3)
            if text:
                lines.extend(text.splitlines())
    return lines

def parse_invoice(lines):
    data = {}
    full_text = "\n".join(lines)

    # Invoice number
    m = re.search(r'No\s+(WM\d+)', full_text)
    data['inv_number'] = m.group(1) if m else ''

    # Date
    m = re.search(r'(\d{2}\s+\w+\s+\d{4})', full_text)
    data['inv_date'] = m.group(1) if m else ''

    # REF number
    m = re.search(r'REF\s*:\s*(\S+)', full_text)
    data['inv_ref'] = m.group(1) if m else ''

    # Logistics company
    m = re.search(r'REF\s*:\s*\S+\s+(.*)', full_text)
    data['logistics_company'] = m.group(1).strip() if m else ''

    # Route
    m = re.search(r'([A-Z]{3,})\s+([A-Z]{3,})\s*-\s*([A-Z]{3,})\s+([A-Z]{3,})', full_text)
    if m:
        data['route_origin'] = f"{m.group(1)} {m.group(2)}"
        data['route_destination'] = f"{m.group(3)} {m.group(4)}"
    else:
        data['route_origin'] = ''
        data['route_destination'] = ''

    # BL number
    m = re.search(r'BL:\s*(\d+)', full_text)
    data['bl_number'] = m.group(1) if m else ''

    # ETA
    m = re.search(r'ETA:\s*(.+)', full_text)
    data['eta'] = m.group(1).strip() if m else ''

    # Container
    m = re.search(r'([A-Z]{4}\d{7})\s*-\s*(\w+)', full_text)
    if m:
        data['container_number'] = m.group(1)
        data['container_type'] = m.group(2)
    else:
        data['container_number'] = ''
        data['container_type'] = ''

    # Ocean freight
    m = re.search(r'OCEAN FREIGHT[^\d]*([\d,]+\.?\d*)\s+USD', full_text)
    data['ocean_freight_usd'] = m.group(1).replace(',', '') if m else ''

    # Total
    m = re.search(r'TOTAL\s+([\d,]+\.\d{2})\s+USD', full_text)
    data['total_usd'] = m.group(1).replace(',', '') if m else ''

    # Client name
    m = re.search(r'TO:\s*\n(.+)', full_text)
    data['client_name'] = m.group(1).strip() if m else ''

    # Client RFC
    m = re.search(r'RFC:\s*(\S+)', full_text)
    data['client_rfc'] = m.group(1).strip() if m else ''

    # Bank beneficiary
    m = re.search(r'Benef[^\n:]*[:\s]+(.+)', full_text, re.IGNORECASE)
    data['bank_beneficiary'] = m.group(1).strip() if m else ''

    # Bank account
    m = re.search(r'ACCOUNT NO\.?:\s*(\S+)', full_text)
    data['bank_account'] = m.group(1) if m else ''

    # ABA
    m = re.search(r'ABA CODE\s*:\s*(\S+)', full_text)
    data['bank_aba'] = m.group(1) if m else ''

    # SWIFT
    m = re.search(r'SWIFT CODE[:\s]+(\S+)', full_text)
    data['bank_swift'] = m.group(1) if m else ''

    # Bank name
    m = re.search(r'(BANK OF .+?)(?:\n|$)', full_text)
    data['bank_name'] = m.group(1).strip() if m else ''

    # Payable to
    m = re.search(r'PAYABLE TO (.+)', full_text)
    data['payable_to'] = m.group(1).strip() if m else ''

    return data

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/parse', methods=['POST'])
def parse():
    payload = request.get_json()
    b64 = payload.get('base64_pdf')
    if not b64:
        return jsonify({'error': 'No base64_pdf provided'}), 400

    try:
        pdf_bytes = base64.b64decode(b64)
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(pdf_bytes)
            tmp_path = f.name

        lines = extract_text(tmp_path)
        os.unlink(tmp_path)
        result = parse_invoice(lines)
        return jsonify({'status': 'ok', 'data': result})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5055))
    app.run(host='0.0.0.0', port=port)
