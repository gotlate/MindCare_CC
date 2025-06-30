document.addEventListener('DOMContentLoaded', function() {
    const studentButton = document.getElementById('student-button');
    const professionalButton = document.getElementById('professional-button');
    const userTypeSelection = document.getElementById('user-type-selection');
    const studentFormContainer = document.getElementById('student-form-container');
    const professionalFormContainer = document.getElementById('professional-form-container');

    const studentForm = document.getElementById('student-prediction-form');
    const professionalForm = document.getElementById('professional-prediction-form');
    const predictionResultDiv = document.getElementById('prediction-result');

    const professionalProfessionInput = document.getElementById('professional_profession');
    const professionalDegreeSelect = document.getElementById('professional_degree');
    const studentDegreeSelect = document.getElementById('student_degree');

    // Populate static student degrees
    const studentDegrees = ["B.Tech", "B.Sc", "B.Com", "B.A", "M.Tech", "M.Sc", "M.Com", "M.A", "PhD"];
    function populateStudentDegrees() {
        if (studentDegreeSelect) {
            studentDegreeSelect.innerHTML = '<option value="">Select Degree</option>';
            studentDegrees.forEach(degree => {
                const option = document.createElement('option');
                option.value = degree;
                option.textContent = degree;
                studentDegreeSelect.appendChild(option);
            });
        }
    }
    populateStudentDegrees(); // Populate on load

    // Event listeners for user type selection buttons
    if (studentButton) {
        studentButton.addEventListener('click', function() {
            if (userTypeSelection) userTypeSelection.style.display = 'none';
            if (studentFormContainer) studentFormContainer.style.display = 'block';
            if (professionalFormContainer) professionalFormContainer.style.display = 'none';
            predictionResultDiv.innerText = ''; // Clear previous results
        });
    }

    if (professionalButton) {
        professionalButton.addEventListener('click', function() {
            if (userTypeSelection) userTypeSelection.style.display = 'none';
            if (studentFormContainer) studentFormContainer.style.display = 'none';
            if (professionalFormContainer) professionalFormContainer.style.display = 'block';
            predictionResultDiv.innerText = ''; // Clear previous results
        });
    }

    // Function to handle form submission (reusable)
    function handleSubmit(event, form, endpoint) {
        event.preventDefault();

        // Client-side validation before sending
        if (!form.checkValidity()) {
            // If the form is invalid, the browser's built-in validation messages will show
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
            if (predictionResultDiv) {
                predictionResultDiv.innerText = 'Prediction Result: ' + data.prediction.toFixed(2);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (predictionResultDiv) {
                predictionResultDiv.innerText = 'Error: ' + error.message;
            }
        });
    }

    // Event listener for student form submission
    if (studentForm) {
        studentForm.addEventListener('submit', function(event) {
            handleSubmit(event, studentForm, '/predict/student');
        });
    }

    // Event listener for professional form submission
    if (professionalForm) {
        professionalForm.addEventListener('submit', function(event) {
            handleSubmit(event, professionalForm, '/predict/professional');
        });
    }

    // Function to update professional degree dropdown based on profession input
    function updateProfessionalDegreeDropdown() {
        const profession = professionalProfessionInput.value.trim().toUpperCase();
        if (profession.length > 2) { // Only fetch if profession has at least 3 characters
            fetch(`/get_degrees?profession=${encodeURIComponent(profession)})`)
                .then(response => response.json())
                .then(data => {
                    if (professionalDegreeSelect) {
                        professionalDegreeSelect.innerHTML = '<option value="">Select Degree</option>';
                        if (data.degrees && data.degrees.length > 0) {
                            data.degrees.forEach(degree => {
                                const option = document.createElement('option');
                                option.value = degree;
                                option.textContent = degree;
                                professionalDegreeSelect.appendChild(option);
                            });
                        } else {
                            // Fallback if no specific degrees found
                            const fallbackOption = document.createElement('option');
                            fallbackOption.value = 'Other';
                            fallbackOption.textContent = 'Other / Not Applicable';
                            professionalDegreeSelect.appendChild(fallbackOption);
                        }
                    }
                })
                .catch(error => {
                    console.error('Error fetching degrees:', error);
                    if (professionalDegreeSelect) {
                        professionalDegreeSelect.innerHTML = '<option value="">Error loading degrees</option>';
                    }
                });
        } else {
            // Clear or set default if profession input is too short
            if (professionalDegreeSelect) {
                professionalDegreeSelect.innerHTML = '<option value="">Enter Profession to see degrees</option>';
            }
        }
    }

    // Attach event listener to the professional profession input
    if (professionalProfessionInput) {
        professionalProfessionInput.addEventListener('input', updateProfessionalDegreeDropdown);
    }
});
