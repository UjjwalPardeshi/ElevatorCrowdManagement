from flask import Flask, render_template, request, redirect, url_for, jsonify
import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Firebase
cred = credentials.Certificate(os.getenv("FIREBASE_KEY_PATH"))
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv("DATABASE_URL")
})

app = Flask(__name__)

# Admin interface to list cameras and update their status
@app.route('/')
def index():
    # Retrieve all cameras and their `isactive` status
    ref = db.reference('cameras')
    cameras = ref.get()  # Get the cameras data from Firebase
    return render_template('index.html', cameras=cameras)

@app.route('/update_status', methods=['POST'])
def update_status():
    camera_id = request.form['camera_id']
    isactive = request.form.get('isactive') == 'on'  # Check if the checkbox is ticked
    ref = db.reference(f'cameras/{camera_id}')
    ref.update({'isactive': isactive})
    return redirect(url_for('index'))

# JSON-based API for mobile app usage
@app.route('/api/update_status', methods=['POST'])
def api_update_status():
    data = request.json
    camera_id = data.get('camera_id')
    isactive = data.get('isactive', True)
    
    if not camera_id:
        return jsonify({"error": "Camera ID is required"}), 400
    
    ref = db.reference(f'cameras/{camera_id}')
    ref.update({'isactive': isactive})
    
    return jsonify({"message": f"Camera {camera_id} updated successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

