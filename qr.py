from collections import defaultdict
import os
from flask import Flask, jsonify, request, render_template_string
import datetime
import csv
from datetime import datetime

app = Flask(__name__)

# Enhanced HTML Form with styling and client-side validation
HTML_FORM = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attendance Form</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        form {
            background-color: #f7f7f7;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        input, button {
            margin: 10px 0;
            padding: 10px;
            width: 100%;
            box-sizing: border-box;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .error {
            color: red;
            font-size: 0.9em;
        }
    </style>
    <script>
        function validateForm() {
            const nameInput = document.getElementById('name');
            const errorDiv = document.getElementById('error-message');
            if (!nameInput.value.trim() || nameInput.value.trim().split(' ').length < 2) {
                errorDiv.textContent = "Please enter your full name (at least two words).";
                return false;
            }
            errorDiv.textContent = ""; // Clear error message
            return true; // Allow form submission
        }
    </script>
</head>
<body>


<form onsubmit="return validateForm();" method="post">
    <div id="error-message" class="error"></div>
    <label for="time">Time:</label>
    <input type="text" id="time" name="time" value="{{ current_time }}" readonly><br>
    <label for="name">Name:</label>
    <input type="text" id="name" name="name" placeholder="Full Name" required><br>
    <button type="submit">Submit</button>
</form>

</body>
</html>
'''

def save_to_csv(name, time):
    date_str = datetime.strptime(time, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    file_name = f'attendance_{date_str}.csv'
    if not name_already_exists(name, file_name):
        with open(file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time, name])
        return True
    return False

@app.route('/', methods=['GET', 'POST'])
def capture_attendance():
    if request.method == 'POST':
        name = request.form['name']
        time = request.form.get('time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if save_to_csv(name, time):
            return render_template_string('''
                <div style="text-align: center; margin-top: 20px;">
                    <h2 style="color: #4CAF50;">Attendance recorded successfully!</h2>
                    <a href="/" style="display: inline-block; margin-top: 20px; background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Record Another</a>
                </div>
            ''')
        else:
            return render_template_string('''
                <div style="text-align: center; margin-top: 20px;">
                    <h2 style="color: #D32F2F;">Name already present for this date.</h2>
                    <a href="/" style="display: inline-block; margin-top: 20px; background-color: #1976D2; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go Back</a>
                </div>
            ''')
    else:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return render_template_string(HTML_FORM, current_time=current_time)
    
def name_already_exists(name, file_name):
    if not os.path.exists(file_name):
        return False
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            _, existing_name = row
            if name.lower() == existing_name.lower():
                return True
    return False
    
@app.route('/data', methods=['GET'])
def get_data():
    date_param = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    file_name = f'attendance_{date_param}.csv'
    
    if not os.path.exists(file_name):
        return jsonify({"error": "No data found for this date"}), 404

    data_by_hour = defaultdict(list)  # Simplified to directly store lists of names by hour
    
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            time, name = row
            hour = datetime.strptime(time, '%Y-%m-%d %H:%M:%S').strftime('%H')
            data_by_hour[hour].append(name)

    # Preparing the structured response
    response = {
        "date": date_param,
        "hours": {hour: names for hour, names in sorted(data_by_hour.items())}
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
