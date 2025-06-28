from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

# Enable frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# File to store data
FILE_NAME = "students.json"

# Load existing data or create empty list
if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r") as f:
        students = json.load(f)
else:
    students = []

@app.post("/register")
def register(name: str = Form(...), roll: str = Form(...)):
    # Check for duplicate roll numbers
    for student in students:
        if student["roll"] == roll:
            return {"error": f"Student with roll number {roll} already exists."}

    student = {"name": name, "roll": roll}
    students.append(student)

    # Save to file
    with open(FILE_NAME, "w") as f:
        json.dump(students, f, indent=4)

    return {"message": f"{name} registered successfully!", "total": len(students)}

@app.get("/students")
def get_students():
    return students
@app.delete("/delete/{roll}")
def delete_student(roll: str):
    global students
    original_count = len(students)

    # Filter out student with matching roll number
    students = [s for s in students if s["roll"] != roll]

    if len(students) < original_count:
        # Save updated list to JSON
        with open(FILE_NAME, "w") as f:
            json.dump(students, f, indent=4)
        return {"message": f"Student with roll number {roll} deleted successfully."}
    else:
        return {"error": f"No student found with roll number {roll}."}
    from fastapi import FastAPI, Form

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
    @app.get("/")
    def read_root():
    return {"message": "Welcome to Principal-Student App!"}
