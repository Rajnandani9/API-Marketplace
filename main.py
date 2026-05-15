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
    name TEXT,
    description TEXT
)
""")

conn.commit()


@app.get("/")
async def home():
    return {
        "status": "success",
        "message": "API Marketplace Running Successfully 🚀"
    }


@app.get("/apis")
async def get_apis():

    cursor.execute("SELECT * FROM apis")
    rows = cursor.fetchall()

    data = []

    for row in rows:
        data.append({
            "id": row[0],
            "name": row[1],
            "description": row[2]
        })

    return {"apis": data}


@app.post("/add-api")
async def add_api(name: str, description: str):

    cursor.execute(
        "INSERT INTO apis (name, description) VALUES (?, ?)",
        (name, description)
    )

    conn.commit()

    return {
        "message": "API Added Successfully"
    }