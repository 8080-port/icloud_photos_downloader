from flask import Blueprint, jsonify
import threading
import time

download_bp = Blueprint('download', __name__)

# Global state for download
download_state = {
    "status": "idle",
    "current_file": None,
    "progress": 0,
    "speed": 0,
    "elapsed": 0,
    "remaining": 0,
    "files_count": {"downloaded": 0, "total": 0}
}

logs = []

def simulate_download():
    global download_state, logs
    download_state["status"] = "syncing"
    download_state["files_count"]["total"] = 100
    start_time = time.time()
    for i in range(101):
        download_state["progress"] = i
        download_state["files_count"]["downloaded"] = i
        download_state["elapsed"] = int(time.time() - start_time)
        download_state["remaining"] = int((100 - i) * 0.1)
        download_state["speed"] = 1024 * 1024  # 1MB/s
        logs.append(f"Downloaded file_{i}.jpg (1MB)")
        if len(logs) > 1000:
            logs.pop(0)
        time.sleep(0.1)
    download_state["status"] = "complete"

download_thread = None

@download_bp.route('/api/status/current', methods=['GET'])
def get_current_status():
    html = f"""
    <div class="card">
        <div class="card-header">
            <h5>Status: {download_state["status"].title()}</h5>
        </div>
        <div class="card-body">
            <p>Current File: {download_state["current_file"] or "None"}</p>
            <div class="progress mb-3">
                <div class="progress-bar" style="width: {download_state["progress"]}%;"></div>
            </div>
            <p>Files Downloaded: {download_state["files_count"]["downloaded"]} / {download_state["files_count"]["total"]}</p>
            <p>Speed: {download_state["speed"] / (1024*1024):.1f} MB/s</p>
            <p>Elapsed: {download_state["elapsed"]}s | Remaining: {download_state["remaining"]}s</p>
        </div>
    </div>
    <div class="mt-3">
        <button class="btn btn-success" hx-post="/api/control/start" hx-swap="none">Start</button>
        <button class="btn btn-warning" hx-post="/api/control/pause" hx-swap="none">Pause</button>
        <button class="btn btn-info" hx-post="/api/control/resume" hx-swap="none">Resume</button>
        <button class="btn btn-danger" hx-post="/api/control/cancel" hx-swap="none">Cancel</button>
        <button class="btn btn-secondary" hx-post="/api/control/retry-errors" hx-swap="none">Retry Errors</button>
    </div>
    """
    return html

@download_bp.route('/api/control/start', methods=['POST'])
def start_download():
    global download_thread
    if download_state["status"] == "idle":
        download_thread = threading.Thread(target=simulate_download)
        download_thread.start()
    return jsonify({"status": "started"})

@download_bp.route('/api/control/pause', methods=['POST'])
def pause_download():
    if download_state["status"] == "syncing":
        download_state["status"] = "paused"
    return jsonify({"status": "paused"})

@download_bp.route('/api/control/resume', methods=['POST'])
def resume_download():
    if download_state["status"] == "paused":
        download_state["status"] = "syncing"
    return jsonify({"status": "resumed"})

@download_bp.route('/api/control/cancel', methods=['POST'])
def cancel_download():
    download_state["status"] = "idle"
    download_state["progress"] = 0
    return jsonify({"status": "cancelled"})

@download_bp.route('/api/control/retry-errors', methods=['POST'])
def retry_errors():
    # TODO: Retry failed files
    return jsonify({"status": "retrying"})

@download_bp.route('/api/logs/current', methods=['GET'])
def get_current_logs():
    html = '<div class="card"><div class="card-body"><div style="height: 300px; overflow-y: auto;">'
    for log in logs[-100:]:
        html += f'<p>{log}</p>'
    html += '</div></div></div>'
    return html

@download_bp.route('/api/logs/history', methods=['GET'])
def get_history_logs():
    # TODO: Get past sync runs
    return jsonify([])

@download_bp.route('/api/stats/current', methods=['GET'])
def get_current_stats():
    stats = {
        "total_processed": download_state["files_count"]["downloaded"],
        "successful": download_state["files_count"]["downloaded"],
        "skipped": 0,
        "errors": 0,
        "total_size": download_state["files_count"]["downloaded"] * 1024 * 1024,
        "avg_size": 1024 * 1024 if download_state["files_count"]["downloaded"] > 0 else 0
    }
    html = f'''
    <div class="row">
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">{stats["total_processed"]}</h5>
                    <p class="card-text">Total Processed</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">{stats["successful"]}</h5>
                    <p class="card-text">Successful</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">{stats["skipped"]}</h5>
                    <p class="card-text">Skipped</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">{stats["errors"]}</h5>
                    <p class="card-text">Errors</p>
                </div>
            </div>
        </div>
    </div>
    '''
    return html

@download_bp.route('/api/logs/export', methods=['POST'])
def export_logs():
    # TODO: Export logs as file
    return jsonify({"status": "exported"})