from flask import Flask, request, jsonify, render_template
import requests
import json
import hidden

app = Flask(__name__)
hiddeninfo = hidden.hiden_info() #private data make a class similar to this
# Update this to your Jetson's IP address
JETSON_IP = hiddeninfo.jetson_ip
JETSON_PORT = hiddeninfo.jetson_port

flight_path = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_mission', methods=['POST'])
def upload_mission():
    global flight_path
    data = request.json
    flight_path = data.get("waypoints", [])
    print("Received flight path:", flight_path)
    
    # Forward mission to Jetson
    try:
        jetson_response = requests.post(f"http://{JETSON_IP}:{JETSON_PORT}/receive_mission", 
                                      json=data,
                                      timeout=5)
        jetson_data = jetson_response.json()
        return jsonify({
            "status": "success", 
            "waypoints": flight_path,
            "jetson_response": jetson_data
        })
    except Exception as e:
        return jsonify({
            "status": "partial_success", 
            "message": f"Saved on server but failed to send to Jetson: {str(e)}",
            "waypoints": flight_path
        })

@app.route('/get_mission', methods=['GET'])
def get_mission():
    return jsonify({"waypoints": flight_path})

@app.route('/mission_feedback', methods=['POST'])
def mission_feedback():
    # Receive feedback from Jetson
    feedback = request.json
    print("Received feedback from Jetson:", feedback)
    return jsonify({"status": "received"})

@app.route('/jetson_status', methods=['GET'])
def jetson_status():
    try:
        response = requests.get(f"http://{JETSON_IP}:{JETSON_PORT}/drone_info", timeout=5)
        return response.json()
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to contact Jetson: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)