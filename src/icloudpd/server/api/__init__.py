from flask import Blueprint, jsonify, request
import os

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/albums', methods=['GET'])
def get_albums():
    # TODO: Fetch available albums from iCloud
    return jsonify([])

@api_bp.route('/api/filesystem/browse', methods=['GET'])
def browse_filesystem():
    path = request.args.get('path', '/')
    try:
        items = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            items.append({
                "name": item,
                "path": full_path,
                "is_dir": os.path.isdir(full_path),
                "size": os.path.getsize(full_path) if os.path.isfile(full_path) else 0
            })
        return jsonify({"path": path, "items": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/api/filesystem/validate', methods=['POST'])
def validate_path():
    data = request.json
    path = data.get('path')
    if not path:
        return jsonify({"valid": False, "error": "No path provided"})
    exists = os.path.exists(path)
    is_dir = os.path.isdir(path) if exists else False
    writable = os.access(path, os.W_OK) if exists else False
    return jsonify({
        "valid": True,
        "exists": exists,
        "is_dir": is_dir,
        "writable": writable
    })

@api_bp.route('/api/filesystem/create', methods=['POST'])
def create_directory():
    data = request.json
    path = data.get('path')
    try:
        os.makedirs(path, exist_ok=True)
        return jsonify({"status": "created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/api/filesystem/disk-space', methods=['GET'])
def get_disk_space():
    path = request.args.get('path', '/')
    try:
        stat = os.statvfs(path)
        total = stat.f_bsize * stat.f_blocks
        available = stat.f_bsize * stat.f_bavail
        return jsonify({
            "total": total,
            "available": available,
            "used": total - available
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/api/config/quick-paths', methods=['GET'])
def get_quick_paths():
    # TODO: Get predefined shortcuts
    return jsonify([
        {"name": "Home", "path": os.path.expanduser("~")},
        {"name": "Desktop", "path": os.path.join(os.path.expanduser("~"), "Desktop")},
        {"name": "Downloads", "path": os.path.join(os.path.expanduser("~"), "Downloads")},
        {"name": "Documents", "path": os.path.join(os.path.expanduser("~"), "Documents")}
    ])

@api_bp.route('/api/config/quick-paths', methods=['POST'])
def add_quick_path():
    # TODO: Add custom shortcut
    return jsonify({"status": "added"})