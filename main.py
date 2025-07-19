from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

FILE_NAME = "students.json"

if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r") as f:
        students = json.load(f)
else:
    students = []

@app.get("/")
def home():
    return {"message": "Welcome to Principal-Student App!"}

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

@app.get("/students")
def get_students():
    return students

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
