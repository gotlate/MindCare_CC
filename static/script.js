document.addEventListener('DOMContentLoaded', function() {
    const studentButton = document.getElementById('student-button');
    const professionalButton = document.getElementById('professional-button');
    const userTypeSelection = document.getElementById('user-type-selection');
    const studentFormContainer = document.getElementById('student-form-container');
    const professionalFormContainer = document.getElementById('professional-form-container');
    const professionalProfessionSelect = document.getElementById('professional_profession');
    const professionalDegreeSelect = document.getElementById('professional_degree');
    const predictionResultDiv = document.getElementById('prediction-result');

    // Function to show/hide forms
    function showStudentForm() {
        studentFormContainer.style.display = 'block';
        professionalFormContainer.style.display = 'none';
        userTypeSelection.style.display = 'none';
        predictionResultDiv.innerText = '';
    }

    function showProfessionalForm() {
        studentFormContainer.style.display = 'none';
        professionalFormContainer.style.display = 'block';
        userTypeSelection.style.display = 'none';
        predictionResultDiv.innerText = '';
        updateProfessionalDegreeDropdown();
    }
    function showUserTypeSelection() {
        studentFormContainer.style.display = 'none';
        professionalFormContainer.style.display = 'none';
        userTypeSelection.style.display = 'flex';
        predictionResultDiv.innerText = '';
    }
    // Attach event listeners to buttons
    studentButton.addEventListener('click', showStudentForm);
    professionalButton.addEventListener('click', showProfessionalForm);

    // Function to handle form submission (reusable)
    function handleSubmit(event, form, endpoint) {
        event.preventDefault();

        // Client-side validation before sending
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const formData = new FormData(form);
        const jsonData = {};

        formData.forEach((value, key) => {
            jsonData[key] = value;
        });

        console.log(`Data being sent to ${endpoint}:`, jsonData);

        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jsonData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Something went wrong');
                });
            }
            return response.json();
        })
        .then(data => {
            predictionResultDiv.innerText = 'Prediction Risk Score: ' + data.prediction.toFixed(2) + ' / 10';
            showUserTypeSelection()
        })
        .catch(error => {
            console.error('Error:', error);
            predictionResultDiv.innerText = 'Error: ' + error.message;
            showUserTypeSelection()
        });
    }

    // Attach event listeners to forms
    const studentForm = document.getElementById('student-prediction-form');
    if (studentForm) {
        studentForm.addEventListener('submit', (event) => {
            handleSubmit(event, studentForm, '/predict/student');
        });
    }

    const professionalForm = document.getElementById('professional-prediction-form');
    if (professionalForm) {
        professionalForm.addEventListener('submit', (event) => {
            handleSubmit(event, professionalForm, '/predict/professional');
        });
    }

    // Function to update professional degree dropdown based on profession selection
    function updateProfessionalDegreeDropdown() {
        const profession = professionalProfessionSelect.value;

        if (profession) {
            fetch(`/get_degrees?profession=${encodeURIComponent(profession)}`)
                .then(response => response.json())
                .then(data => {
                    professionalDegreeSelect.innerHTML = '<option value="">Select Degree</option>';
                    data.degrees.forEach(degree => {
                        const option = document.createElement('option');
                        option.value = degree;
                        option.textContent = degree;
                        professionalDegreeSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error fetching degrees:', error);
                    professionalDegreeSelect.innerHTML = '<option value="">Error loading degrees</option>';
                });
        } else {
            professionalDegreeSelect.innerHTML = '<option value="">Select Profession first</option>';
        }
    }

    // Attach event listener to the professional profession select dropdown
    if (professionalProfessionSelect) {
        professionalProfessionSelect.addEventListener('change', updateProfessionalDegreeDropdown);
    }
});