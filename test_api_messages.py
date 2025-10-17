import requests
import json

BASE_URL = 'https://natural-presence-production.up.railway.app'

print("Testing API message retrieval...")

# Create user
user_response = requests.post(f'{BASE_URL}/users', json={'username': 'testuser_api'})
user = user_response.json()
print(f'Created user: {user}')

# Create room
room_response = requests.post(f'{BASE_URL}/rooms', json={'name': 'testroom_api'})
room = room_response.json()
print(f'Created room: {room}')

# Join room
join_response = requests.post(f'{BASE_URL}/rooms/{room["id"]}/join', json={'user_id': user["id"]})
print(f'Joined room: {join_response.status_code}')

# Get messages
messages_response = requests.get(f'{BASE_URL}/rooms/{room["id"]}/messages')
messages = messages_response.json()
print(f'Messages in room: {len(messages)}')

if messages:
    print("Sample message:")
    print(json.dumps(messages[0], indent=2))
else:
    print("No messages found")

print("API test complete")