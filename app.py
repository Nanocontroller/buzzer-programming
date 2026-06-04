import json
import os
from flask import Flask, render_template, request, jsonify, redirect
from datetime import datetime
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
SHELLY_SERVER = "https://shelly-16-eu.shelly.cloud" # Replace with your server
AUTH_KEY = "MjdkZWN1aWQBF6065DF985253E54EFBEF5E6AECBC3F5A1BC49E10A88D6DFB9F2F0CCB6D3E5E6328E5B5DCEFDB7E"                           # Replace with your key
DEVICE_ID = "3494547a181b"                         # Replace with your device ID
ADMIN_PASSWORD = "change-me-123" 
DATA_FILE = "guests.json"

# FIX FOR DEPLOYMENT: This ensures the file is saved in your main folder
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(THIS_FOLDER, "guests.json")

def load_guests():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_guests(guests):
    with open(DATA_FILE, 'w') as f:
        json.dump(guests, f)

# Logic to check if the current time is within the guest's window
def is_guest_valid(guest_data):
    now = datetime.now()
    start = datetime.strptime(guest_data['start'], "%Y-%m-%d %H:%M")
    end = datetime.strptime(guest_data['end'], "%Y-%m-%d %H:%M")
    return start <= now <= end

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD:
        return "Unauthorized", 401
    guests = load_guests()

    if request.method == 'POST':
        code = request.form.get('code')
        start = request.form.get('start').replace('T', ' ')
        end = request.form.get('end').replace('T', ' ')
        
        guests[code] = {"start": start, "end": end}
        save_guests(guests)
        return redirect(f'/admin?pw={ADMIN_PASSWORD}')

    return render_template('admin.html', guests=guests)

@app.route('/unlock/<code>')
def index(code):
    guests = load_guests()
    
    if code not in guests:
        return render_template('error.html', 
            title="Link Not Found", 
            message="We couldn't find an access record for this link. Please double-check the URL."), 404

    # Time checks
    now = datetime.now()
    start = datetime.strptime(guests[code]['start'], "%Y-%m-%d %H:%M")
    end = datetime.strptime(guests[code]['end'], "%Y-%m-%d %H:%M")

    if now < start:
        return render_template('error.html', 
            title="Too Early!", 
            message=f"Your access doesn't start until {guests[code]['start']}. We look forward to seeing you then!"), 403
            
    if now > end:
        return render_template('error.html', 
            title="Access Expired", 
            message="This link expired at " + guests[code]['end'] + ". We hope you enjoyed your stay!"), 403

    # If all is well, show the actual buzzer button
    return render_template('index.html', guest_code=code)

@app.route('/trigger-buzzer/<code>', methods=['POST'])
def trigger(code):
    guests = load_guests()
    if code in guests and is_guest_valid(guests[code]):
        url = f"{SHELLY_SERVER}/device/relay/control"
        data = {"id": DEVICE_ID, "auth_key": AUTH_KEY, "turn": "on", "timer": "3", "channel": "0"}
        resp = requests.post(url, data=data)
        if resp.status_code == 200 and '"isok":true' in resp.text:
            return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Expired or Invalid"}), 403

# route to delete guests
@app.route('/admin/delete/<code>')
def delete_guest(code):
    if request.args.get('pw') != ADMIN_PASSWORD:
        return "Unauthorized", 401
    
    guests = load_guests()
    if code in guests:
        del guests[code]
        save_guests(guests)
    
    # Redirect back to the admin page so the list refreshes
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

if __name__ == '__main__':
    app.run(debug=True)