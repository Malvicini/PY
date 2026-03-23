from flask import Flask, render_template, jsonify, request, redirect, url_for
from data_loader import DataLoader
from flask import send_file, make_response
import io
import requests
import subprocess
import sys
import os
import json
import tempfile
import shlex
import re

app = Flask(__name__)

# Initialize data loader with the Excel file in workspace
DATA_FILE = 'Gestione_Studi_DB_20251010.xlsx'
loader = DataLoader(DATA_FILE)

# Cache for groups/machines data (loaded once at startup)
_groups_machines_cache = None

def get_groups_machines_cached():
    """Load groups/machines data once and cache it in memory for fast access"""
    global _groups_machines_cache
    if _groups_machines_cache is not None:
        return _groups_machines_cache
    
    # Load from Excel
    df = loader.get_groups_machines()
    if df is None or df.empty:
        _groups_machines_cache = []
        return _groups_machines_cache
    
    # Convert to list of dicts
    data = []
    for _, row in df.iterrows():
        data.append({
            'id': str(row.get('id', '')).strip(),
            'cod': str(row.get('cod', '')).strip(),
            'pro': str(row.get('pro', '')).strip(),
            'tipo': str(row.get('tipo', '')).strip(),
            'articolo': str(row.get('articolo', '')).strip(),
            'desart': str(row.get('desart', '')).strip(),
        })
    _groups_machines_cache = data
    return _groups_machines_cache


@app.route('/')
def index():
    # For now a simple login-free demo: show main UI
    return render_template('index.html')


@app.route('/api/families')
def families():
    # Return families and their collapsed sequences on demand
    families = loader.get_families()
    return jsonify(families)


@app.route('/api/sequences')
def sequences():
    fam_code = request.args.get('family_code')
    if not fam_code:
        return jsonify({'error': 'family_code required'}), 400
    seqs = loader.get_sequences_for_family(fam_code)
    return jsonify(seqs)


@app.route('/api/all_sequences')
def all_sequences():
    # Return all sequences for all families (for client-side filtering)
    families = loader.get_families()
    all_seqs = []
    for fam in families:
        seqs = loader.get_sequences_for_family(fam['family_code'])
        for seq in seqs:
            seq['family_code'] = fam['family_code']  # Add family code to each sequence
            all_seqs.append(seq)
    return jsonify(all_seqs)


@app.route('/api/groups_machines')
def groups_machines():
    fam_code = request.args.get('family_code')
    seq_code = request.args.get('sequence_code')
    if not fam_code:
        return jsonify({'error': 'family_code required'}), 400
    groups_machines = loader.get_groups_machines_for_family(fam_code, seq_code)
    return jsonify(groups_machines)


@app.route('/api/all_groups_machines')
def all_groups_machines():
    # Return cached groups and machines data (loaded once at startup)
    data = get_groups_machines_cached()
    return jsonify(data)


@app.route('/api/fetch_pdf', methods=['POST'])
def fetch_pdf():
    # Deprecated: selenium-based PDF fetching removed. Use /api/fetch_pdf_local instead.
    return jsonify({'error': 'endpoint removed, use /api/fetch_pdf_local'}), 410


@app.route('/api/proxy_pdf', methods=['POST'])
def proxy_pdf():
    """Proxy an arbitrary PDF URL and return bytes to the client.

    Accepts JSON: { url: string, cookie: optional string }
    Use this when the PDF URL requires session cookies; you can paste the
    URL from the browser and optionally paste the cookie header if available.
    """
    data = request.json or {}
    url = data.get('url')
    cookie = data.get('cookie')
    if not url:
        return jsonify({'error': 'url required'}), 400

    headers = {
        'User-Agent': 'Raccoglitore/1.0'
    }
    if cookie:
        # allow user to paste just the raw cookie value (e.g. '223F52...')
        # in that case assume it's the common JSESSIONID
        if '=' not in cookie:
            cookie = 'JSESSIONID=' + cookie
        headers['Cookie'] = cookie

    try:
        r = requests.get(url, headers=headers, timeout=15, stream=True)
    except Exception as e:
        return jsonify({'error': 'request failed', 'detail': str(e)}), 502

    if r.status_code != 200:
        return jsonify({'error': 'upstream returned error', 'status_code': r.status_code}), 502

    content_type = r.headers.get('Content-Type', 'application/octet-stream')
    data_bytes = r.content
    out = make_response(data_bytes)
    out.headers.set('Content-Type', content_type)
    out.headers.set('Content-Disposition', 'inline; filename="remote.pdf"')
    return out


