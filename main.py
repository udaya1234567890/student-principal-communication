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

# JSON file to store student data
FILE_NAME = "students.json"
PRINCIPAL_FILE = "principal.json"

# Load existing student data
if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r") as f:
        students = json.load(f)
else:
    students = []

# Load existing principal data
if os.path.exists(PRINCIPAL_FILE):
    with open(PRINCIPAL_FILE, "r") as f:
        principals = json.load(f)
else:
    principals = []

# Home route
@app.get("/")
def home():
    return {"message": "Welcome to Principal-Student Communication App!"}

# Register student
@app.post("/register")
def register(name: str = Form(...), roll: str = Form(...)):
    for student in students:
        if student["roll"] == roll:
            return {"error": f"Student with roll number {roll} already exists."}

    registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    student = {
        "name": name,
        "roll": roll,
        "registered_at": registration_time
    }

    students.append(student)

    with open(FILE_NAME, "w") as f:
        json.dump(students, f, indent=4)

    return {
        "message": f"{name} registered successfully!",
        "total": len(students),
        "student": student
    }

# Get all students
@app.get("/students")
def get_students():
    return students

# Delete student by roll number
@app.delete("/delete/{roll}")
def delete_student(roll: str):
    global students
    original_count = len(students)
    students = [s for s in students if s["roll"] != roll]

    if len(students) < original_count:
        with open(FILE_NAME, "w") as f:
            json.dump(students, f, indent=4)
        return {"message": f"Student with roll number {roll} deleted successfully."}
    else:
        return {"error": f"No student found with roll number {roll}."}

# Update student info
@app.put("/update")
def update_student(
    old_roll: str = Form(...),
    new_name: str = Form(...),
    new_roll: str = Form(...)
):
    found = False

    for student in students:
        if student["roll"] == old_roll:
            student["name"] = new_name
            student["roll"] = new_roll
            found = True
            break

    if found:
        with open(FILE_NAME, "w") as f:
            json.dump(students, f, indent=4)
        return {"message": f"Student with roll {old_roll} updated successfully."}
    else:
        return {"error": f"No student found with roll number {old_roll}."}

# Serve principal dashboard
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard():
    with open("admin_dashboard.html", "r") as f:
        return f.read()

# Register principal
@app.post("/register_principal")
def register_principal(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    for admin in principals:
        if admin["username"] == username:
            return {"error": "Username already exists."}

    principals.append({
        "username": username,
        "email": email,
        "password": password
    })
    with open(PRINCIPAL_FILE, "w") as f:
        json.dump(principals, f, indent=4)
    return {"message": "Principal registered successfully!"}

# Login principal
@app.post("/login_principal")
def login_principal(username: str = Form(...), password: str = Form(...)):
    for admin in principals:
        if admin["username"] == username and admin["password"] == password:
            return {"success": True, "message": "Login successful!"}
    return {"success": False, "error": "Invalid username or password."}
