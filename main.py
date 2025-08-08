# app.py (Final, Fully AI-Powered Version)

import os
import json
from flask import Flask, request, jsonify , render_template
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
print("Backend server starting...")

# --- 1. Configure the Gemini API ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Gemini API key not found. Please set it in the .env file.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
print("✅ Gemini API configured successfully.")

app = Flask(__name__)
CORS(app)

# --- 2. Define Candidate Labels ---
# We still provide the labels to guide the model's classification
candidate_labels = [
    'govt_job', 'marriage', 'nostalgia', 'comparison', 'money_advice', 
    'health', 'philosophy', 'study_abroad', 'job_shaming', 'random_fact', 
    'gulf_stories', 'politics', 'food_control'
]

# --- 3. THE NEW, ADVANCED PROMPT ---
# This prompt asks the model to generate the response text itself.
def create_prompt(advice_text):
    return f"""
    You are the "Sarcastic Ammavan Decoder", the ultimate eye-roller at cliché Malayalam advice. Your mission, should you choose to stay awake, is to dissect yet another tired pearl of wisdom and shove it into a predictable box. You've heard these gems a million times, but let's pretend this is new.

    Here's the drill, oh wise one:
    1. Pinpoint the most fitting category for this advice from this list: {', '.join(candidate_labels)}.
    2. Write a "classification_text" in Malayalam that drips with sarcasm, calling out the cliché for what it is.
    3. Craft a "recommended_action" in Malayalam that's gloriously unhelpful—think sarcastic, passive-aggressive ways to nod along and escape the lecture.

    Output ONE valid JSON object, no funny business. It must have exactly these four keys:
    - "label": The single best category name from the list.
    - "confidence": A number from 0.0 to 1.0 showing how painfully obvious this cliché is.
    - "classification_text": A snarky Malayalam description of the advice's predictability.
    - "recommended_action": A sarcastic Malayalam escape plan to dodge the conversation.

    For example, if the advice is "നിന്റെ പ്രായത്തിൽ ഒരു സർക്കാർ ജോലി നോക്കണം, പിന്നെ ജീവിതം സെറ്റ്!", your response should be:
    {{
        "label": "govt_job",
        "confidence": 0.99,
        "classification_text": "ഓ, വേറെന്താ? ക്ലാസിക് സർക്കാർ ജോലി മന്ത്രം!",
        "recommended_action": "ഒരു 'ശരി, നോക്കാം' എന്ന് മന്ത്രിച്ച് ചിരിച്ച് പതിയെ വലിഞ്ഞ് രക്ഷപ്പെടുക."
    }}

    Now, gird your loins for this gem of "wisdom".  
    Advice to analyze: "{advice_text}"

    JSON Response:
    """

@app.route('/')
def home():
    return render_template('index.html')

# --- 4. The API endpoint ---
@app.route('/analyze', methods=['POST'])
def analyze_advice():
    data = request.get_json()
    advice_text = data['advice_text']
    
    prompt = create_prompt(advice_text)
    response = model.generate_content(prompt)
    
    try:
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        model_output = json.loads(cleaned_response_text)
        
        # We now get everything directly from the model's JSON response
        final_response = {
            "classification": model_output.get("classification_text", "അജ്ഞാതമായ ജ്ഞാനം"),
            "confidence": f"{float(model_output.get('confidence', 0)) * 100:.2f}%",
            "recommended_action": model_output.get("recommended_action", "സൂക്ഷിച്ച് കൈകാര്യം ചെയ്യുക.")
        }
        return jsonify(final_response)
        
    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        print(f"Error parsing Gemini response: {e}")
        print(f"Raw response text: {response.text}")
        return jsonify({"error": "Failed to parse the model's response"}), 500

# --- 5. Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=8080)