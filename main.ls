document.addEventListener('DOMContentLoaded', () => {
    const studentForm = document.getElementById('student-form');
    const studentIdInput = document.getElementById('student-id');
    const nameInput = document.getElementById('name');
    const rollNoInput = document.getElementById('roll_no');
    const classInput = document.getElementById('class_name');
    const marksInput = document.getElementById('marks');
    const contactInput = document.getElementById('contact');
    const tableBody = document.getElementById('student-table-body');
    const alertContainer = document.getElementById('alert-container');
    const formTitle = document.getElementById('form-title');
    const submitBtn = document.getElementById('submit-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resetBtn = document.getElementById('reset-btn');

    fetchStudents();

    // Submit Form (Add or Edit)
    studentForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const studentData = {
            name: nameInput.value.trim(),
            roll_no: rollNoInput.value.trim(),
            class_name: classInput.value.trim(),
            marks: parseFloat(marksInput.value),
            contact: contactInput.value.trim()
        };

        // Client-Side Validation
        if (!/^\d{10}$/.test(studentData.contact)) {
            showAlert(['Contact number must be exactly 10 digits.'], 'danger');
            return;
        }

        const isEdit = Boolean(studentIdInput.value);
        const url = isEdit ? `/api/students/${studentIdInput.value}` : '/api/students';
        const method = isEdit ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(studentData)
            });

            const result = await response.json();

            if (response.ok) {
                showAlert([result.message], 'success');
                resetForm();
                fetchStudents();
            } else {
                showAlert(result.errors || ['An error occurred.'], 'danger');
            }
        } catch (err) {
            showAlert(['Failed to communicate with the server.'], 'danger');
        }
    });

    // Fetch and Display Records
    async function fetchStudents(searchQuery = '') {
        try {
            const response = await fetch(`/api/students?search=${encodeURIComponent(searchQuery)}`);
            const data = await response.json();

            tableBody.innerHTML = '';

            if (data.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center;">No student records found.</td></tr>`;
                return;
            }

            data.forEach(student => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${student.id}</td>
                    <td>${student.name}</td>
                    <td>${student.roll_no}</td>
                    <td>${student.class_name}</td>
                    <td>${student.marks}</td>
                    <td>${student.contact}</td>
                    <td>
                        <button class="edit" onclick='populateEdit(${JSON.stringify(student)})'>Edit</button>
                        <button class="danger" onclick="deleteStudent(${student.id})">Delete</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        } catch (err) {
            showAlert(['Error loading student records.'], 'danger');
        }
    }

    // Populate Form for Editing
    window.populateEdit = function(student) {
        studentIdInput.value = student.id;
        nameInput.value = student.name;
        rollNoInput.value = student.roll_no;
        classInput.value = student.class_name;
        marksInput.value = student.marks;
        contactInput.value = student.contact;

        formTitle.textContent = 'Edit Student Record';
        submitBtn.textContent = 'Update Record';
        cancelBtn.style.display = 'inline-block';
    };

    // Delete Student
    window.deleteStudent = async function(id) {
        if (!confirm('Are you sure you want to delete this student record?')) return;

        try {
            const response = await fetch(`/api/students/${id}`, { method: 'DELETE' });
            const result = await response.json();

            if (response.ok) {
                showAlert([result.message], 'success');
                fetchStudents();
            } else {
                showAlert(result.errors || ['Failed to delete record.'], 'danger');
            }
        } catch (err) {
            showAlert(['Error processing delete request.'], 'danger');
        }
    };

    // Search and Reset
    searchBtn.addEventListener('click', () => fetchStudents(searchInput.value));
    resetBtn.addEventListener('click', () => {
        searchInput.value = '';
        fetchStudents();
    });

    cancelBtn.addEventListener('click', resetForm);

    function resetForm() {
        studentIdInput.value = '';
        studentForm.reset();
        formTitle.textContent = 'Add Student Record';
        submitBtn.textContent = 'Save Record';
        cancelBtn.style.display = 'none';
    }

    function showAlert(messages, type) {
        alertContainer.innerHTML = `
            <div class="alert alert-${type}">
                ${messages.join('<br>')}
            </div>
        `;
        setTimeout(() => alertContainer.innerHTML = '', 4000);
    }
});
