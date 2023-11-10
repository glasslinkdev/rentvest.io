from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Store user data in a list (this will be in-memory storage, you can use a database in production)
user_data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = {
        "first_name": request.form.get('first_name'),
        "middle_name": request.form.get('middle_name'),
        "last_name": request.form.get('last_name'),
        "phone": request.form.get('phone'),
        "email": request.form.get('email'),
        "address": request.form.get('address')
    }
    user_data.append(data)

    # Save the data to a JSON file (you can use a database in production)
    with open('userdata.json', 'w') as json_file:
        json.dump(user_data, json_file, indent=4)

    return "Data submitted successfully."

if __name__ == '__main__':
    app.run(debug=True)