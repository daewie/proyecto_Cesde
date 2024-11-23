from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

users = {}
reservations_data = []

airplane = {
    'second_floor': {'rows': 2, 'seats_per_row': 4, 'price': 750_000},  
    'first_class': {'rows': 2, 'seats_per_row': 4, 'price': 500_000},   
    'business': {'rows': 3, 'seats_per_row': 6, 'price': 250_000},      
    'economy': {'rows': 10, 'seats_per_row': 6, 'price': 100_000},     
}

seats = {}
for class_type, config in airplane.items():
    for row in range(1, config['rows'] + 1):
        for seat in range(1, config['seats_per_row'] + 1):
            seat_id = f"{class_type[0].upper()}{row}{chr(64+seat)}"
            seats[seat_id] = {'occupied': False, 'price': config['price']}

def get_analytics_data():
    df = pd.DataFrame(reservations_data)
    if df.empty:
        return {
            'total_revenue': 0,
            'seats_by_class': {'economy': 0, 'business': 0, 'first_class': 0, 'second_floor': 0},
            'daily_revenue': [],
            'class_revenue': []
        }
    
    total_revenue = df['total_price'].sum()
    
    seats_by_class = {
        'economy': len([s for s in df['seats'].explode() if s.startswith('E')]),
        'business': len([s for s in df['seats'].explode() if s.startswith('B')]),
        'first_class': len([s for s in df['seats'].explode() if s.startswith('F')]),
        'second_floor': len([s for s in df['seats'].explode() if s.startswith('S')])
    }
    
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_revenue = df.groupby('date')['total_price'].sum().reset_index()
    daily_revenue['date'] = daily_revenue['date'].astype(str)
    
    class_revenue = []
    for class_type in ['economy', 'business', 'first_class', 'second_floor']:
        class_seats = [s for s in df['seats'].explode() if s.startswith(class_type[0].upper())]
        revenue = len(class_seats) * airplane[class_type]['price']
        class_revenue.append({'class': class_type, 'revenue': revenue})
    
    return {
        'total_revenue': total_revenue,
        'seats_by_class': seats_by_class,
        'daily_revenue': daily_revenue.to_dict('records'),
        'class_revenue': class_revenue
    }

@app.route('/analytics')
def analytics():
    if 'user' not in session:
        flash('Please log in to view analytics', 'error')
        return redirect(url_for('login'))
    analytics_data = get_analytics_data()
    return render_template('analytics.html', analytics=analytics_data, user=session.get('user'))

@app.route('/api/analytics')
def api_analytics():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(get_analytics_data())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists', 'error')
        else:
            users[username] = generate_password_hash(password)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and check_password_hash(users[username], password):
            session['user'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html', user=session.get('user'))

def generate_seats_html():
    seats_html = "<div class='airplane'>"
    for class_type, config in airplane.items():
        class_name = class_type.replace('_', '')
        seats_html += f"<div class='{class_name}-section mb-8'>"
        seats_html += f"<h2 class='text-2xl font-bold mb-4 text-center'>{class_type.replace('_', ' ').title()}</h2>"
        seats_html += "<div class='grid grid-cols-6 gap-2'>"
        for row in range(1, config['rows'] + 1):
            for seat in range(1, config['seats_per_row'] + 1):
                seat_id = f"{class_type[0].upper()}{row}{chr(64+seat)}"
                seat_info = seats[seat_id]
                occupied_class = 'occupied' if seat_info['occupied'] else ''
                seats_html += f"""
                    <div id='{seat_id}' 
                         data-seat-id='{seat_id}' 
                         data-price='{seat_info["price"]}'
                         class='seat {occupied_class} w-10 h-10 rounded-md flex items-center justify-center text-sm font-semibold cursor-pointer bg-{class_name}'>
                        {seat_id}
                    </div>
                """
        seats_html += "</div></div>"
    seats_html += "</div>"
    return seats_html

@app.route('/reservation')
def reservation():
    if 'user' not in session:
        flash('Please log in to make a reservation', 'error')
        return redirect(url_for('login'))
    seats_html = generate_seats_html()
    return render_template('reservation.html', seats=seats_html, user=session.get('user'))

@app.route('/reserve', methods=['POST'])
def reserve_seat():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in to reserve seats'})
    
    data = request.json
    seat_ids = data.get('seats', [])
    
    if not seat_ids:
        return jsonify({'success': False, 'message': 'No seats selected'})
    
    total_price = 0
    reserved_seats = []
    
    for seat_id in seat_ids:
        if seat_id not in seats:
            return jsonify({'success': False, 'message': f'Invalid seat: {seat_id}'})
        
        if seats[seat_id]['occupied']:
            return jsonify({'success': False, 'message': f'Seat {seat_id} is already occupied'})
        
        seats[seat_id]['occupied'] = True
        total_price += seats[seat_id]['price']
        reserved_seats.append(seat_id)
    
    reservations_data.append({
        'user': session['user'],
        'seats': reserved_seats,
        'total_price': total_price,
        'timestamp': datetime.now().isoformat()
    })
    
    session['reserved_seats'] = reserved_seats
    session['total_price'] = total_price
    
    return jsonify({
        'success': True,
        'message': 'Seats successfully reserved',
        'reserved_seats': reserved_seats,
        'total_price': total_price
    })

@app.route('/payment')
def payment():
    if 'user' not in session:
        flash('Please log in to access the payment page', 'error')
        return redirect(url_for('login'))
    
    reserved_seats = session.get('reserved_seats', [])
    total_price = session.get('total_price', 0)
    if not reserved_seats:
        return redirect(url_for('reservation'))
    return render_template('payment.html', reserved_seats=reserved_seats, total_price=total_price, user=session.get('user'))

@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please log in to process payment'})
    
    session.pop('reserved_seats', None)
    session.pop('total_price', None)
    return jsonify({'success': True, 'message': 'Payment successfully processed'})

@app.route('/select_destination')
def select_destination():
    if 'user' not in session:
        flash('Please log in to select a destination', 'error')
        return redirect(url_for('login'))
    return render_template('select_destination.html', user=session.get('user'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)