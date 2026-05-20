import json
import os
import re

import requests
from flask import Blueprint, jsonify, make_response, render_template, request, send_file

from config import CREDENTIALS_FILE, DATA_FILE, DEFAULT_DRAWINGS_DIR, QUICK_TEST_FILE
from cache_manager import GroupsMachinesCache
from data_loader import DataLoader
from helpers import (
    build_http_headers,
    fetch_url_and_respond,
    load_json_file,
    parse_curl_command,
    sanitize_filesystem_name,
)
from pdf_finder import find_pdf_path

main_bp = Blueprint('main', __name__)

loader = DataLoader(DATA_FILE)
cache = GroupsMachinesCache()


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/api/families')
def families():
    families_data = loader.get_families()
    return jsonify(families_data)


@main_bp.route('/api/sequences')
def sequences():
    fam_code = request.args.get('family_code')
    if not fam_code:
        return jsonify({'error': 'family_code required'}), 400
    seqs = loader.get_sequences_for_family(fam_code)
    return jsonify(seqs)


@main_bp.route('/api/all_sequences')
def all_sequences():
    families_data = loader.get_families()
    all_seqs = []
    for fam in families_data:
        seqs = loader.get_sequences_for_family(fam['family_code'])
        for seq in seqs:
            seq['family_code'] = fam['family_code']
            all_seqs.append(seq)
    return jsonify(all_seqs)


@main_bp.route('/api/groups_machines')
def groups_machines():
    fam_code = request.args.get('family_code')
    seq_code = request.args.get('sequence_code')
    if not fam_code:
        return jsonify({'error': 'family_code required'}), 400
    groups_machines_data = loader.get_groups_machines_for_family(fam_code, seq_code)
    return jsonify(groups_machines_data)


@main_bp.route('/api/all_groups_machines')
def all_groups_machines():
    data = cache.get_cached_data(loader)
    return jsonify(data)


@main_bp.route('/api/fetch_pdf', methods=['POST'])
def fetch_pdf():
    return jsonify({'error': 'endpoint removed, use /api/fetch_pdf_local'}), 410


@main_bp.route('/api/proxy_pdf', methods=['POST'])
def proxy_pdf():
    data = request.json or {}
    url = data.get('url')
    if not url:
        return jsonify({'error': 'url required'}), 400
    cookie = data.get('cookie')
    headers = build_http_headers(cookie)
    return fetch_url_and_respond(url, headers, 'remote.pdf')


@main_bp.route('/api/run_quick_proxy', methods=['POST'])
def run_quick_proxy():
    if not QUICK_TEST_FILE.exists():
        return jsonify({'error': 'quick_test.json not found'}), 404
    cfg, error = load_json_file(str(QUICK_TEST_FILE))
    if error:
        return jsonify({'error': 'failed to read quick_test.json', 'detail': error}), 500
    url = cfg.get('pdf_url')
    if not url:
        return jsonify({'error': 'pdf_url missing in quick_test.json'}), 400
    cookie = cfg.get('cookie')
    headers = build_http_headers(cookie)
    return fetch_url_and_respond(url, headers, 'quick_test.pdf')


@main_bp.route('/api/fetch_pdf_local', methods=['POST'])
def fetch_pdf_local():
    data = request.json or {}
    code = data.get('code')
    if not code:
        return jsonify({'error': 'code required'}), 400

    pdf_path, error = find_pdf_path(code, DEFAULT_DRAWINGS_DIR)
    if error or not pdf_path:
        error_msg = error or 'PDF not found'
        print(f"DEBUG: Error - {error_msg}")
        return jsonify({'error': error_msg, 'searched_for': code}), 404

    try:
        print(f"DEBUG: Sending file: {pdf_path}")
        return send_file(pdf_path, mimetype='application/pdf', as_attachment=False, download_name=os.path.basename(pdf_path))
    except Exception as exc:
        print(f"DEBUG: Exception send_file: {exc}")
        return jsonify({'error': 'failed to send file', 'detail': str(exc)}), 500


