from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os, json, hashlib
from datetime import datetime

app = FastAPI(title="Student-Principal Communication App")

# ------------------- CORS -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ------------------- Static & Templates -------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ------------------- Data Files -------------------
DATA_DIR = "data"
STUDENT_FILE = os.path.join(DATA_DIR, "students.json")
PRINCIPAL_FILE = os.path.join(DATA_DIR, "principals.json")
REQUEST_FILE = os.path.join(DATA_DIR, "requests.json")
EVENT_FILE = os.path.join(DATA_DIR, "events.json")
EMERGENCY_FILE = os.path.join(DATA_DIR, "emergencies.json")
os.makedirs(DATA_DIR, exist_ok=True)

# ------------------- Utility Functions -------------------
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_principal(username: str, password: str):
    hashed = hash_password(password)
    return any(p["username"] == username and p["password"] == hashed for p in load_data(PRINCIPAL_FILE))

def get_student_by_roll(roll: str):
    for s in load_data(STUDENT_FILE):
        if s["roll"] == roll:
            return s
    return None

def get_new_id(data):
    return max((item.get("id", 0) for item in data), default=0) + 1

# ------------------- Pages -------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register_student_page", response_class=HTMLResponse)
def register_student_page(request: Request):
    return templates.TemplateResponse("register_student.html", {"request": request})

@app.get("/request", response_class=HTMLResponse)
def request_page(request: Request):
    return templates.TemplateResponse("request.html", {"request": request})

@app.get("/view_requests_page", response_class=HTMLResponse)
def view_requests_page(request: Request):
    return templates.TemplateResponse("view_requests.html", {"request": request})

