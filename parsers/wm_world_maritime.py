python"""
Parser: WM World Maritime Ltd.
Document type: Ocean Freight Invoice
Fingerprint: "WM WORLD MARITIME"
"""
import pdfplumber
import re

def extract_text(pdf_path):
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=3, y_tolerance=3)
            if text:
                lines.extend(text.splitlines())
    return lines

def parse(pdf_path):
    lines = extract_text(pdf_path)
    full_text = "\n".join(lines)
    data = {}

    data['doc_type'] = 'wm_world_maritime'

    m = re.search(r'No\s+(WM\d+)', full_text)
    data['inv_number'] = m.group(1) if m else ''

    m = re.search(r'(\d{2}\s+\w+\s+\d{4})', full_text)
    data['inv_date'] = m.group(1) if m else ''

    m = re.search(r'REF\s*:\s*(\S+)', full_text)
    data['inv_ref'] = m.group(1) if m else ''

    m = re.search(r'REF\s*:\s*\S+\s+(.*)', full_text)
    data['logistics_company'] = m.group(1).strip() if m else ''

    m = re.search(r'([A-Z]{3,})\s+([A-Z]{3,})\s*-\s*([A-Z]{3,})\s+([A-Z]{3,})', full_text)
    if m:
        data['route_origin'] = f"{m.group(1)} {m.group(2)}"
        data['route_destination'] = f"{m.group(3)} {m.group(4)}"
    else:
        data['route_origin'] = ''
        data['route_destination'] = ''

    m = re.search(r'BL:\s*(\d+)', full_text)
    data['bl_number'] = m.group(1) if m else ''

    m = re.search(r'ETA:\s*(.+)', full_text)
    data['eta'] = m.group(1).strip() if m else ''

    m = re.search(r'([A-Z]{4}\d{7})\s*-\s*(\w+)', full_text)
    if m:
        data['container_number'] = m.group(1)
        data['container_type'] = m.group(2)
    else:
        data['container_number'] = ''
        data['container_type'] = ''

    m = re.search(r'OCEAN FREIGHT[^\d]*([\d,]+\.?\d*)\s+USD', full_text)
    data['ocean_freight_usd'] = m.group(1).replace(',', '') if m else ''

    m = re.search(r'TOTAL\s+([\d,]+\.\d{2})\s+USD', full_text)
    data['total_usd'] = m.group(1).replace(',', '') if m else ''

    m = re.search(r'TO:\s*\n(.+)', full_text)
    data['client_name'] = m.group(1).strip() if m else ''

    m = re.search(r'RFC:\s*(\S+)', full_text)
    data['client_rfc'] = m.group(1).strip() if m else ''

    m = re.search(r'Benef[^\n:]*[:\s]+(.+)', full_text, re.IGNORECASE)
    data['bank_beneficiary'] = m.group(1).strip() if m else ''

    m = re.search(r'ACCOUNT NO\.?:\s*(\S+)', full_text)
    data['bank_account'] = m.group(1) if m else ''

    m = re.search(r'ABA CODE\s*:\s*(\S+)', full_text)
    data['bank_aba'] = m.group(1) if m else ''

    m = re.search(r'SWIFT CODE[:\s]+(\S+)', full_text)
    data['bank_swift'] = m.group(1) if m else ''

    m = re.search(r'(BANK OF .+?)(?:\n|$)', full_text)
    data['bank_name'] = m.group(1).strip() if m else ''

    m = re.search(r'PAYABLE TO (.+)', full_text)
    data['payable_to'] = m.group(1).strip() if m else ''

    return data
