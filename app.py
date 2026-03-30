from flask import Flask, render_template, request, jsonify
import subprocess
import os
import sys

app = Flask(__name__)
app.secret_key = 'sms-spam-secret'

active_processes = {}

@app.route('/')
def main_page():
    return render_template('sms_spammer.html')

@app.route('/api/sms-spam/start', methods=['POST'])
def start_sms_spam():
    """Background execution of SMS Spam tool (spamsms.py)"""
    data = request.json
    phone = data.get('phone')
    count = data.get('count', 1)
    
    if not phone:
        return jsonify({"success": False, "message": "Thiếu số điện thoại"})
        
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'spamsms.py')
        flags = 0x00000010 if os.name == 'nt' else 0
        if os.name == 'nt':
            process = subprocess.Popen([sys.executable, script_path, str(phone), str(count)], creationflags=flags)
        else:
            process = subprocess.Popen([sys.executable, script_path, str(phone), str(count)])
            
        active_processes[phone] = process
        
        return jsonify({"success": True, "message": "SMS Attack initiated successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/sms-spam/stop', methods=['POST'])
def stop_sms_spam():
    phone = request.json.get('phone')
    if phone in active_processes:
        try:
            active_processes[phone].terminate()
            del active_processes[phone]
            return jsonify({"success": True, "message": "Đã chặn cuộc tấn công SMS thành công!"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
    return jsonify({"success": False, "message": "Không tìm thấy tiến trình trên số này."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
