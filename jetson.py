#!/usr/bin/env python3

import asyncio
import json
import requests
from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan)
from flask import Flask, request, jsonify

app = Flask(__name__)

# Store the received mission data
mission_data = None

# MAVsdk connection parameters
drone_address = "udp://:14540"  # Update with your drone's connection string if different

async def setup_drone():
    """Connect to the drone and return the drone object."""
    drone = System()
    await drone.connect(system_address=drone_address)
    
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone connected!")
            break

    return drone

async def get_drone_info(drone):
    """Get basic drone information."""
    async for health in drone.telemetry.health():
        is_ready = health.is_armable
        print(f"Drone is {'ready' if is_ready else 'not ready'} to arm")
        break
    
    return {
        "is_ready": is_ready,
        "battery": await get_battery_info(drone),
        "gps": await get_gps_info(drone)
    }

async def get_battery_info(drone):
    """Get battery information."""
    async for battery in drone.telemetry.battery():
        return {
            "voltage_v": battery.voltage_v,
            "remaining_percent": battery.remaining_percent
        }

async def get_gps_info(drone):
    """Get GPS information."""
    async for position in drone.telemetry.position():
        return {
            "latitude_deg": position.latitude_deg,
            "longitude_deg": position.longitude_deg,
            "absolute_altitude_m": position.absolute_altitude_m,
            "relative_altitude_m": position.relative_altitude_m
        }

async def upload_mission(drone, waypoints):
    """Create and upload a mission to the drone."""
    mission_items = []
    
    for i, wp in enumerate(waypoints):
        mission_items.append(MissionItem(
            wp['lat'],
            wp['lng'],
            float(wp['alt']),
            10.0,  # speed in m/s
            True,  # is_fly_through
            float('nan'),  # gimbal_pitch_deg
            float('nan'),  # gimbal_yaw_deg
            MissionItem.CameraAction.NONE,
            float('nan'),  # loiter_time_s
            float('nan'),  # camera_photo_interval_s
            float(1.0),    # acceptance_radius_m
            float('nan'),  # yaw_deg
            float('nan')   # camera_photo_distance_m
        ))
    
    mission_plan = MissionPlan(mission_items)
    
    await drone.mission.clear_mission()
    print("Mission cleared")
    
    await drone.mission.upload_mission(mission_plan)
    print("Mission uploaded")
    
    return {"status": "Mission uploaded successfully", "items": len(mission_items)}

@app.route('/receive_mission', methods=['POST'])
def receive_mission():
    global mission_data
    mission_data = request.json
    print("Received mission data:", json.dumps(mission_data, indent=2))
    
    # Process the mission data with MAVsdk in a separate async task
    asyncio.create_task(process_mission(mission_data))
    
    return jsonify({"status": "success", "message": "Mission received by Jetson"})

@app.route('/mission_status', methods=['GET'])
def mission_status():
    if mission_data:
        return jsonify({
            "status": "Mission loaded",
            "waypoints": len(mission_data.get("waypoints", [])),
            "mission_data": mission_data
        })
    else:
        return jsonify({"status": "No mission loaded"})

@app.route('/drone_info', methods=['GET'])
def get_drone_status():
    # This will be handled by the event loop
    future = asyncio.run_coroutine_threadsafe(get_drone_info_handler(), loop)
    return jsonify(future.result())

async def get_drone_info_handler():
    drone = await setup_drone()
    info = await get_drone_info(drone)
    return info

async def process_mission(mission_data):
    """Process the received mission data and upload it to the drone."""
    try:
        drone = await setup_drone()
        waypoints = mission_data.get("waypoints", [])
        result = await upload_mission(drone, waypoints)
        print("Mission processed:", result)
        
        # You could send a confirmation to the web server if needed
        try:
            requests.post("http://web-server-ip:5000/mission_feedback", 
                         json={"status": "success", "message": "Mission uploaded to drone"})
        except Exception as e:
            print(f"Failed to send feedback: {e}")
            
    except Exception as e:
        print(f"Error processing mission: {e}")

if __name__ == '__main__':
    # Create an event loop that will run in a separate thread
    loop = asyncio.new_event_loop()
    
    # Start the Flask app in the main thread
    print("Starting Jetson mission receiver on port 5001...")
    app.run(host='0.0.0.0', port=5001)