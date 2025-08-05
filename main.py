from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime
import json
import os

app = FastAPI()

# Enable CORS
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
EVENT_FILE = "events.json"

# Utility Functions
def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_new_id(data):
    return max([d.get("id", 0) for d in data], default=0) + 1

# ---------------- Student & Principal ----------------

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
    return {"message": "Student registered"}

@app.post("/register_principal")
def register_principal(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    principals = load_data(PRINCIPAL_FILE)
    if any(p["username"] == username for p in principals):
        return {"error": "Principal already registered"}
    principals.append({"username": username, "email": email, "password": password})
    save_data(PRINCIPAL_FILE, principals)
    return {"message": "Principal registered"}

@app.post("/login_principal")
def login_principal(username: str = Form(...), password: str = Form(...)):
    if any(p["username"] == username and p["password"] == password for p in load_data(PRINCIPAL_FILE)):
        return {"success": True}
    return {"success": False, "message": "Invalid credentials"}

@app.get("/students")
def get_students():
    return load_data(STUDENT_FILE)

@app.delete("/delete_student/{roll}")
def delete_student(roll: str):
    students = load_data(STUDENT_FILE)
    updated = [s for s in students if s["roll"] != roll]
    save_data(STUDENT_FILE, updated)
    return {"message": "Student deleted"}

# ---------------- Leave Requests ----------------

@app.post("/request_permission")
def request_permission(name: str = Form(...), roll: str = Form(...), reason: str = Form(...),
                       start_date: str = Form(...), return_date: str = Form(...), total_days: str = Form(...)):
    if not any(s["roll"] == roll for s in load_data(STUDENT_FILE)):
        return {"error": "Student not registered"}
    requests = load_data(REQUEST_FILE)
    new_id = get_new_id(requests)
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

@app.post("/update_status")
def update_status(request_id: int = Form(...), status: str = Form(...), response: str = Form(""),
                  username: str = Form(...), password: str = Form(...)):
    if not any(p["username"] == username and p["password"] == password for p in load_data(PRINCIPAL_FILE)):
        return {"error": "Unauthorized"}
    requests = load_data(REQUEST_FILE)
    for r in requests:
        if r["id"] == request_id:
            r["status"] = status
            r["response"] = response
            save_data(REQUEST_FILE, requests)
            return {"message": "Request updated"}
    return {"error": "Request ID not found"}

@app.post("/view_requests")
def view_requests(role: str = Form(...), username: str = Form(None), password: str = Form(None), roll: str = Form(None)):
    if role == "principal":
        if any(p["username"] == username and p["password"] == password for p in load_data(PRINCIPAL_FILE)):
            return load_data(REQUEST_FILE)
        return {"error": "Unauthorized"}
    elif role == "student":
        if not roll:
            return {"error": "Roll number required"}
        return [r for r in load_data(REQUEST_FILE) if r["roll"] == roll]
    return {"error": "Invalid role"}

# ---------------- Event Requests ----------------

@app.post("/submit_event")
def submit_event(title: str = Form(...), date: str = Form(...), location: str = Form(...),
                 description: str = Form(...), name: str = Form(...), roll: str = Form(...)):
    if not any(s["roll"] == roll for s in load_data(STUDENT_FILE)):
        return {"error": "Student not registered"}
    events = load_data(EVENT_FILE)
    new_id = get_new_id(events)
    events.append({
        "id": new_id,
        "title": title,
        "date": date,
        "location": location,
        "description": description,
        "requested_by": name,
        "roll": roll,
        "status": "Pending",
        "response": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_data(EVENT_FILE, events)
    return {"message": "Event request submitted"}

@app.post("/view_events_by_roll")
def view_events_by_roll(roll: str = Form(...)):
    return [e for e in load_data(EVENT_FILE) if e["roll"] == roll]

@app.get("/get_event_requests")
def get_event_requests(username: str, password: str):
    if not any(p["username"] == username and p["password"] == password for p in load_data(PRINCIPAL_FILE)):
        return {"error": "Unauthorized"}
    return load_data(EVENT_FILE)

@app.post("/update_event_status")
def update_event_status(id: int = Form(...), title: str = Form(...), date: str = Form(...),
                        location: str = Form(...), description: str = Form(...), status: str = Form(...),
                        username: str = Form(...), password: str = Form(...)):
    if not any(p["username"] == username and p["password"] == password for p in load_data(PRINCIPAL_FILE)):
        return {"error": "Unauthorized"}
    events = load_data(EVENT_FILE)
    for e in events:
        if e["id"] == id:
            e["title"] = title
            e["date"] = date
            e["location"] = location
            e["description"] = description
            e["status"] = status
            save_data(EVENT_FILE, events)
            return {"message": "Event updated"}
    return {"error": "Event not found"}

@app.get("/delete_event")
def delete_event(id: int, username: str, password: str):
    if not any(p["username"] == username and p["password"] == password for p in load_data(PRINCIPAL_FILE)):
        return {"error": "Unauthorized"}
    events = load_data(EVENT_FILE)
    updated = [e for e in events if e["id"] != id]
    save_data(EVENT_FILE, updated)
    return {"message": "Event deleted"}

# ---------------- Serve HTML Pages ----------------

def serve_html(file: str):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content=f"{file} not found", status_code=404)

@app.get("/")
def root():
    return {"message": "Principal-Student Communication App is running"}

@app.get("/request", response_class=HTMLResponse)
def request_page():
    return serve_html("request.html")

@app.get("/admin_dashboard", response_class=HTMLResponse)
def admin_dashboard():
    return serve_html("admin_dashboard.html")

@app.get("/view_requests_page", response_class=HTMLResponse)
def view_requests_page():
    return serve_html("view_requests.html")

@app.get("/event_request", response_class=HTMLResponse)
def event_request_page():
    return serve_html("event_request.html")

@app.get("/view_event_status", response_class=HTMLResponse)
def view_event_status_page():
    return serve_html("view_event_status.html")
