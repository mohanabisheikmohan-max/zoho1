import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from chatbot_config import SYSTEM_PROMPT

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please enter a question."}), 400

    if client is None:
        return jsonify({"error": "Gemini API key is not configured."}), 500

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"{SYSTEM_PROMPT}\n\nUser question:\n{message}"
        )

        answer = (response.text or "").strip()

        if not answer:
            return jsonify({"error": "No response was returned by Gemini."}), 502

        return jsonify({"answer": answer})

    except Exception:
        return jsonify({
            "error": "Gemini service is temporarily unavailable. Please check the API configuration and try again."
        }), 500

if __name__ == "__main__":
    app.run()
