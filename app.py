import os
import io
import json
from flask import Flask, render_template, request, jsonify
from PIL import Image
from google import genai

app = Flask(__name__)

# Configure Google GenAI Client
API_KEY = os.getenv("GEMINI_API_KEY", "ENTER_API_KEY")
client = genai.Client(api_key=API_KEY)

# ==================== KNOWLEDGE GRAPH DATABASE ====================
KNOWN_INTERACTIONS_GRAPH = [
    {
        "pair": ["warfarin", "cranberry juice"],
        "type": "Drug-Food",
        "severity": "High",
        "description": "Cranberry juice inhibits CYP2C9 metabolism of Warfarin, significantly increasing bleeding risks.",
        "recommendation": "Avoid cranberry juice completely while taking Warfarin."
    },
    {
        "pair": ["warfarin", "aspirin"],
        "type": "Drug-Drug",
        "severity": "High",
        "description": "Combining anticoagulants (Warfarin) with antiplatelet agents (Aspirin) dramatically elevates major hemorrhage risk.",
        "recommendation": "Use together only under strict cardiologist supervision with regular INR monitoring."
    },
    {
        "pair": ["aspirin", "ibuprofen"],
        "type": "Drug-Drug",
        "severity": "Moderate",
        "description": "Ibuprofen may attenuate the cardioprotective antiplatelet effect of low-dose Aspirin.",
        "recommendation": "Take Aspirin at least 30 minutes before or 8 hours after Ibuprofen."
    },
    {
        "pair": ["atorvastatin", "grapefruit juice"],
        "type": "Drug-Food",
        "severity": "High",
        "description": "Grapefruit juice inhibits CYP3A4 and increases Atorvastatin serum concentration, escalating rhabdomyolysis risk.",
        "recommendation": "Avoid large quantities of grapefruit juice."
    },
    {
        "pair": ["lisinopril", "potassium supplements"],
        "type": "Drug-Nutrient",
        "severity": "Moderate",
        "description": "ACE inhibitors reduce potassium excretion; combining with potassium supplements can cause severe hyperkalemia.",
        "recommendation": "Monitor serum potassium levels regularly."
    },
    {
        "pair": ["metformin", "alcohol"],
        "type": "Drug-Food",
        "severity": "High",
        "description": "Alcohol potentiates the effect of Metformin on lactate metabolism, raising severe lactic acidosis risk.",
        "recommendation": "Avoid excessive alcohol intake while on Metformin."
    }
]

@app.route("/")
def index():
    return render_template("index.html")


# 1. INSTANT AUTO-GREETING & SCHEDULE BRIEFING NARRATOR
@app.route("/api/narrator-greeting", methods=["POST"])
def narrator_greeting():
    try:
        data = request.get_json() or {}
        patient_name = data.get("patient_name", "Patient")
        medicines = data.get("medicines", [])
        language = data.get("language", "English")

        completed_meds = [m for m in medicines if m.get("taken")]
        pending_meds = [m for m in medicines if not m.get("taken")]

        prompt = f"""
        You are PolyBot, an always-active voice narrator and personal AI assistant for elderly patients.
        
        Patient Name: {patient_name}
        Selected Language: {language}
        Completed Medicines Today: {json.dumps(completed_meds)}
        Pending Medicines Today: {json.dumps(pending_meds)}

        Instructions:
        1. Speak warmly in simple, clear, and reassuring tone for senior citizens.
        2. Deliver the response strictly in {language}.
        3. Greet {patient_name} immediately on app load.
        4. Briefly state completed pills vs pending pills with time & food context.
        5. Warn if any severe clash exists (e.g. Warfarin and Cranberry Juice).
        6. End by assuring them that you are listening and navigating with them continuously.
        7. Keep response to 2-3 short sentences max for immediate TTS reading.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return jsonify({"success": True, "greeting": response.text})

    except Exception as e:
        print("Narrator Greeting Error:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


# 2. ACTION & NAVIGATION REAL-TIME NARRATOR
@app.route("/api/narrate-action", methods=["POST"])
def narrate_action():
    try:
        data = request.get_json() or {}
        action_type = data.get("action_type", "")  # e.g., 'check_med', 'add_med', 'scan_prescription', 'open_modal', 'change_lang'
        details = data.get("details", {})
        language = data.get("language", "English")

        prompt = f"""
        You are PolyBot, a continuous real-time navigation narrator for an elderly patient app.
        The user performed this action: "{action_type}" with details: {json.dumps(details)}.
        Language: {language}

        Instructions:
        1. Generate a single clear, friendly sentence in {language} narrating what just happened or guiding what to do next.
        2. Keep it under 15 words so speech synthesis is instant and fluid.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return jsonify({"success": True, "narration": response.text})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# 3. OCR PRESCRIPTION SCANNER
