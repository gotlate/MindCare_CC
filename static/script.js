document.getElementById('predictionForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const form = event.target;
    const formData = new FormData(form);
    const jsonData = {};

    // Convert form data to JSON
    formData.forEach((value, key) => {
        jsonData[key] = value;
    });

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonData),
    })
    .then(response => response.json())
    .then(data => {
        // Display the prediction result (you'll need to add an element to your HTML for this)
        document.getElementById('predictionResult').innerText = 'Risk Score: ' + data.risk_score.toFixed(2);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
