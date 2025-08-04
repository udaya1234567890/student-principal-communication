from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime
import json
import os

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# File paths
STUDENT_FILE = "students.json"
PRINCIPAL_FILE = "principals.json"
REQUEST_FILE = "requests.json"

# Helper functions
def load_data(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_data(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def get_new_request_id(requests):
    if not requests:
        return 1
    return max([req["id"] for req in requests], default=0) + 1

# Register student
@app.post("/register_student")
def register_student(name: str = Form(...), roll: str = Form(...)):
    students = load_data(STUDENT_FILE)
    if any(s["roll"] == roll for s in students):
        return {"error": "Student already registered"}
    students.append({
        "name": name,
        "roll": roll,
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_data(STUDENT_FILE, students)
    return {"message": "Student registered successfully"}

@app.get("/students")
def get_students():
    return load_data(STUDENT_FILE)

@app.delete("/delete_student/{roll}")
def delete_student(roll: str):
    students = load_data(STUDENT_FILE)
    updated_students = [s for s in students if s["roll"] != roll]
    save_data(STUDENT_FILE, updated_students)
    return {"message": f"Student with roll {roll} deleted"}

# Register principal
@app.post("/register_principal")
def register_principal(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    principals = load_data(PRINCIPAL_FILE)
    if any(p["username"] == username for p in principals):
        return {"error": "Principal already registered"}
    principals.append({
        "username": username,
        "email": email,
        "password": password
    })
    save_data(PRINCIPAL_FILE, principals)
    return {"message": "Principal registered successfully"}

@app.post("/login_principal")
def login_principal(username: str = Form(...), password: str = Form(...)):
    principals = load_data(PRINCIPAL_FILE)
    for p in principals:
        if p["username"] == username and p["password"] == password:
            return {"success": True}
    return {"success": False, "message": "Invalid credentials"}

# Request permission
@app.post("/request_permission")
def request_permission(
    name: str = Form(...),
    roll: str = Form(...),
    reason: str = Form(...),
    start_date: str = Form(...),
    return_date: str = Form(...),
    total_days: str = Form(...)
):
    students = load_data(STUDENT_FILE)
    if not any(s["roll"] == roll for s in students):
        return {"error": "Student not registered"}

    requests = load_data(REQUEST_FILE)
    new_id = get_new_request_id(requests)

    requests.append({
        "id": new_id,
        "name": name,
        "roll": roll,
        "reason": reason,
        "start_date": start_date,
        "return_date": return_date,
        "total_days": total_days,
        "status": "Pending",
        "response": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_data(REQUEST_FILE, requests)
    return {"message": "Leave request submitted"}

# Update leave request status
@app.post("/update_status")
def update_status(
    request_id: int = Form(...),
    status: str = Form(...),           # Approved / Rejected / Paused
    response: str = Form(""),
    username: str = Form(...),
    password: str = Form(...)
):
    principals = load_data(PRINCIPAL_FILE)
    is_valid = any(p["username"] == username and p["password"] == password for p in principals)

    if not is_valid:
        return {"error": "Unauthorized principal"}

    requests = load_data(REQUEST_FILE)
    found = False

    for req in requests:
        if req["id"] == request_id:
            req["status"] = status
            req["response"] = response
            found = True
            break

    if not found:
        return {"error": "Request ID not found"}

    save_data(REQUEST_FILE, requests)
    return {"message": "Request status updated successfully"}

# View requests
@app.post("/view_requests")
def view_requests(role: str = Form(...), username: str = Form(None), password: str = Form(None), roll: str = Form(None)):
    requests = load_data(REQUEST_FILE)

    if role == "principal":
        principals = load_data(PRINCIPAL_FILE)
        is_valid = any(p["username"] == username and p["password"] == password for p in principals)
        if is_valid:
            return requests
        return {"error": "Unauthorized"}

    elif role == "student":
        if not roll:
            return {"error": "Roll number required"}
        return [r for r in requests if r["roll"] == roll]

    return {"error": "Invalid role"}

# Serve HTML pages
def serve_html(filename: str):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content=f"{filename} not found", status_code=404)

@app.get("/request", response_class=HTMLResponse)
def request_page():
    return serve_html("request.html")

@app.get("/admin_dashboard", response_class=HTMLResponse)
def admin_page():
    return serve_html("admin_dashboard.html")

@app.get("/view_requests_page", response_class=HTMLResponse)
def view_page():
    return serve_html("view_requests.html")

@app.get("/")
def root():
    return {"message": "Principal-Student Communication App is running"}
