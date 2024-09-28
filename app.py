from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Definimos la estructura del avión y los precios
airplane = {
    'second_floor': {'rows': 2, 'seats_per_row': 4, 'price': 750},
    'first_class': {'rows': 2, 'seats_per_row': 4, 'price': 500},
    'business': {'rows': 3, 'seats_per_row': 6, 'price': 250},
    'economy': {'rows': 10, 'seats_per_row': 6, 'price': 100},
}

# Inicializamos los asientos como disponibles
seats = {}
for class_type, config in airplane.items():
    for row in range(1, config['rows'] + 1):
        for seat in range(1, config['seats_per_row'] + 1):
            seat_id = f"{class_type[0].upper()}{row}{chr(64+seat)}"
            seats[seat_id] = {'occupied': False, 'price': config['price']}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reservation')
def reservation():
    seats_html = "<div class='airplane'>"
    seats_html += "<div class='second-floor mb-12'><h2 class='text-2xl font-bold mb-4 text-center'>Second Floor</h2>"
    for class_type, config in airplane.items():
        if class_type == 'second_floor':
            seats_html += generate_seats_html(class_type, config)
    seats_html += "</div><div class='first-floor'>"
    for class_type, config in airplane.items():
        if class_type != 'second_floor':
            seats_html += generate_seats_html(class_type, config)
    seats_html += "</div></div>"
    
    return render_template('reservation.html', seats=seats_html)

def generate_seats_html(class_type, config):
    html = f'<div class="mb-8"><h2 class="text-xl font-semibold mb-2 text-center">{class_type.replace("_", " ").title()}</h2>'
    for row in range(1, config['rows'] + 1):
        html += '<div class="flex justify-center mb-2">'
        for seat in range(1, config['seats_per_row'] + 1):
            seat_id = f"{class_type[0].upper()}{row}{chr(64+seat)}"
            seat_info = seats[seat_id]
            occupied = 'occupied' if seat_info['occupied'] else ''
            html += f"""
                <div id='{seat_id}' data-seat-id='{seat_id}' data-price='{seat_info['price']}'
                     class='seat w-10 h-10 rounded m-1 flex items-center justify-center text-sm font-semibold bg-{class_type} hover:bg-{class_type}/80 cursor-pointer {occupied}'>
                    {seat_id}
                </div>
            """
            if seat == config['seats_per_row'] // 2:
                html += '<div class="w-8"></div>'  # Pasillo
        html += '</div>'
    html += '</div>'
    return html

@app.route('/reserve', methods=['POST'])
def reserve_seat():
    data = request.json
    seat_ids = data.get('seats', [])
    
    if not seat_ids:
        return jsonify({'success': False, 'message': 'No se seleccionaron asientos'})
    
    total_price = 0
    reserved_seats = []
    
    for seat_id in seat_ids:
        if seat_id not in seats:
            return jsonify({'success': False, 'message': f'Asiento inválido: {seat_id}'})
        
        if seats[seat_id]['occupied']:
            return jsonify({'success': False, 'message': f'El asiento {seat_id} ya está ocupado'})
        
        seats[seat_id]['occupied'] = True
        total_price += seats[seat_id]['price']
        reserved_seats.append(seat_id)
    
    return jsonify({
        'success': True,
        'message': 'Asientos reservados con éxito',
        'reserved_seats': reserved_seats,
        'total_price': total_price
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)