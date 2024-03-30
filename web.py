import cv2
import numpy as np
import pandas as pd
import base64
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Define your Plant.id API key
PLANT_ID_API_KEY = 'V2d4whKmG682XKG4HrNT1yh5zPYUnSECQ4czFda90Oc6fW2Y2V'

# Load the CSV file containing plant descriptions and uses
plant_info_df = pd.read_csv("C:/Users/NAGA HARSHITHA/OneDrive/Desktop/Plant/plant_descriptions_and_uses.csv", encoding='cp1252')

# Function to encode image to base64
def encode_image(image):
    _, encoded_image = cv2.imencode('.jpg', image)
    base64_encoded_image = base64.b64encode(encoded_image).decode('utf-8')
    return base64_encoded_image

# Function to identify plant using Plant.id API
def identify_plant(image):
    base64_image = encode_image(image)
    url = "https://api.plant.id/v2/identify"
    headers = {
        "Content-Type": "application/json",
        "Api-Key": PLANT_ID_API_KEY
    }
    data = {
        "images": [base64_image],
        "organs": ["leaf"]
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def get_plant_info_from_csv(plant_name):
    # Lookup the plant name in the DataFrame
    plant_info = plant_info_df[plant_info_df['PlantName'].str.contains(plant_name, case=False, na=False)]
    if not plant_info.empty:
        # Assuming 'Description' and 'Uses' are the column names in your CSV
        description = plant_info.iloc[0]['Description']
        uses = plant_info.iloc[0]['Uses']
        return description, uses
    else:
        return "Description not available", "Uses not available"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', message='No file part')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', message='No selected file')
        
        try:
            image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
            plant_id_response = identify_plant(image)
            
            if plant_id_response and plant_id_response['suggestions']:
                plant_info = plant_id_response['suggestions'][0]
                plant_name = plant_info['plant_name']
                
                # Get additional information from CSV
                description, uses = get_plant_info_from_csv(plant_name)
                
                # Display the identified plant information along with the description and uses from the CSV
                return render_template('index.html', predicted_plant=plant_name, plant_description=description, plant_uses=uses)
            else:
                return render_template('index.html', message='Plant not identified')

        except Exception as e:
            return render_template('index.html', message=f'Error: {str(e)}')

    return render_template('index.html')

# Define a route for the favicon
@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)