@app.route('/api/run_quick_proxy', methods=['POST'])
def run_quick_proxy():
    """Run the proxy using the preconfigured quick_test.json values.

    This allows a one-click test: the server reads `quick_test.json` for
    `pdf_url` and `cookie` and attempts to fetch the PDF and return it.
    """
    cfg_path = os.path.join(os.path.dirname(__file__), 'quick_test.json')
    if not os.path.exists(cfg_path):
        return jsonify({'error': 'quick_test.json not found'}), 404
    try:
        with open(cfg_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    except Exception as e:
        return jsonify({'error': 'failed to read quick_test.json', 'detail': str(e)}), 500

    url = cfg.get('pdf_url')
    cookie = cfg.get('cookie')
    if not url:
        return jsonify({'error': 'pdf_url missing in quick_test.json'}), 400

    headers = {'User-Agent': 'Raccoglitore/1.0'}
    if cookie:
        if '=' not in cookie:
            cookie = 'JSESSIONID=' + cookie
        headers['Cookie'] = cookie

    try:
        r = requests.get(url, headers=headers, timeout=15, stream=True)
    except Exception as e:
        return jsonify({'error': 'request failed', 'detail': str(e)}), 502

    if r.status_code != 200:
        return jsonify({'error': 'upstream returned error', 'status_code': r.status_code}), 502

    content_type = r.headers.get('Content-Type', 'application/octet-stream')
    data_bytes = r.content
    out = make_response(data_bytes)
    out.headers.set('Content-Type', content_type)
    out.headers.set('Content-Disposition', 'inline; filename="quick_test.pdf"')
    return out


@app.route('/api/fetch_pdf_local', methods=['POST'])
def fetch_pdf_local():
    """Fetch a PDF from the local drawings directory.

    Expects JSON: { code: 'TT30001' }
    Directory layout: BASE_DIR / PREFISSO / CODICE / CODICE.pdf
    Example: H:\\96-GESTIONE_STUDI\\DISEGNI\\TT30\\TT30001\\TT30001.pdf
    """
    data = request.json or {}
    code = data.get('code')
    if not code:
        return jsonify({'error': 'code required'}), 400

    # Normalizza il code in maiuscolo
    code = code.upper()
    
    BASE_DIR = os.environ.get('DRAWINGS_DIR', r'H:\96-GESTIONE_STUDI\DISEGNI')

    def find_pdf():
        # Prova a trovare il prefisso controllando quale cartella in DISEGNI corrisponde al codice
        # Prova in ordine di lunghezza decrescente (5 char, 4 char, 3 char, 2 char)
        prefisso = None
        
        for prefix_len in [5, 4, 3, 2]:
            test_prefix = code[:prefix_len]
            test_path = os.path.join(BASE_DIR, test_prefix)
            if os.path.isdir(test_path):
                prefisso = test_prefix
                print(f"DEBUG: Trovato prefisso {prefisso} (lunghezza {prefix_len})")
                break
        
        if not prefisso:
            # Fallback: estrai solo lettere iniziali
            prefisso_match = re.match(r'([A-Z]+)', code)
            if prefisso_match:
                prefisso = prefisso_match.group(1)
                print(f"DEBUG: Prefisso estratto da lettere: {prefisso}")
            else:
                return None, f'Prefisso non trovato nel codice: {code}'
        
        # Cerca SOLO in: BASE_DIR / PREFISSO / CODICE / CODICE.pdf (o .PDF)
        target_dir = os.path.join(BASE_DIR, prefisso, code)
        
        print(f"DEBUG: Cercando PDF per codice={code}, prefisso={prefisso}")
        print(f"DEBUG: Cercando in: {target_dir}")
        
        # Prova sia .pdf che .PDF
        for ext in ['.pdf', '.PDF']:
            pdf_path = os.path.join(target_dir, code + ext)
            print(f"DEBUG: Verificando {pdf_path} - Esiste: {os.path.isfile(pdf_path)}")
            if os.path.isfile(pdf_path):
                print(f"DEBUG: Trovato! {pdf_path}")
                return pdf_path, None
        
        # Se il file esatto non trovato, prova qualsiasi PDF nella cartella
        if os.path.isdir(target_dir):
            print(f"DEBUG: Cartella {target_dir} esiste, cercando qualsiasi PDF dentro...")
            try:
                for fn in os.listdir(target_dir):
                    if fn.lower().endswith('.pdf'):
                        full_path = os.path.join(target_dir, fn)
                        print(f"DEBUG: Trovato PDF alternativo: {full_path}")
                        return full_path, None
            except Exception as e:
                print(f"DEBUG: Errore listando cartella: {e}")
        
        # Se non trovato, ritorna errore (SENZA cercare globalmente)
        print(f"DEBUG: PDF non trovato in {target_dir}")
        return None, f'PDF non trovato in {target_dir}'

    pdf_path, error = find_pdf()
    if error or not pdf_path:
        error_msg = error or 'PDF non trovato'
        print(f"DEBUG: Errore - {error_msg}")
        return jsonify({'error': error_msg, 'searched_for': code}), 404

    try:
        print(f"DEBUG: Inviando file: {pdf_path}")
        return send_file(pdf_path, mimetype='application/pdf', as_attachment=False, download_name=os.path.basename(pdf_path))
    except Exception as e:
        print(f"DEBUG: Exception send_file: {e}")
        return jsonify({'error': 'failed to send file', 'detail': str(e)}), 500


@app.route('/api/init_drawings', methods=['POST'])
def init_drawings():
    """Create folder structure under DRAWINGS_DIR for families and sequences.

    Optional JSON input: { base_dir: 'H:\\path\\to\\DISEGNI' }
    Returns JSON with created directories and any errors.
    """
    data = request.json or {}
    base_dir = data.get('base_dir') or os.environ.get('DRAWINGS_DIR') or r'H:\96-GESTIONE_STUDI\DISEGNI'

    results = {'created': [], 'existing': [], 'errors': []}

    try:
        families = loader.get_families()
    except Exception as e:
        return jsonify({'error': 'failed to read families', 'detail': str(e)}), 500

    def sanitize(name):
        # simple sanitize for filesystem
        return ''.join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()

    for fam in families:
        fam_name = fam.get('family_name') or fam.get('family_code') or fam.get('family_id') or 'Unknown'
        fam_name_s = sanitize(fam_name)
        fam_dir = os.path.join(base_dir, fam_name_s)
        try:
            os.makedirs(fam_dir, exist_ok=True)
            results['existing' if os.path.exists(fam_dir) else 'created'].append(fam_dir)
        except Exception as e:
            results['errors'].append({'path': fam_dir, 'detail': str(e)})

        # create subfolders for sequences
        try:
            seqs = loader.get_sequences_for_family(fam.get('family_code') or fam.get('family_id') or fam_name)
        except Exception:
            seqs = []
        for s in seqs:
            seq_code = s.get('sequence_id') or s.get('codice') or ''
            # extract numeric suffix if present
            import re as _re
            m = _re.search(r"(\d+)", seq_code)
            if m:
                num = m.group(1).lstrip('0') or m.group(1)
                subname = f"{fam_name_s} {num.zfill(3)}"
            else:
                subname = f"{fam_name_s} {sanitize(seq_code)}"
            subdir = os.path.join(fam_dir, subname)
            try:
                os.makedirs(subdir, exist_ok=True)
                results['existing' if os.path.exists(subdir) else 'created'].append(subdir)
            except Exception as e:
                results['errors'].append({'path': subdir, 'detail': str(e)})

    return jsonify(results)


@app.route('/api/replay_curl', methods=['POST'])
def replay_curl():
    """Accept a cURL command (as copied from browser DevTools -> Copy as cURL)
    and replay it via requests. Returns the response bytes and Content-Type.

    JSON input: { curl: "curl ..." }
    """
    data = request.json or {}
    curl = data.get('curl')
    if not curl:
        return jsonify({'error': 'curl field required'}), 400

    # naive parsing using shlex to split the cURL command into tokens
    try:
        parts = shlex.split(curl)
    except Exception as e:
        return jsonify({'error': 'failed to parse curl', 'detail': str(e)}), 400

    # find URL (last token that looks like http)
    url = None
    method = 'GET'
    headers = {}
    data_body = None
    for i, tok in enumerate(parts):
        if tok.upper() == 'CURL':
            continue
        if tok == '-X' and i+1 < len(parts):
            method = parts[i+1].upper()
        if tok.startswith('-H') or tok == '-H':
            # handle both -H 'Header: value' and -HHeader
            if tok == '-H' and i+1 < len(parts):
                h = parts[i+1]
            else:
                h = tok[2:]
            if ':' in h:
                k, v = h.split(':',1)
                headers[k.strip()] = v.strip()
        if tok.startswith('--data') or tok.startswith('-d'):
            # data may be in next token or appended
            if tok in ('--data','--data-raw','-d') and i+1 < len(parts):
                data_body = parts[i+1]
            else:
                # --data='...'
                m = re.match(r"--data(?:-raw)?=(.*)", tok)
                if m:
                    data_body = m.group(1)
        # crude URL detection
        if tok.startswith('http://') or tok.startswith('https://'):
            url = tok

    if not url:
        # try last token
        last = parts[-1]
        if last.startswith('http://') or last.startswith('https://'):
            url = last

    if not url:
        return jsonify({'error': 'could not find URL in curl command'}), 400

    # if Cookie header present, keep it; otherwise user may have included -H 'Cookie: ...'
    try:
        sess = requests.Session()
        req_kwargs = {'headers': headers, 'timeout': 30, 'stream': True}
        if data_body is not None:
            # choose method
            if method == 'GET':
                method = 'POST'
            req = sess.request(method, url, data=data_body, **req_kwargs)
        else:
            req = sess.request(method, url, **req_kwargs)
    except Exception as e:
        return jsonify({'error': 'request failed', 'detail': str(e)}), 502

    if req.status_code != 200:
        return jsonify({'error': 'upstream returned error', 'status_code': req.status_code}), 502

    content_type = req.headers.get('Content-Type','application/octet-stream')
    content = req.content
    resp = make_response(content)
    resp.headers.set('Content-Type', content_type)
    resp.headers.set('Content-Disposition', 'inline; filename="replay_result"')
    return resp


@app.route('/api/fetch_pdf_selenium', methods=['POST'])
def fetch_pdf_selenium():
    # Selenium-based automation removed. Use local filesystem for PDFs.
    return jsonify({'error': 'selenium automation removed, use /api/fetch_pdf_local'}), 410


@app.route('/api/run_ide', methods=['POST'])
def run_ide():
    # removed: no local IDE runner exposed
    return jsonify({'error': 'endpoint removed'}), 410


@app.route('/api/credentials', methods=['GET', 'POST', 'DELETE'])
def credentials():
    """GET: return stored username (not password) and remember flag.
       POST: save { username, password, remember }
       DELETE: remove stored credentials
    """
    creds_path = os.path.join(os.path.dirname(__file__), 'stored_credentials.json')
    if request.method == 'GET':
        if not os.path.exists(creds_path):
            return jsonify({'stored': False}), 200
        try:
            with open(creds_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # do not return password unless explicitly requested (not implemented)
            return jsonify({'stored': True, 'username': data.get('username')}), 200
        except Exception as e:
            return jsonify({'error': 'failed to read credentials', 'detail': str(e)}), 500

    if request.method == 'POST':
        data = request.json or {}
        username = data.get('username')
        password = data.get('password')
        remember = data.get('remember')
        if not username or not password:
            return jsonify({'error': 'username and password required'}), 400
        if remember:
            try:
                with open(creds_path, 'w', encoding='utf-8') as f:
                    json.dump({'username': username, 'password': password}, f)
            except Exception as e:
                return jsonify({'error': 'failed to save credentials', 'detail': str(e)}), 500
        return jsonify({'status': 'saved' if remember else 'not_saved'}), 200

    # DELETE
    try:
        if os.path.exists(creds_path):
            os.remove(creds_path)
        return jsonify({'status': 'deleted'}), 200
    except Exception as e:
        return jsonify({'error': 'failed to delete', 'detail': str(e)}), 500


if __name__ == '__main__':
    # Listen on all network interfaces (0.0.0.0) on port 8000 to allow access from other PCs
    # Avoid port 5000 which may conflict with Windows Backup Manager
    app.run(host='0.0.0.0', port=8000, debug=False)
