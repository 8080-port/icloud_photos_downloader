from flask import Blueprint, jsonify, request
import json
import os

config_bp = Blueprint('config', __name__)

CONFIG_DIR = os.path.expanduser("~/.icloudpd_web")
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
PROFILES_DIR = os.path.join(CONFIG_DIR, "profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)

@config_bp.route('/api/config/schema', methods=['GET'])
def get_config_schema():
    schema = {
        "watch_interval": {"type": "number", "default": 3600, "min": 60, "max": 86400},
        "album": {"type": "string", "multiple": True},
        "folder_structure": {"type": "string", "default": "{:%Y/%m/%d}"},
        "sync_strategy": {"type": "string", "options": ["copy", "sync", "move"]},
        "keep_icloud_recent_days": {"type": "number", "min": 0},
        "size": {"type": "array", "options": ["original", "medium", "thumb", "adjusted", "alternative"]},
        "live_photo_size": {"type": "string", "options": ["original", "medium", "thumb"]},
        "recent": {"type": "number", "min": 1},
        "until_found": {"type": "number", "min": 1},
        "skip_photos": {"type": "boolean"},
        "skip_videos": {"type": "boolean"},
        "skip_live_photos": {"type": "boolean"},
        "align_raw": {"type": "string", "options": ["as-is", "original", "alternative"]},
        "file_match_policy": {"type": "string", "options": ["name-size-dedup-with-suffix", "name-id7"]},
        "skip_created_before": {"type": "datetime"},
        "skip_created_after": {"type": "datetime"},
        "auto_delete": {"type": "boolean"},
        "set_exif_datetime": {"type": "boolean"},
        "xmp_sidecar": {"type": "boolean"},
        "keep_unicode_in_filenames": {"type": "boolean"},
        "live_photo_mov_filename_policy": {"type": "string", "options": ["suffix", "original"]},
        "force_size": {"type": "boolean"},
        "dry_run": {"type": "boolean"},
        "only_print_filenames": {"type": "boolean"},
        "log_level": {"type": "string", "options": ["debug", "info", "error"]},
        "domain": {"type": "string", "options": ["com", "cn"]},
        "use_os_locale": {"type": "boolean"},
    }
    return jsonify(schema)

@config_bp.route('/api/config/current', methods=['GET'])
def get_current_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({})

@config_bp.route('/api/config/save', methods=['POST'])
def save_config():
    config = request.json
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    return jsonify({"status": "saved"})

@config_bp.route('/api/config/profiles', methods=['GET'])
def get_profiles():
    profiles = []
    for f in os.listdir(PROFILES_DIR):
        if f.endswith('.json'):
            profiles.append(f[:-5])
    return jsonify(profiles)

@config_bp.route('/api/config/profiles/<name>', methods=['POST'])
def load_profile(name):
    profile_file = os.path.join(PROFILES_DIR, f"{name}.json")
    if os.path.exists(profile_file):
        with open(profile_file, 'r') as f:
            config = json.load(f)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        return jsonify({"status": "loaded"})
    return jsonify({"error": "Profile not found"}), 404

@config_bp.route('/api/config/profiles/<name>', methods=['DELETE'])
def delete_profile(name):
    profile_file = os.path.join(PROFILES_DIR, f"{name}.json")
    if os.path.exists(profile_file):
        os.remove(profile_file)
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Profile not found"}), 404

@config_bp.route('/api/config/validate', methods=['POST'])
def validate_config():
    config = request.json
    # Basic validation
    errors = []
    if 'watch_interval' in config and not (60 <= config['watch_interval'] <= 86400):
        errors.append("watch_interval out of range")
    # Add more validations
    return jsonify({"valid": len(errors) == 0, "errors": errors})