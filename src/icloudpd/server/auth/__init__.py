from flask import Blueprint, render_template, request, make_response, redirect, url_for, jsonify

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

# Global reference to status_exchange - this is a hack, better to pass it properly
_status_exchange = None

def set_status_exchange(se):
    global _status_exchange
    _status_exchange = se

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        apple_id = request.form.get('apple_id')
        password = request.form.get('password')
        remember = request.form.get('remember')
        # Set the credentials in status_exchange
        if _status_exchange:
            _status_exchange.set_credentials(apple_id, password)
            # Trigger authentication
            # This would normally be handled by the CLI flow, but for web UI, we need to simulate
            return redirect(url_for('auth.mfa'))  # Assume MFA is needed
        return render_template('login.html', error="Authentication system not available")
    return render_template('login.html')

@auth_bp.route('/mfa', methods=['GET', 'POST'])
def mfa():
    if request.method == 'POST':
        code = request.form.get('code')
        if _status_exchange and code:
            if _status_exchange.set_payload(code):
                return redirect(url_for('index'))
        return render_template('mfa.html', error="Invalid code")
    return render_template('mfa.html')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    if _status_exchange:
        _status_exchange.logout()
    return redirect(url_for('auth.login'))

@auth_bp.route('/status')
def auth_status():
    if _status_exchange:
        status = _status_exchange.get_status()
        return jsonify({"authenticated": status != "NEED_PASSWORD", "status": status})
    return jsonify({"authenticated": False, "status": "unknown"})