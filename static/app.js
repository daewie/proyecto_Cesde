document.addEventListener('DOMContentLoaded', function() {
    let selectedSeat = null;
    const reserveButton = document.getElementById('reserve-button');

    document.querySelectorAll('.seat').forEach(seat => {
        seat.addEventListener('click', function() {
            if (this.classList.contains('occupied')) {
                return;
            }
            if (selectedSeat) {
                selectedSeat.classList.remove('selected');
            }
            selectedSeat = this;
            this.classList.add('selected');
            document.getElementById('selected-seat').textContent = this.dataset.seatId;
            document.getElementById('seat-price').textContent = this.dataset.price;
            reserveButton.disabled = false;
        });
    });

    reserveButton.addEventListener('click', function() {
        if (selectedSeat) {
            fetch('/reserve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ seat: selectedSeat.dataset.seatId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    selectedSeat.classList.add('occupied');
                    selectedSeat.classList.remove('selected');
                    document.getElementById('selected-seat').textContent = 'Ninguno';
                    document.getElementById('seat-price').textContent = '0';
                    reserveButton.disabled = true;
                    alert(data.message);
                } else {
                    alert(data.message);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Ha ocurrido un error al reservar el asiento.');
            });
        }
    });
});
