document.addEventListener('DOMContentLoaded', function() {
    const studentForm = document.getElementById('student-form');
    const professionalForm = document.getElementById('professional-form');
    const predictionResultDiv = document.getElementById('prediction-result');

    if (studentForm) {
        studentForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            predictionResultDiv.style.display = 'none';
            predictionResultDiv.textContent = '';

            const formData = new FormData(studentForm);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }

            // Convert age, CGPA, and work/study hours to numbers if they exist
            if (data['Age']) data['Age'] = parseInt(data['Age']);
            if (data['CGPA']) data['CGPA'] = parseFloat(data['CGPA']);
            if (data['Work/Study Hours']) data['Work/Study Hours'] = parseInt(data['Work/Study Hours']);

            try {
                const response = await fetch('/predict/student', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                predictionResultDiv.textContent = `Prediction Risk Score: ${result.prediction.toFixed(2)} / 10`;
                predictionResultDiv.style.display = 'block';
            } catch (error) {
                console.error('Error during student prediction:', error);
                predictionResultDiv.textContent = `Error: ${error.message}. Please try again.`;
                predictionResultDiv.style.display = 'block';
                predictionResultDiv.style.backgroundColor = '#ffe0e0'; // Light red for errors
                predictionResultDiv.style.borderColor = '#ffb3b3';
            }
        });
    }

    if (professionalForm) {
        const professionSelect = document.getElementById('profession');
        const degreeSelect = document.getElementById('prof-degree');

        // Function to dynamically load degrees based on profession
        async function loadDegreesForProfession(profession) {
            degreeSelect.innerHTML = '<option value="">Loading Degrees...</option>';
            if (!profession) {
                degreeSelect.innerHTML = '<option value="">Select your Degree</option>';
                return;
            }
            try {
                const response = await fetch(`/get_degrees?profession=${encodeURIComponent(profession)}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                degreeSelect.innerHTML = '<option value="">Select your Degree</option>'; // Clear existing options
                if (data.degrees && data.degrees.length > 0) {
                    data.degrees.forEach(degree => {
                        const option = document.createElement('option');
                        option.value = degree;
                        option.textContent = degree;
                        degreeSelect.appendChild(option);
                    });
                } else {
                    degreeSelect.innerHTML = '<option value="">No degrees found for this profession</option>';
                }
            } catch (error) {
                console.error('Error loading degrees:', error);
                degreeSelect.innerHTML = '<option value="">Error loading degrees</option>';
            }
        }

        // Initial load for professional form if a profession is pre-selected (unlikely in new form)
        // if (professionSelect.value) {
        //     loadDegreesForProfession(professionSelect.value);
        // }

        // Event listener for profession change
        professionSelect.addEventListener('change', function() {
            loadDegreesForProfession(this.value);
        });

        professionalForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            predictionResultDiv.style.display = 'none';
            predictionResultDiv.textContent = '';

            const formData = new FormData(professionalForm);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }

            // Convert age and work/study hours to numbers if they exist
            if (data['Age']) data['Age'] = parseInt(data['Age']);
            if (data['Work/Study Hours']) data['Work/Study Hours'] = parseInt(data['Work/Study Hours']);

            try {
                const response = await fetch('/predict/professional', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                predictionResultDiv.textContent = `Prediction Risk Score: ${result.prediction.toFixed(2)} / 10`;
                predictionResultDiv.style.display = 'block';
            } catch (error) {
                console.error('Error during professional prediction:', error);
                predictionResultDiv.textContent = `Error: ${error.message}. Please try again.`;
                predictionResultDiv.style.display = 'block';
                predictionResultDiv.style.backgroundColor = '#ffe0e0'; // Light red for errors
                predictionResultDiv.style.borderColor = '#ffb3b3';
            }
        });
    }
});