@app.get("/admin_dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@app.get("/event_request", response_class=HTMLResponse)
def event_request_page(request: Request):
    return templates.TemplateResponse("event_request.html", {"request": request})

@app.get("/view_event_status_page", response_class=HTMLResponse)
def view_event_status_page(request: Request):
    return templates.TemplateResponse("view_event_status.html", {"request": request})

@app.get("/emergency_request", response_class=HTMLResponse)
def emergency_request_page(request: Request):
    return templates.TemplateResponse("emergency_request.html", {"request": request})

@app.get("/view_emergency_status_page", response_class=HTMLResponse)
def view_emergency_status_page(request: Request):
    return templates.TemplateResponse("view_emergency_status.html", {"request": request})

# ------------------- Student & Principal -------------------
@app.post("/register_student")
def register_student(
    name: str = Form(...),
    roll: str = Form(...),
    branch: str = Form(...),
    year: str = Form(...)
):
    students = load_data(STUDENT_FILE)
    if any(s["roll"] == roll for s in students):
        raise HTTPException(status_code=400, detail="Student already registered")
    students.append({
        "name": name,
        "roll": roll,
        "branch": branch,
        "year": year,
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_data(STUDENT_FILE, students)
    return {"message": "Student registered successfully"}

@app.post("/register_principal")
def register_principal(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    principals = load_data(PRINCIPAL_FILE)
    if any(p["username"] == username for p in principals):
        raise HTTPException(status_code=400, detail="Principal already registered")
    principals.append({
        "username": username,
        "email": email,
        "password": hash_password(password)
    })
    save_data(PRINCIPAL_FILE, principals)
    return {"message": "Principal registered successfully"}

@app.post("/login_principal")
def login_principal(username: str = Form(...), password: str = Form(...)):
    if verify_principal(username, password):
        return {"success": True}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/students")
def get_students():
    return load_data(STUDENT_FILE)

@app.delete("/delete_student/{roll}")
def delete_student(roll: str):
    students = load_data(STUDENT_FILE)
    updated = [s for s in students if s["roll"] != roll]
    save_data(STUDENT_FILE, updated)
    return {"message": "Student deleted successfully"}

# -------- NEW: Update student --------
@app.post("/update_student")
def update_student(roll: str = Form(...), new_name: str = Form(...)):
    students = load_data(STUDENT_FILE)
    found = False
    for s in students:
        if s["roll"] == roll:
            s["name"] = new_name
            found = True
    if not found:
        raise HTTPException(status_code=404, detail="Student not found")
    save_data(STUDENT_FILE, students)
    return {"message": "Student updated successfully"}

# -------- NEW: Dashboard page --------
@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request):
    students = load_data(STUDENT_FILE)
    return templates.TemplateResponse("dashboard.html", {"request": request, "students": students})

# ------------------- Leave Requests -------------------
@app.post("/request_permission")
def request_permission(
    roll: str = Form(...), reason: str = Form(...),
    start_date: str = Form(...), return_date: str = Form(...), total_days: str = Form(...)
):
    student = get_student_by_roll(roll)
    if not student:
        raise HTTPException(status_code=400, detail="Student not registered")
    requests = load_data(REQUEST_FILE)
    requests.append({
        "id": get_new_id(requests),
        "name": student["name"],
        "roll": roll,
        "branch": student["branch"],
        "year": student["year"],
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
def update_status(
    request_id: int = Form(...), status: str = Form(...), response: str = Form(""),
    username: str = Form(...), password: str = Form(...)
):
    if not verify_principal(username, password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    requests = load_data(REQUEST_FILE)
    for r in requests:
        if r["id"] == request_id:
            r.update({"status": status, "response": response})
            save_data(REQUEST_FILE, requests)
            return {"message": "Request updated"}
    raise HTTPException(status_code=404, detail="Request ID not found")

@app.post("/view_requests")
def view_requests(
    role: str = Form(...), username: str = Form(None),
    password: str = Form(None), roll: str = Form(None)
):
    if role == "principal":
        if verify_principal(username, password):
            return load_data(REQUEST_FILE)
        raise HTTPException(status_code=401, detail="Unauthorized")
    elif role == "student":
        if not roll:
            raise HTTPException(status_code=400, detail="Roll number required")
        return [r for r in load_data(REQUEST_FILE) if r["roll"] == roll]
    raise HTTPException(status_code=400, detail="Invalid role")

# ------------------- Event Requests -------------------
@app.post("/submit_event")
def submit_event(
    title: str = Form(...), date: str = Form(...), location: str = Form(...),
    description: str = Form(...), roll: str = Form(...)
):
    student = get_student_by_roll(roll)
    if not student:
        raise HTTPException(status_code=400, detail="Student not registered")
    events = load_data(EVENT_FILE)
    events.append({
        "id": get_new_id(events),
        "title": title,
        "date": date,
        "location": location,
        "description": description,
        "requested_by": student["name"],
        "roll": roll,
        "branch": student["branch"],
        "year": student["year"],
        "status": "Pending",
        "response": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_data(EVENT_FILE, events)
    return {"message": "Event request submitted"} 

@app.post("/update_event")
def update_event(
    eventId: int = Form(...),
    status: str = Form(...),
    principalusername: str = Form(...),
    principalpassword: str = Form(...),
    title: str = Form(None),
    date: str = Form(None),
    location: str = Form(None),
    description: str = Form(None)
):
    if not verify_principal(principalusername, principalpassword):
        raise HTTPException(status_code=401, detail="Unauthorized")
    events = load_data(EVENT_FILE)
    for e in events:
        if e["id"] == eventId:
            if title: e["title"] = title
            if date: e["date"] = date
            if location: e["location"] = location
            if description: e["description"] = description
            e["status"] = status
            save_data(EVENT_FILE, events)
            return {"message": "Event updated successfully", "event": e}
    raise HTTPException(status_code=404, detail="Event not found")

@app.post("/delete_event")
def delete_event(
    eventId: int = Form(...),
    principalusername: str = Form(...),
    principalpassword: str = Form(...)
):
    if not verify_principal(principalusername, principalpassword):
        raise HTTPException(status_code=401, detail="Unauthorized")
    events = load_data(EVENT_FILE)
    updated_events = [e for e in events if e["id"] != eventId]
    if len(updated_events) == len(events):
        raise HTTPException(status_code=404, detail="Event not found")
    save_data(EVENT_FILE, updated_events)
    return {"message": "Event deleted successfully"}

@app.get("/get_event_requests")
def get_event_requests(username: str, password: str):
    if not verify_principal(username, password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return load_data(EVENT_FILE)

@app.post("/view_events_by_roll")
def view_events_by_roll(roll: str = Form(...)):
    return [e for e in load_data(EVENT_FILE) if e["roll"] == roll]

# ------------------- Emergency Requests -------------------
@app.post("/submit_emergency")
def submit_emergency(
    roll: str = Form(...), emergency_type: str = Form(...), description: str = Form(...)
):
    student = get_student_by_roll(roll)
    if not student:
        raise HTTPException(status_code=400, detail="Student not registered")
    emergencies = load_data(EMERGENCY_FILE)
    emergencies.append({
        "id": get_new_id(emergencies),
        "name": student["name"],
        "roll": roll,
        "branch": student["branch"],
        "year": student["year"],
        "emergency_type": emergency_type,
        "description": description,
        "status": "Pending",
        "response": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_data(EMERGENCY_FILE, emergencies)
    return {"message": "Emergency request submitted"}

@app.get("/get_emergencies")
def get_emergencies(username: str, password: str):
    if not verify_principal(username, password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return load_data(EMERGENCY_FILE)

@app.post("/update_emergency_status")
def update_emergency_status(
    id: int = Form(...), status: str = Form(...), response: str = Form(""),
    username: str = Form(...), password: str = Form(...)
):
    if not verify_principal(username, password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    emergencies = load_data(EMERGENCY_FILE)
    for e in emergencies:
        if e["id"] == id:
            e.update({"status": status, "response": response})
            save_data(EMERGENCY_FILE, emergencies)
            return {"message": "Emergency request updated"}
    raise HTTPException(status_code=404, detail="Emergency request not found")

@app.post("/view_emergency_by_roll")
def view_emergency_by_roll(roll: str = Form(...)):
    return [e for e in load_data(EMERGENCY_FILE) if e["roll"] == roll]