@main_bp.route('/api/init_drawings', methods=['POST'])
def init_drawings():
    data = request.json or {}
    base_dir = data.get('base_dir') or DEFAULT_DRAWINGS_DIR
    results = {'created': [], 'existing': [], 'errors': []}

    try:
        families_data = loader.get_families()
    except Exception as exc:
        return jsonify({'error': 'failed to read families', 'detail': str(exc)}), 500

    for fam in families_data:
        fam_name = fam.get('family_name') or fam.get('family_code') or fam.get('family_id') or 'Unknown'
        fam_name_s = sanitize_filesystem_name(fam_name)
        fam_dir = os.path.join(base_dir, fam_name_s)
        try:
            os.makedirs(fam_dir, exist_ok=True)
            results['existing' if os.path.exists(fam_dir) else 'created'].append(fam_dir)
        except Exception as exc:
            results['errors'].append({'path': fam_dir, 'detail': str(exc)})

        try:
            seqs = loader.get_sequences_for_family(fam.get('family_code') or fam.get('family_id') or fam_name)
        except Exception:
            seqs = []

        for seq in seqs:
            seq_code = seq.get('sequence_id') or seq.get('codice') or ''
            subname = seq_code
            if isinstance(seq_code, str):
                import re as _re
                m = _re.search(r"(\d+)", seq_code)
                if m:
                    num = m.group(1).lstrip('0') or m.group(1)
                    subname = f"{fam_name_s} {num.zfill(3)}"
                else:
                    subname = f"{fam_name_s} {sanitize_filesystem_name(seq_code)}"
            else:
                subname = f"{fam_name_s}"
            subdir = os.path.join(fam_dir, subname)
            try:
                os.makedirs(subdir, exist_ok=True)
                results['existing' if os.path.exists(subdir) else 'created'].append(subdir)
            except Exception as exc:
                results['errors'].append({'path': subdir, 'detail': str(exc)})

    return jsonify(results)


@main_bp.route('/api/replay_curl', methods=['POST'])
def replay_curl():
    data = request.json or {}
    curl = data.get('curl')
    if not curl:
        return jsonify({'error': 'curl field required'}), 400

    url, method, headers, data_body = parse_curl_command(curl)
    if not url:
        return jsonify({'error': 'could not find URL in curl command'}), 400

    try:
        session = requests.Session()
        request_kwargs = {'headers': headers, 'timeout': 30, 'stream': True}
        if data_body is not None:
            if method == 'GET':
                method = 'POST'
            req = session.request(method, url, data=data_body, **request_kwargs)
        else:
            req = session.request(method, url, **request_kwargs)
    except Exception as exc:
        return jsonify({'error': 'request failed', 'detail': str(exc)}), 502

    if req.status_code != 200:
        return jsonify({'error': 'upstream returned error', 'status_code': req.status_code}), 502

    content_type = req.headers.get('Content-Type', 'application/octet-stream')
    response = make_response(req.content)
    response.headers.set('Content-Type', content_type)
    response.headers.set('Content-Disposition', 'inline; filename="replay_result"')
    return response


@main_bp.route('/api/fetch_pdf_selenium', methods=['POST'])
def fetch_pdf_selenium():
    return jsonify({'error': 'selenium automation removed, use /api/fetch_pdf_local'}), 410


@main_bp.route('/api/run_ide', methods=['POST'])
def run_ide():
    return jsonify({'error': 'endpoint removed'}), 410


@main_bp.route('/api/credentials', methods=['GET', 'POST', 'DELETE'])
def credentials():
    if request.method == 'GET':
        if not CREDENTIALS_FILE.exists():
            return jsonify({'stored': False}), 200
        try:
            with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as handler:
                data = json.load(handler)
            return jsonify({'stored': True, 'username': data.get('username')}), 200
        except Exception as exc:
            return jsonify({'error': 'failed to read credentials', 'detail': str(exc)}), 500

    if request.method == 'POST':
        data = request.json or {}
        username = data.get('username')
        password = data.get('password')
        remember = data.get('remember')
        if not username or not password:
            return jsonify({'error': 'username and password required'}), 400
        if remember:
            try:
                with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as handler:
                    json.dump({'username': username, 'password': password}, handler)
            except Exception as exc:
                return jsonify({'error': 'failed to save credentials', 'detail': str(exc)}), 500
        return jsonify({'status': 'saved' if remember else 'not_saved'}), 200

    try:
        if CREDENTIALS_FILE.exists():
            CREDENTIALS_FILE.unlink()
        return jsonify({'status': 'deleted'}), 200
    except Exception as exc:
        return jsonify({'error': 'failed to delete', 'detail': str(exc)}), 500
