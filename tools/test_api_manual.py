import requests
import json

# Test the API endpoints
base_url = "http://localhost:8000"

print("Testing FastAPI Chat API...")

# Test root endpoint
try:
    response = requests.get(f"{base_url}/")
    print(f"Root endpoint: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"Root endpoint error: {e}")

# Test create user
try:
    user_data = {"username": "TestUser"}
    response = requests.post(f"{base_url}/users", json=user_data)
    print(f"Create user: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"User created: {user}")
        
        # Test create room
        room_data = {"name": "TestRoom"}
        response = requests.post(f"{base_url}/rooms", json=room_data)
        print(f"Create room: {response.status_code}")
        if response.status_code == 200:
            room = response.json()
            print(f"Room created: {room}")
            
            # Test get rooms
            response = requests.get(f"{base_url}/rooms")
            print(f"Get rooms: {response.status_code}")
            if response.status_code == 200:
                rooms = response.json()
                print(f"Rooms: {rooms}")
        else:
            print(f"Create room failed: {response.text}")
    else:
        print(f"Create user failed: {response.text}")
except Exception as e:
    print(f"API test error: {e}")

print("API test complete.")
