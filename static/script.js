document.addEventListener('DOMContentLoaded', function() {
    const studentButton = document.getElementById('student-button');
    const professionalButton = document.getElementById('professional-button');
    const userTypeSelection = document.getElementById('user-type-selection');
    const studentFormContainer = document.getElementById('student-form-container');
    const professionalFormContainer = document.getElementById('professional-form-container');

    const studentForm = document.getElementById('student-prediction-form');
    const professionalForm = document.getElementById('professional-prediction-form');
    const predictionResultDiv = document.getElementById('prediction-result');

    const professionalProfessionSelect = document.getElementById('professional_profession');
    const professionalDegreeSelect = document.getElementById('professional_degree');

    // Event listeners for user type selection buttons
    if (studentButton) {
        studentButton.addEventListener('click', function() {
            userTypeSelection.style.display = 'none';
            studentFormContainer.style.display = 'block';
            professionalFormContainer.style.display = 'none';
            predictionResultDiv.innerText = ''; // Clear previous results
        });
    }

    if (professionalButton) {
        professionalButton.addEventListener('click', function() {
            userTypeSelection.style.display = 'none';
            studentFormContainer.style.display = 'none';
            professionalFormContainer.style.display = 'block';
            predictionResultDiv.innerText = ''; // Clear previous results
            // Trigger degree dropdown update when professional form is shown
            updateProfessionalDegreeDropdown();
        });
    }

    // Function to handle form submission (reusable)
    function handleSubmit(event, form, endpoint) {
        event.preventDefault();

        // Client-side validation before sending
        if (!form.checkValidity()) {
            form.reportValidity(); // This will show the browser's built-in validation messages
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
                predictionResultDiv.innerText = 'Prediction Risk Score: ' + data.prediction.toFixed(2) + ' / 10';
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

    // Function to update professional degree dropdown based on profession selection
    function updateProfessionalDegreeDropdown() {
        const profession = professionalProfessionSelect.value;
        
        if (profession) { // Only fetch if a profession is selected
            fetch(`/get_degrees?profession=${encodeURIComponent(profession)}`)
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
            if (professionalDegreeSelect) {
                professionalDegreeSelect.innerHTML = '<option value="">Select Profession first</option>';
            }
        }
    }
    
    // Attach event listener to the professional profession select dropdown
    if(professionalProfessionSelect) {
        professionalProfessionSelect.addEventListener('change', updateProfessionalDegreeDropdown);
    }
});