@app.route("/api/scan-prescription", methods=["POST"])
def scan_prescription():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No image file uploaded"}), 400
        
        file = request.files["file"]
        image = Image.open(io.BytesIO(file.read()))

        prompt = """
        You are an expert clinical pharmacologist and OCR system.
        Analyze the handwritten or printed prescription in the image.
        Return ONLY a strict JSON array (no markdown code blocks, no intro text) of extracted medicines with this schema:
        [
          {
            "name": "Medicine Name and Strength",
            "dose": "Dosage (e.g., 500mg)",
            "type": "tablet / capsule / syrup / injection",
            "frequency": "Frequency (e.g., Twice daily, Once daily)",
            "when_to_eat": "Timing (e.g., After food, Before breakfast)",
            "pills_per_dose": "Amount (e.g., 1 tab)"
          }
        ]
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image]
        )

        clean_json = response.text.strip().replace("```json", "").replace("```", "").strip()
        medicines = json.loads(clean_json)

        return jsonify({"success": True, "medicines": medicines})

    except Exception as e:
        print("OCR Error:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


# 4. AI CHATBOT & CONTINUOUS VOICE DOUBT RESOLUTION
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        user_msg = data.get("message", "")
        medicines = data.get("medicines", [])
        language = data.get("language", "English")

        prompt = f"""
        You are PolyBot, an empathetic personal AI health assistant and continuous voice companion for elderly patients.
        Active patient schedule: {json.dumps(medicines)}
        Output Language: {language}

        User query: "{user_msg}"

        Instructions:
        1. Respond strictly in {language}.
        2. Keep sentences clear, simple, and reassuring for elderly listening.
        3. If the user asks for repetition, re-explain their pending medicines gently and clearly.
        4. Answer any doubt about medicine timing, food interactions, side effects, or general health concerns directly.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return jsonify({"success": True, "reply": response.text})

    except Exception as e:
        print("Chat Error:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


# 5. KNOWLEDGE GRAPH INTERACTION ENGINE
@app.route("/api/check-interactions", methods=["POST"])
def check_interactions():
    try:
        data = request.get_json() or {}
        medicines = data.get("medicines", [])

        if not medicines or len(medicines) < 2:
            return jsonify({
                "success": True, 
                "risk_status": "Safe",
                "interactions": []
            })

        found_interactions = []
        med_names_lower = [m.lower() for m in medicines]

        for item in KNOWN_INTERACTIONS_GRAPH:
            target_1, target_2 = item["pair"][0], item["pair"][1]
            has_1 = any(target_1 in m for m in med_names_lower)
            has_2 = any(target_2 in m for m in med_names_lower)

            if has_1 and has_2:
                found_interactions.append({
                    "pair": f"{item['pair'][0].title()} + {item['pair'][1].title()}",
                    "severity": item["severity"],
                    "type": item["type"],
                    "description": item["description"],
                    "recommendation": item["recommendation"]
                })

        if not found_interactions:
            prompt = f"""
            Analyze these patient medications and food items for potential interactions:
            Items: {json.dumps(medicines)}

            Return strictly a JSON object with this exact structure:
            {{
              "risk_status": "Severe / Caution / Safe",
              "interactions": [
                 {{
                    "pair": "Drug A + Drug B or Food",
                    "severity": "High / Moderate / Low",
                    "type": "Drug-Drug / Drug-Food",
                    "description": "Clear mechanism explanation in plain terms.",
                    "recommendation": "Safer timing or clinical alternative recommendation."
                 }}
              ]
            }}
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            clean_json = response.text.strip().replace("```json", "").replace("```", "").strip()
            analysis = json.loads(clean_json)
            return jsonify({"success": True, "data": analysis})

        has_high = any(i["severity"] == "High" for i in found_interactions)
        risk_status = "Severe Risk" if has_high else ("Caution" if found_interactions else "Safe")

        return jsonify({
            "success": True,
            "data": {
                "risk_status": risk_status,
                "interactions": found_interactions
            }
        })

    except Exception as e:
        print("Interaction Engine Error:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
