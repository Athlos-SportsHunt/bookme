<script></script>
document.querySelector('#createTurfForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const turfName = document.getElementById('turfName').value;
    const pricePerHour = document.getElementById('pricePerHour').value;
    const venueId = document.getElementById('venueId').value;

    const nameError = document.getElementById('nameError');
    const priceError = document.getElementById('priceError');
    const successMessage = document.getElementById('successMessage');

    // Reset error messages
    nameError.style.display = 'none';
    priceError.style.display = 'none';
    successMessage.style.display = 'none';

    // Validate inputs
    let valid = true;

    if (!turfName) {
        nameError.style.display = 'block';
        valid = false;
    }

    if (pricePerHour <= 0 || isNaN(pricePerHour)) {
        priceError.style.display = 'block';
        valid = false;
    }

    if (!valid) {
        return;
    }

    try {
        const response = await fetch('{% url "api:create_turf" venue_id %}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify({
                turf_name: turfName,
                price_per_hr: parseFloat(pricePerHour),
                venue: parseInt(venueId),
            }),
        });

        if (response.ok) {
            successMessage.style.display = 'block';
            setTimeout(() => {
                window.location.href = `{% url 'host:venue' venue_id %}`;
            }, 1500);
        } else {
            alert('Failed to create turf. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while creating the turf.');
    }
});