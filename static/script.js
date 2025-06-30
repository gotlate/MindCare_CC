document.addEventListener('DOMContentLoaded', function() {
    const studentButton = document.getElementById('student-button');
    const professionalButton = document.getElementById('professional-button');
    let userTypeSelection = document.getElementById('user-type-selection');
    let studentFormContainer = document.getElementById('student-form-container');
    let professionalFormContainer = document.getElementById('professional-form-container');

    let studentForm = document.getElementById('student-prediction-form');
    let professionalForm = document.getElementById('professional-prediction-form');
    let predictionResultDiv = document.getElementById('prediction-result');

    let professionalProfessionSelect = document.getElementById('professional_profession');
    let professionalDegreeSelect = document.getElementById('professional_degree');

    function ensureElementsExist() {
        userTypeSelection = document.getElementById('user-type-selection');
        studentFormContainer = document.getElementById('student-form-container');
        professionalFormContainer = document.getElementById('professional-form-container');
        studentForm = document.getElementById('student-prediction-form');
        professionalForm = document.getElementById('professional-prediction-form');
        predictionResultDiv = document.getElementById('prediction-result');
        professionalProfessionSelect = document.getElementById('professional_profession');
        professionalDegreeSelect = document.getElementById('professional_degree');
    }

    // Function to show/hide forms
    function showStudentForm() {
        ensureElementsExist()
        if(studentFormContainer) studentFormContainer.style.display = 'block';
        if(professionalFormContainer) professionalFormContainer.style.display = 'none';
        if(userTypeSelection) userTypeSelection.style.display = 'none';
        if(predictionResultDiv) predictionResultDiv.innerText = '';
    }

    function showProfessionalForm() {
         ensureElementsExist()
        if(studentFormContainer) studentFormContainer.style.display = 'none';
        if(professionalFormContainer) professionalFormContainer.style.display = 'block';
        if(userTypeSelection) userTypeSelection.style.display = 'none';
        if(predictionResultDiv) predictionResultDiv.innerText = '';
        updateProfessionalDegreeDropdown();
    }
    function showUserTypeSelection() {
         ensureElementsExist()
        if(studentFormContainer) studentFormContainer.style.display = 'none';
        if(professionalFormContainer) professionalFormContainer.style.display = 'none';
        if(userTypeSelection) userTypeSelection.style.display = 'flex';
        if(predictionResultDiv) predictionResultDiv.innerText = '';
    }
    // Attach event listeners to buttons
    if (studentButton) {
        studentButton.addEventListener('click', showStudentForm);
    }
    if (professionalButton) {
        professionalButton.addEventListener('click', showProfessionalForm);
    }

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
            if(predictionResultDiv) predictionResultDiv.innerText = 'Prediction Risk Score: ' + data.prediction.toFixed(2) + ' / 10';
            showUserTypeSelection()
        })
        .catch(error => {
            console.error('Error:', error);
            if(predictionResultDiv) predictionResultDiv.innerText = 'Error: ' + error.message;
            showUserTypeSelection()
        });
    }

    // Attach event listeners to forms
    if (studentForm) {
        studentForm.addEventListener('submit', (event) => {
            handleSubmit(event, studentForm, '/predict/student');
        });
    }

    if (professionalForm) {
        professionalForm.addEventListener('submit', (event) => {
            handleSubmit(event, professionalForm, '/predict/professional');
        });
    }

    // Function to update professional degree dropdown based on profession selection
    function updateProfessionalDegreeDropdown() {
        if(!professionalProfessionSelect || !professionalDegreeSelect) return; // Exit if they dont exist yet

        const profession = professionalProfessionSelect.value;

        if (profession) {
            fetch(`/get_degrees?profession=${encodeURIComponent(profession)}`)
                .then(response => response.json())
                .then(data => {
                    professionalDegreeSelect.innerHTML = '<option value="">Select Degree</option>';
                    if (data.degrees && data.degrees.length > 0) {
                        data.degrees.forEach(degree => {
                            const option = document.createElement('option');
                            option.value = degree;
                            option.textContent = degree;
                            professionalDegreeSelect.appendChild(option);
                        });
                    } else {
                        const fallbackOption = document.createElement('option');
                        fallbackOption.value = 'Other';
                        fallbackOption.textContent = 'Other / Not Applicable';
                        professionalDegreeSelect.appendChild(fallbackOption);
                    }
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
    if(professionalProfessionSelect) {
        professionalProfessionSelect.addEventListener('change', updateProfessionalDegreeDropdown);
    }
    ensureElementsExist();
});