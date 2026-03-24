from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from ml_model import predict_price
from dotenv import load_dotenv
import sqlite3
import requests
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Create database
def create_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstName TEXT,
        lastName TEXT,
        contact TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

create_db()

@app.route("/")
def home():
    return "Ornafy backend running"

@app.route("/signup", methods=["POST"])
def signup():

    data = request.get_json()

    firstName = data["firstName"]
    lastName = data["lastName"]
    contact = data["contact"]
    password = generate_password_hash(data["password"])

    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(firstName,lastName,contact,password) VALUES (?,?,?,?)",
            (firstName,lastName,contact,password)
        )

        conn.commit()
        conn.close()

        return jsonify({"status":"success"})

    except:
        return jsonify({"status":"error","message":"User already exists"})
    
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    contact = data["contact"]
    password = data["password"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE contact=?",
        (contact,)
    )

    user = cursor.fetchone()

    conn.close()

    if user and check_password_hash(user[4], password):
        return jsonify({"status":"success"})
    else:
        return jsonify({"status":"error"})
    
@app.route("/generate_jewelry", methods=["POST"])
def generate_jewelry():

    data = request.get_json()

    jewelry = data["type"]
    metal = data["metal"]
    stone = data["stone"]
    description = data["description"]

    prompt = f"""luxury {metal} {stone} {jewelry},
    custom jewelry design: {description},
    high-end jewelry product photography,
    white background,
    studio lighting,
    ultra detailed,
    4k render,
    professional catalog photo
    """

    print("Generating image for:", prompt)

    API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer{os.getenv("HF_TOKEN")}"
    }

    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

    print("Status Code:", response.status_code)
    print("Content Type:", response.headers.get("content-type"))

    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        print("HuggingFace error:", response.json())
        return jsonify({
        "error": "AI model is warming up. Please try again in a few seconds."
        })
    return Response(response.content, mimetype="image/png")

@app.route("/predict_price", methods=["POST"])
def predict_price_api():

    data = request.get_json()

    jewelry = data["type"]
    metal = data["metal"]
    stone = data["stone"]

    price = predict_price(jewelry, metal, stone)

    return jsonify({"price": price})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)