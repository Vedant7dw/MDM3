Python Flask + SQLite (sqlite3) + HTML/CSS/JavaScript (Fetch API).

Run
Bash
pip install flask
python app.py        # http://localhost:5000
Database auto-initializes on startup. The database file is students.db.

Structure
Plaintext
app.py               Flask server, routes, payload validation, SQLite schema
templates/index.html Frontend (updates the page with fetch, no reload)
static/css/style.css Stylesheet for UI dashboard
static/js/main.js    Client-side AJAX logic & dynamic DOM rendering
REST API (JSON)
Method	Endpoint	Purpose
GET	/api/students	List all students
GET	/api/students?search=query	Search students by name or roll number
POST	/api/students	Add a student {name, roll_no, class_name, marks, contact}
PUT	/api/students/:id	Update student details {name, roll_no, class_name, marks, contact}
DELETE	/api/students/:id	Delete a student record
Validation and Edge Cases
Duplicate Roll Number: Adding or updating to a roll number already assigned to another student returns HTTP 409.

Payload Validation: Missing required fields, invalid contact numbers (must be 10 digits), or invalid marks (must be numeric between 0–100) return HTTP 400.

Missing Records: Updating or deleting a non-existent student ID returns HTTP 404.
