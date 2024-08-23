from flask import Flask, request, jsonify
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv
from flask_cors import CORS


# Load environment variables from .env file
load_dotenv()


app = Flask(__name__)
CORS(app)


# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def get_location_name(lat, lon):
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={google_maps_api_key}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        return data['results'][0]['formatted_address']
    return "Location not found"


@app.route('/generate-guide', methods=['POST'])
def generate_guide():
    data = request.get_json()
    location = data.get('location')
    lat = location['lat']
    lon = location['lon']
    interests = data.get('interests', [])  # Get interests from the request


    # Get the readable location name using Geocoding API
    location_name = get_location_name(lat, lon)


    try:
        # Combine interests into a single string
        interest_str = " and ".join(interests)
        
        # Generate the tour guide using OpenAI's Chat API
        prompt = f"Create a guided tour for the location: {location_name}. Include points of interest related to {interest_str}."
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the appropriate model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )


        guide_text = completion.choices[0].message.content.strip()


    except Exception as e:
        return jsonify({"error": f"OpenAI API call failed: {str(e)}"}), 500


    return jsonify({"guide": guide_text})


if __name__ == '__main__':
    app.run(debug=True)