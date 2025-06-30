document.addEventListener('DOMContentLoaded', function() {
    const studentButton = document.getElementById('student-button');
    const professionalButton = document.getElementById('professional-button');
    const userTypeSelection = document.getElementById('user-type-selection');
    const studentFormContainer = document.getElementById('student-form-container');
    const professionalFormContainer = document.getElementById('professional-form-container');

    const studentForm = document.getElementById('student-prediction-form');
    const professionalForm = document.getElementById('professional-prediction-form');
    const predictionResultDiv = document.getElementById('prediction-result');

    // Event listeners for user type selection buttons
    if (studentButton) {
        studentButton.addEventListener('click', function() {
            if (userTypeSelection) userTypeSelection.style.display = 'none';
            if (studentFormContainer) studentFormContainer.style.display = 'block';
            if (professionalFormContainer) professionalFormContainer.style.display = 'none';
        });
    }

    if (professionalButton) {
        professionalButton.addEventListener('click', function() {
            if (userTypeSelection) userTypeSelection.style.display = 'none';
            if (studentFormContainer) studentFormContainer.style.display = 'none';
            if (professionalFormContainer) professionalFormContainer.style.display = 'block';
        });
    }

    // Function to handle form submission (reusable)
    function handleSubmit(event, form, endpoint) {
        event.preventDefault();

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
                // If response is not OK (e.g., 500 error), parse error message
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Something went wrong');
                });
            }
            return response.json();
        })
        .then(data => {
            if (predictionResultDiv) {
                predictionResultDiv.innerText = 'Prediction Result: ' + data.prediction;
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
});
