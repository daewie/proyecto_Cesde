document.addEventListener('DOMContentLoaded', function() {
    let selectedSeats = new Set();
    const reserveButton = document.getElementById('reserve-button');

    document.querySelectorAll('.seat').forEach(seat => {
        seat.addEventListener('click', function() {
            if (this.classList.contains('occupied')) {
                return;
            }
            if (this.classList.contains('selected')) {
                this.classList.remove('selected');
                selectedSeats.delete(this.dataset.seatId);
            } else {
                this.classList.add('selected');
                selectedSeats.add(this.dataset.seatId);
            }
            updateSelection();
        });
    });

    function updateSelection() {
        const selectedSeatsElement = document.getElementById('selected-seats');
        const totalPriceElement = document.getElementById('total-price');

        if (selectedSeats.size > 0) {
            selectedSeatsElement.textContent = Array.from(selectedSeats).join(', ');
            let totalPrice = Array.from(selectedSeats).reduce((total, seatId) => {
                return total + parseInt(document.getElementById(seatId).dataset.price);
            }, 0);
            totalPriceElement.textContent = totalPrice;
            reserveButton.disabled = false;
        } else {
            selectedSeatsElement.textContent = 'Ninguno';
            totalPriceElement.textContent = '0';
            reserveButton.disabled = true;
        }
    }

    reserveButton.addEventListener('click', function() {
        if (selectedSeats.size > 0) {
            fetch('/reserve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ seats: Array.from(selectedSeats) }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    data.reserved_seats.forEach(seatId => {
                        const seatElement = document.getElementById(seatId);
                        seatElement.classList.add('occupied');
                        seatElement.classList.remove('selected');
                    });
                    selectedSeats.clear();
                    updateSelection();
                    alert(`Asientos reservados con éxito. Precio total: $${data.total_price}`);
                } else {
                    alert(data.message);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Ha ocurrido un error al reservar los asientos.');
            });
        }
    });
});