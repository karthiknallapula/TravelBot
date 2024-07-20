from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
from openai import OpenAI
import pyttsx3
import requests

app = Flask(__name__, static_folder='static', template_folder='templates')

# Define your API key
GOOGLE_API_KEY = 'AIzaSyBGCk8jBdlDnWcP0EObe0AAuP5IML1O6bc'
genai.configure(api_key=GOOGLE_API_KEY)

def get_weather(city):
    base_url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'units': 'metric',  # Use 'imperial' for Fahrenheit
        'appid': '863dac0d7db84fee9ac95b89cc47d32a'
    }
    response = requests.get(base_url, params=params)
    weather_data = response.json()
    
    if weather_data['cod'] == 200:
        # Extract relevant weather information
        main_weather = weather_data['weather'][0]['main']
        description = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        
        # Print weather information
        return f'Current weather in {city}: Description: {main_weather} and {description}, Temperature: {temp}°C, Humidity: {humidity}%, Wind Speed: {wind_speed} m/s'
    else:
        return ""
    
def get_location_name(prompt):
    model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="You will return the name of the location mentioned. If more than one are mentioned then only return the first location.",
    generation_config=genai.GenerationConfig(
        max_output_tokens=2000,
        temperature=0.9,
    ))
    response = model.generate_content(prompt)
    if response and response._result and response._result.candidates:
        gemini_response = response._result.candidates[0].content.parts[0].text
        return gemini_response.strip()
    else:
        return ""
    
session = {'context': {'previous_responses': []}}

# Function to call the Generative Language API and get a response
def get_gemini_response(prompt):
    model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="""You will respond as a travel planner that plans 
    out one's trips. Mention places specific to the chosen area. **Analyze 
    the weather conditions and inform the user how suitable it is for their 
    trip activities**. If the weather seems perfect, suggest exploring or 
    highlight activities that benefit from the conditions. If the weather 
    is not ideal, suggest alternative activities or recommend rescheduling 
    the trip (depending on severity). DO NOT ask for more information if 
    the user doesn't provide any just give them a generic plan.""",
    generation_config=genai.GenerationConfig(
        max_output_tokens=2000,
        temperature=0.9,
    ))
    print(get_location_name(prompt))
    weather = get_weather(get_location_name(prompt))
    print(weather)
    prompt = prompt + weather
    context = session['context']
    context['previous_responses'].append(prompt)
    response = model.generate_content('\n'.join(context['previous_responses']))
    if response and response._result and response._result.candidates:
        gemini_response = response._result.candidates[0].content.parts[0].text
        context['previous_responses'].append(gemini_response)  # Store the generated response in context
        session['context'] = context  # Update session context
        return gemini_response
    else:
        return "No response found"

# Function to clean text by removing asterisks
def clean_text(text):
    return text.replace('*', '')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    prompt = request.json.get('prompt')
    if prompt:
        response = get_gemini_response(prompt)
        clean_response = clean_text(response)
        return jsonify(response=clean_response)
    else:
        return jsonify(response="Please enter a prompt.")

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle text-to-speech
@app.route('/read_aloud', methods=['POST'])
def read_aloud():
    text = request.json.get('text')
    
    # Reinitialize the TTS engine for each request
    tts_engine = pyttsx3.init()

    # Configure TTS engine properties (optional)
    tts_engine.setProperty('rate', 180)  # Speed percent (can go over 100)
    tts_engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)

    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
        tts_engine.stop()  # Ensure the engine is properly shut down
        return jsonify(status="success")
    except Exception as e:
        return jsonify(status="error", message=str(e))

if __name__ == '__main__':
    app.run(debug=True)
