import os
import re
from datetime import datetime
from flask import Blueprint, jsonify, render_template, request, send_file

BASE_SEARCH_DIR = r"D:\home\Jobs Malvicini\JOBS\ARCHIVIO-JOBS-PARTICOLARI\test_di_esportazione\exp"
MAX_RESULTS = 250

main_bp = Blueprint('main', __name__)


def _format_file_record(path, base_dir):
    stat = os.stat(path)
    relative_path = os.path.relpath(path, base_dir).replace('\\', '/')
    return {
        'name': os.path.basename(path),
        'relative_path': relative_path,
        'folder': os.path.dirname(relative_path).replace('\\', '/'),
        'size_bytes': stat.st_size,
        'size_label': f"{stat.st_size / 1024:.1f} KB" if stat.st_size < 1024 * 1024 else f"{stat.st_size / 1024 / 1024:.1f} MB",
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        'download_url': f"/api/download?file={relative_path}"
    }


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/api/search')
def search_files():
    query = (request.args.get('code') or '').strip()
    if not query:
        return jsonify({'query': query, 'count': 0, 'files': []})

    if not os.path.isdir(BASE_SEARCH_DIR):
        return jsonify({'error': 'Base search directory not found', 'base_dir': BASE_SEARCH_DIR}), 500

    terms = [term for term in re.split(r'[\*\s]+', query.lower()) if term]
    if not terms:
        return jsonify({'query': query, 'count': 0, 'files': []})

    results = []
    for root, _, files in os.walk(BASE_SEARCH_DIR):
        normalized_root = root.lower()
        for file_name in files:
            normalized_name = file_name.lower()
            searchable = f"{normalized_root}/{normalized_name}"
            if all(term in searchable for term in terms):
                try:
                    path = os.path.join(root, file_name)
                    results.append(_format_file_record(path, BASE_SEARCH_DIR))
                except OSError:
                    continue
        if len(results) >= MAX_RESULTS:
            break

    results.sort(key=lambda item: item['modified'], reverse=True)
    return jsonify({'query': query, 'count': len(results), 'files': results[:MAX_RESULTS]})


@main_bp.route('/api/download')
def download_file():
    relative_path = (request.args.get('file') or '').strip()
    if not relative_path:
        return jsonify({'error': 'file parameter is required'}), 400

    normalized = relative_path.replace('/', os.sep).replace('\\', os.sep)
    candidate_path = os.path.normpath(os.path.join(BASE_SEARCH_DIR, normalized))
    base_norm = os.path.normpath(BASE_SEARCH_DIR)
    if not candidate_path.startswith(base_norm + os.sep) and candidate_path != base_norm:
        return jsonify({'error': 'invalid path'}), 400

    if not os.path.isfile(candidate_path):
        return jsonify({'error': 'file not found', 'path': relative_path}), 404

    return send_file(candidate_path, as_attachment=True, download_name=os.path.basename(candidate_path))
