document.addEventListener('DOMContentLoaded', function() {
    const studentForm = document.getElementById('student-form');
    const professionalForm = document.getElementById('professional-form');
    const predictionResultDiv = document.getElementById('prediction-result');
    const suggestionsList = document.getElementById('suggestions-list');
    const shuffleButton = document.getElementById('shuffle-suggestions');

    // Student Form Submission
    if (studentForm) {
        studentForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const formData = new FormData(studentForm);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            // Convert numerical fields to the correct type
            if (data['Age']) data['Age'] = parseInt(data['Age']);
            if (data['CGPA']) data['CGPA'] = parseFloat(data['CGPA']);
            if (data['Work/Study Hours']) data['Work/Study Hours'] = parseInt(data['Work/Study Hours']);

            try {
                const response = await fetch('/predict/student', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const result = await response.json();
                
                // Redirect to the result page
                if (result.redirect_url) {
                    window.location.href = result.redirect_url;
                } else {
                    console.error('Error: No redirect URL found in response.');
                    if (predictionResultDiv) {
                        predictionResultDiv.textContent = 'An unexpected error occurred. Please try again.';
                        predictionResultDiv.style.display = 'block';
                    }
                }
            } catch (error) {
                console.error('Error during student prediction:', error);
                if (predictionResultDiv) {
                    predictionResultDiv.textContent = `Error: ${error.message}. Please try again.`;
                    predictionResultDiv.style.display = 'block';
                }
            }
        });
    }

    // Professional Form and Degree Loading
    if (professionalForm) {
        const professionSelect = document.getElementById('profession');
        const degreeSelect = document.getElementById('prof-degree');

        async function loadDegreesForProfession(profession) {
            if (!degreeSelect) return;
            degreeSelect.innerHTML = '<option value="">Loading Degrees...</option>';
            if (!profession) {
                degreeSelect.innerHTML = '<option value="">Select your Degree</option>';
                return;
            }
            try {
                const response = await fetch(`/get_degrees?profession=${encodeURIComponent(profession)}`);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const data = await response.json();
                degreeSelect.innerHTML = '<option value="">Select your Degree</option>';
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

        if (professionSelect) {
            professionSelect.addEventListener('change', function() { loadDegreesForProfession(this.value); });
        }
        
        professionalForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const formData = new FormData(professionalForm);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            // Convert numerical fields
            if (data['Age']) data['Age'] = parseInt(data['Age']);
            if (data['Work/Study Hours']) data['Work/Study Hours'] = parseInt(data['Work/Study Hours']);

            try {
                const response = await fetch('/predict/professional', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const result = await response.json();

                // Redirect to the result page
                if (result.redirect_url) {
                    window.location.href = result.redirect_url;
                } else {
                    console.error('Error: No redirect URL found in response.');
                    if (predictionResultDiv) {
                        predictionResultDiv.textContent = 'An unexpected error occurred. Please try again.';
                        predictionResultDiv.style.display = 'block';
                    }
                }
            } catch (error) {
                console.error('Error during professional prediction:', error);
                if (predictionResultDiv) {
                    predictionResultDiv.textContent = `Error: ${error.message}. Please try again.`;
                    predictionResultDiv.style.display = 'block';
                }
            }
        });
    }

    // Suggestions Logic
    async function fetchAndDisplaySuggestions(userType) {
        if (!suggestionsList) return;
        suggestionsList.innerHTML = '<p>Loading suggestions...</p>';

        try {
            const response = await fetch(`/get_suggestions/${userType}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const suggestions = await response.json();

            suggestionsList.innerHTML = '';
            if (suggestions && suggestions.length > 0) {
                suggestions.forEach(suggestion => {
                    const div = document.createElement('div');
                    div.className = 'resource-item';
                    div.textContent = suggestion;
                    suggestionsList.appendChild(div);
                });
            } else {
                suggestionsList.innerHTML = '<p>No suggestions available at the moment.</p>';
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
            suggestionsList.innerHTML = `<p>Error loading suggestions: ${error.message}</p>`;
        }
    }

    // Initial fetch for suggestions on page load
    if (window.location.pathname.includes('student_resources')) {
        const userType = 'student';
        fetchAndDisplaySuggestions(userType);
        if (shuffleButton) {
            shuffleButton.addEventListener('click', () => fetchAndDisplaySuggestions(userType));
        }
    } else if (window.location.pathname.includes('professional_resources')) {
        const userType = 'professional';
        fetchAndDisplaySuggestions(userType);
        if (shuffleButton) {
            shuffleButton.addEventListener('click', () => fetchAndDisplaySuggestions(userType));
        }
    }
});