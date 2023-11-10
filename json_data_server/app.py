import requests

# Define the URL of your JSON backend server
url = 'http://localhost:3000/posts'

# Define the data you want to write to the server as a Python dictionary
data_to_send = {
    "id": 12345,
    "title": "John Doe"
}

# Send a POST request to the server with the JSON data
response = requests.post(url, json=data_to_send)

# Check the response from the server
if response.status_code == 200:
    print("Data successfully written to the server.")
else:
    print("Failed to write data to the server. Status code:", response.status_code)
