import sqlite3
import re
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DATABASE = 'students.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()

def validate_student_data(data, is_update=False):
    errors = []
    
    # Required Fields Check
    required_fields = ['name', 'roll_no', 'class_name', 'marks', 'contact']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Field '{field}' is required.")

    if errors:
        return errors

    # Name Validation
    if not isinstance(data['name'], str) or len(data['name'].strip()) < 2:
        errors.append("Name must be at least 2 characters long.")

    # Roll No Validation
    if not str(data['roll_no']).isalnum():
        errors.append("Roll Number must be alphanumeric.")

    # Contact Number Validation (10 digits)
    contact_str = str(data['contact']).strip()
    if not re.match(r'^\d{10}$', contact_str):
        errors.append("Contact number must be exactly 10 digits.")

    # Marks Validation (0 to 100)
    try:
        marks = float(data['marks'])
        if marks < 0 or marks > 100:
            errors.append("Marks must be between 0 and 100.")
    except ValueError:
        errors.append("Marks must be a valid number.")

    return errors

@app.route('/')
def index():
    return render_template('index.html')

# API Endpoints

# 1. Get All Students or Search
@app.route('/api/students', methods=['GET'])
def get_students():
    query_param = request.args.get('search', '').strip()
    conn = get_db_connection()
    
    if query_param:
        search_pattern = f"%{query_param}%"
        students = conn.execute(
            "SELECT * FROM students WHERE name LIKE ? OR roll_no LIKE ?",
            (search_pattern, search_pattern)
        ).fetchall()
    else:
        students = conn.execute("SELECT * FROM students").fetchall()
        
    conn.close()
    return jsonify([dict(student) for student in students]), 200

# 2. Add New Student
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json() or {}
    validation_errors = validate_student_data(data)
    
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400

    conn = get_db_connection()
    
    # Check Duplicate Roll Number
    existing = conn.execute("SELECT id FROM students WHERE roll_no = ?", (data['roll_no'],)).fetchone()
    if existing:
        conn.close()
        return jsonify({'errors': ['Roll Number already exists.']}), 409

    conn.execute(
        "INSERT INTO students (name, roll_no, class_name, marks, contact) VALUES (?, ?, ?, ?, ?)",
        (data['name'].strip(), data['roll_no'].strip(), data['class_name'].strip(), float(data['marks']), data['contact'].strip())
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Student record created successfully.'}), 201

# 3. Update Existing Student
@app.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json() or {}
    validation_errors = validate_student_data(data, is_update=True)
    
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400

    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    
    if not student:
        conn.close()
        return jsonify({'errors': ['Student record not found.']}), 404

    # Check Duplicate Roll Number for other records
    existing = conn.execute("SELECT id FROM students WHERE roll_no = ? AND id != ?", (data['roll_no'], student_id)).fetchone()
    if existing:
        conn.close()
        return jsonify({'errors': ['Roll Number is already assigned to another student.']}), 409

    conn.execute(
        "UPDATE students SET name = ?, roll_no = ?, class_name = ?, marks = ?, contact = ? WHERE id = ?",
        (data['name'].strip(), data['roll_no'].strip(), data['class_name'].strip(), float(data['marks']), data['contact'].strip(), student_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Student record updated successfully.'}), 200

# 4. Delete Student
@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    conn = get_db_connection()
    student = conn.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
    
    if not student:
        conn.close()
        return jsonify({'errors': ['Student record not found.']}), 404

    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Student record deleted successfully.'}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
