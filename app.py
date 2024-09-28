from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Definimos la estructura del avión y los precios
airplane = {
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
    seats_html = "<div class='airplane'>"
    for class_type, config in airplane.items():
        seats_html += f'<div class="mb-8"><h2 class="text-xl font-semibold mb-2 text-center">{class_type.replace("_", " ").title()}</h2>'
        for row in range(1, config['rows'] + 1):
            seats_html += '<div class="flex justify-center mb-2">'
            for seat in range(1, config['seats_per_row'] + 1):
                seat_id = f"{class_type[0].upper()}{row}{chr(64+seat)}"
                seat_info = seats[seat_id]
                occupied = 'occupied' if seat_info['occupied'] else ''
                seats_html += f"""
                    <div id='{seat_id}' data-seat-id='{seat_id}' data-price='{seat_info['price']}'
                         class='seat w-10 h-10 rounded m-1 flex items-center justify-center text-sm font-semibold bg-{class_type} hover:bg-{class_type}/80 cursor-pointer {occupied}'>
                        {seat_id}
                    </div>
                """
                if seat == config['seats_per_row'] // 2:
                    seats_html += '<div class="w-8"></div>'  # Pasillo
            seats_html += '</div>'
        seats_html += '</div>'
    seats_html += "</div>"
    
    return render_template('index.html', seats=seats_html)

@app.route('/reserve', methods=['POST'])
def reserve_seat():
    data = request.json
    seat_id = data.get('seat')
    
    if seat_id not in seats:
        return jsonify({'success': False, 'message': 'Asiento inválido'})
    
    if seats[seat_id]['occupied']:
        return jsonify({'success': False, 'message': 'El asiento ya está ocupado'})
    
    seats[seat_id]['occupied'] = True
    return jsonify({'success': True, 'message': 'Asiento reservado con éxito'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
