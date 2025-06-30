document.getElementById('prediction-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const form = event.target;
    const jsonData = {};

    // Convert form data to JSON
    Array.from(form.elements).forEach(input => {
        if (input.name) {
            jsonData[input.name] = input.value;
        }
    });

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData),
    })
    .then(response => response.json())
    .then(data => {
        // Display the prediction result (you'll need to add an element to your HTML for this)
        document.getElementById('prediction-result').innerText = 'Prediction Result: ' + data.prediction;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
