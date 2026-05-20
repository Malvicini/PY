import json
import os
import re
import shlex
from typing import Dict, Optional, Tuple

import requests
from flask import make_response, jsonify


def build_http_headers(cookie: Optional[str] = None) -> Dict[str, str]:
    headers = {'User-Agent': 'Raccoglitore/1.0'}
    if cookie:
        if '=' not in cookie:
            cookie = 'JSESSIONID=' + cookie
        headers['Cookie'] = cookie
    return headers


def fetch_url_and_respond(url: str, headers: Dict[str, str], filename: str):
    try:
        r = requests.get(url, headers=headers, timeout=15, stream=True)
    except Exception as exc:
        return jsonify({'error': 'request failed', 'detail': str(exc)}), 502

    if r.status_code != 200:
        return jsonify({'error': 'upstream returned error', 'status_code': r.status_code}), 502

    content_type = r.headers.get('Content-Type', 'application/octet-stream')
    content = r.content
    response = make_response(content)
    response.headers.set('Content-Type', content_type)
    response.headers.set('Content-Disposition', f'inline; filename="{filename}"')
    return response


def parse_curl_command(curl: str) -> Tuple[Optional[str], str, Dict[str, str], Optional[str]]:
    try:
        tokens = shlex.split(curl)
    except Exception:
        return None, 'GET', {}, None

    url = None
    method = 'GET'
    headers: Dict[str, str] = {}
    data_body = None

    for idx, token in enumerate(tokens):
        if token.upper() == 'CURL':
            continue
        if token == '-X' and idx + 1 < len(tokens):
            method = tokens[idx + 1].upper()
        if token.startswith('-H') or token == '-H':
            header_value = None
            if token == '-H' and idx + 1 < len(tokens):
                header_value = tokens[idx + 1]
            else:
                header_value = token[2:]
            if header_value and ':' in header_value:
                key, value = header_value.split(':', 1)
                headers[key.strip()] = value.strip()
        if token in ('--data', '--data-raw', '-d') and idx + 1 < len(tokens):
            data_body = tokens[idx + 1]
        if token.startswith('--data') and '=' in token:
            match = re.match(r'--data(?:-raw)?=(.*)', token)
            if match:
                data_body = match.group(1)
        if token.startswith('http://') or token.startswith('https://'):
            url = token

    if not url and tokens:
        last = tokens[-1]
        if last.startswith(('http://', 'https://')):
            url = last

    return url, method, headers, data_body


def sanitize_filesystem_name(name: str) -> str:
    return ''.join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()


def load_json_file(path: str):
    if not os.path.exists(path):
        return None, f'file not found: {path}'
    try:
        with open(path, 'r', encoding='utf-8') as handler:
            return json.load(handler), None
    except Exception as exc:
        return None, str(exc)
