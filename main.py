from fastapi import FastAPI
import sqlite3

app = FastAPI()

# Database Connection
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# Create Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS apis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL
)
""")

conn.commit()

# Home Route
@app.get("/")
def home():
    return {
        "message": "API Marketplace Running Successfully on Vercel 🚀"
    }

# Get All APIs
@app.get("/apis")
def get_apis():
    cursor.execute("SELECT * FROM apis")
    data = cursor.fetchall()

    apis = []

    for api in data:
        apis.append({
            "id": api[0],
            "name": api[1],
            "description": api[2]
        })

    return {"apis": apis}

# Add API
@app.post("/add-api")
def add_api(name: str, description: str):

    cursor.execute(
        "INSERT INTO apis (name, description) VALUES (?, ?)",
        (name, description)
    )

    conn.commit()

    return {
        "message": "API Added Successfully"
    }