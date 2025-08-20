const BASE_URL = "http://127.0.0.1:8000";
let principalUsername = "";
let principalPassword = "";

// ---------------- Principal Registration ----------------
function registerPrincipal() {
    const username = document.getElementById("regUsername").value;
    const email = document.getElementById("regEmail").value;
    const password = document.getElementById("regPassword").value;

    fetch(`${BASE_URL}/register_principal`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `username=${encodeURIComponent(username)}&email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("registerMessage").innerText = data.message || data.detail || data.error;
    })
    .catch(err => console.error(err));
}

// ---------------- Principal Login ----------------
function loginPrincipal() {
    const username = document.getElementById("loginUsername").value;
    const password = document.getElementById("loginPassword").value;

    fetch(`${BASE_URL}/login_principal`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            principalUsername = username;
            principalPassword = password;
            document.getElementById("registerSection").classList.add("hidden");
            document.getElementById("loginSection").classList.add("hidden");
            document.getElementById("dashboard").classList.remove("hidden");

            loadStudents();
            loadLeaveRequests();
            loadEventRequests();
            loadEmergencyRequests();
        } else {
            document.getElementById("loginError").innerText = data.message || data.detail || "Login failed";
        }
    })
    .catch(err => console.error(err));
}

// ---------------- Students ----------------
function loadStudents() {
    fetch(`${BASE_URL}/students`)
    .then(res => res.json())
    .then(data => {
        const table = document.getElementById("studentTable");
        table.innerHTML = "";
        data.forEach(student => {
            table.innerHTML += `<tr>
                <td>${student.name}</td>
                <td>${student.roll}</td>
                <td>${student.branch || "N/A"}</td>
                <td>${student.year || "N/A"}</td>
                <td>${student.registered_at || ""}</td>
                <td><button onclick="deleteStudent('${student.roll}')">Delete</button></td>
            </tr>`;
        });
    });
}

function deleteStudent(roll) {
    fetch(`${BASE_URL}/delete_student/${roll}`, { method: "DELETE" })
    .then(res => res.json())
    .then(data => {
        alert(data.message || data.detail || data.error);
        loadStudents();
    });
}

// ---------------- Leave Requests ----------------
function loadLeaveRequests() {
    const body = `role=principal&username=${encodeURIComponent(principalUsername)}&password=${encodeURIComponent(principalPassword)}`;
    fetch(`${BASE_URL}/view_requests`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body
    })
    .then(res => res.json())
    .then(data => {
        let html = `<table class="table"><thead>
            <tr>
                <th>ID</th><th>Name</th><th>Roll</th><th>Reason</th>
                <th>Start</th><th>Return</th><th>Days</th><th>Status</th>
                <th>Response</th><th>Action</th>
            </tr>
        </thead><tbody>`;
        data.forEach(req => {
            html += `<tr>
                <td>${req.id}</td>
                <td>${req.name}</td>
                <td>${req.roll}</td>
                <td>${req.reason}</td>
                <td>${req.start_date}</td>
                <td>${req.return_date}</td>
                <td>${req.total_days}</td>
                <td>${req.status}</td>
                <td>${req.response || ""}</td>
                <td>
                    <select id="leave_status_${req.id}">
                        <option ${req.status === "Approved" ? "selected" : ""}>Approved</option>
                        <option ${req.status === "Rejected" ? "selected" : ""}>Rejected</option>
                        <option ${req.status === "Paused" ? "selected" : ""}>Paused</option>
                    </select>
                    <input type="text" id="leave_response_${req.id}" placeholder="Response" value="${req.response || ""}">
                    <button onclick="submitLeaveStatus(${req.id})">Submit</button>
                </td>
            </tr>`;
        });
        html += "</tbody></table>";
        document.getElementById("requestsTable").innerHTML = html;
    });
}

function submitLeaveStatus(id) {
    const status = document.getElementById(`leave_status_${id}`).value;
    const response = document.getElementById(`leave_response_${id}`).value;
    const body = `request_id=${id}&status=${encodeURIComponent(status)}&response=${encodeURIComponent(response)}&username=${encodeURIComponent(principalUsername)}&password=${encodeURIComponent(principalPassword)}`;

    fetch(`${BASE_URL}/update_status`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || data.detail || data.error);
        loadLeaveRequests();
    });
}

// ---------------- Event Requests ----------------
function loadEventRequests() {
    fetch(`${BASE_URL}/get_event_requests?username=${encodeURIComponent(principalUsername)}&password=${encodeURIComponent(principalPassword)}`)
    .then(res => res.json())
    .then(data => {
        let html = `<table class="table"><thead>
            <tr><th>ID</th><th>Title</th><th>Date</th><th>Location</th><th>Description</th>
            <th>Status</th><th>Response</th><th>Actions</th></tr></thead><tbody>`;
        data.forEach(e => {
            html += `<tr>
                <td>${e.id}</td>
                <td><input id="event_title_${e.id}" value="${e.title}"></td>
                <td><input id="event_date_${e.id}" type="date" value="${e.date}"></td>
                <td><input id="event_location_${e.id}" value="${e.location}"></td>
                <td><input id="event_desc_${e.id}" value="${e.description}"></td>
                <td>
                    <select id="event_status_${e.id}">
                        <option ${e.status==="Approved"?"selected":""}>Approved</option>
                        <option ${e.status==="Rejected"?"selected":""}>Rejected</option>
                        <option ${e.status==="Pending"?"selected":""}>Pending</option>
                    </select>
                </td>
                <td>${e.response || ""}</td>
                <td>
                    <button onclick="updateEvent(${e.id})">Update</button>
                    <button onclick="deleteEvent(${e.id})">Delete</button>
                </td>
            </tr>`;
        });
        html += "</tbody></table>";
        document.getElementById("eventTable").innerHTML = html;
    });
}

function updateEvent(eventId) {
    const title = document.getElementById(`event_title_${eventId}`).value;
    const date = document.getElementById(`event_date_${eventId}`).value;
    const location = document.getElementById(`event_location_${eventId}`).value;
    const description = document.getElementById(`event_desc_${eventId}`).value;
    const status = document.getElementById(`event_status_${eventId}`).value;

    const body = `eventId=${eventId}&title=${encodeURIComponent(title)}&date=${encodeURIComponent(date)}&location=${encodeURIComponent(location)}&description=${encodeURIComponent(description)}&status=${encodeURIComponent(status)}&principalusername=${encodeURIComponent(principalUsername)}&principalpassword=${encodeURIComponent(principalPassword)}`;

    fetch(`${BASE_URL}/update_event`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || data.detail || "Event updated");
        loadEventRequests();
    })
    .catch(err => alert("Error: " + err));
}

function deleteEvent(eventId) {
    if (!confirm("Are you sure you want to delete this event?")) return;

    const body = `eventId=${eventId}&principalusername=${encodeURIComponent(principalUsername)}&principalpassword=${encodeURIComponent(principalPassword)}`;

    fetch(`${BASE_URL}/delete_event`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || data.detail || "Event deleted");
        loadEventRequests();
    })
    .catch(err => alert("Error: " + err));
}


// ---------------- Emergency Requests ----------------
function loadEmergencyRequests() {
    fetch(`${BASE_URL}/get_emergencies?username=${encodeURIComponent(principalUsername)}&password=${encodeURIComponent(principalPassword)}`)
    .then(res => res.json())
    .then(data => {
        let html = `<table class="table"><thead>
            <tr><th>ID</th><th>Name</th><th>Roll</th><th>Type</th><th>Description</th><th>Status</th><th>Response</th><th>Action</th></tr></thead><tbody>`;
        data.forEach(e => {
            html += `<tr>
                <td>${e.id}</td>
                <td>${e.name}</td>
                <td>${e.roll}</td>
                <td>${e.emergency_type}</td>
                <td>${e.description}</td>
                <td>
                    <select id="emergency_status_${e.id}">
                        <option ${e.status==="Approved"?"selected":""}>Approved</option>
                        <option ${e.status==="Rejected"?"selected":""}>Rejected</option>
                        <option ${e.status==="Pending"?"selected":""}>Pending</option>
                    </select>
                </td>
                <td><input id="emergency_response_${e.id}" value="${e.response || ""}"></td>
                <td><button onclick="updateEmergency(${e.id})">Submit</button></td>
            </tr>`;
        });
        html += "</tbody></table>";
        document.getElementById("emergencyTable").innerHTML = html;
    });
}

function updateEmergency(id) {
    const status = document.getElementById(`emergency_status_${id}`).value;
    const response = document.getElementById(`emergency_response_${id}`).value;
    const body = `id=${id}&status=${encodeURIComponent(status)}&response=${encodeURIComponent(response)}&username=${encodeURIComponent(principalUsername)}&password=${encodeURIComponent(principalPassword)}`;

    fetch(`${BASE_URL}/update_emergency_status`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || data.detail || data.error);
        loadEmergencyRequests();
    });
}
