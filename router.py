pythonimport pdfplumber

# Import every parser you have
from parsers.wm_world_maritime import parse as parse_wm
from parsers.ete_logistica import parse as parse_ete
from parsers.bill_of_lading_generic import parse as parse_bol
# Add new parsers here as you create them:
# from parsers.hapag_lloyd import parse as parse_hapag

# ─────────────────────────────────────────────────────
# Map of doc_type strings to parser functions
# These are the values FileMaker sends in the doc_type field
# ─────────────────────────────────────────────────────
PARSER_MAP = {
    'wm_world_maritime':      parse_wm,
    'ete_logistica':          parse_ete,
    'bill_of_lading_generic': parse_bol,
    # 'hapag_lloyd':          parse_hapag,
}

# ─────────────────────────────────────────────────────
# Fingerprints for auto-detection
# Each entry: (text_to_look_for, parser_function)
# Order matters — more specific fingerprints go first
# ─────────────────────────────────────────────────────
FINGERPRINTS = [
    ('WM WORLD MARITIME',      parse_wm),
    ('ETE LOGISTICA',          parse_ete),
    ('BILL OF LADING',         parse_bol),
    # ('HAPAG-LLOYD',           parse_hapag),
]

def extract_raw_text(pdf_path):
    """Extract all text from PDF for fingerprinting."""
    text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text(x_tolerance=3, y_tolerance=3)
            if t:
                text += t + '\n'
    return text.upper()

def detect_and_parse(pdf_path, doc_type='auto'):
    """
    Route the PDF to the correct parser.
    - If doc_type is provided by FileMaker, use it directly.
    - If doc_type is 'auto', scan the text and fingerprint-match.
    """

    # 1. FileMaker told us exactly what type it is
    if doc_type != 'auto' and doc_type in PARSER_MAP:
        return PARSER_MAP[doc_type](pdf_path)

    # 2. Auto-detect by scanning PDF text
    raw_text = extract_raw_text(pdf_path)

    for fingerprint, parser_func in FINGERPRINTS:
        if fingerprint.upper() in raw_text:
            return parser_func(pdf_path)

    # 3. Nothing matched
    return {
        'error': 'Unknown document type',
        'hint': 'Add a matching fingerprint to router.py or pass doc_type explicitly'
    }
