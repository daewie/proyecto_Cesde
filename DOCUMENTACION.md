# Documentación del Sistema de Reserva de Asientos de Avión

## Índice

1. [Introducción](#introducción)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Backend (Flask)](#backend-flask)
4. [Frontend](#frontend)
5. [Flujo de Usuario](#flujo-de-usuario)
6. [Funcionalidades Principales](#funcionalidades-principales)
7. [Seguridad](#seguridad)
8. [Mejoras Potenciales](#mejoras-potenciales)
9. [Nota Importante](#nota-importante)

## Introducción

Este proyecto implementa un sistema didáctico de reserva de asientos de avión utilizando Flask como backend y HTML/JavaScript como frontend. El sistema permite a los usuarios seleccionar múltiples asientos en diferentes clases, incluyendo una segunda planta exclusiva, y simular el proceso de pago de su reserva.

## Estructura del Proyecto

proyecto/
│
├── app.py
├── static/
│   ├── app.js
│   └── style.css
├── templates/
│   ├── index.html
│   ├── reservation.html
│   └── payment.html
└── DOCUMENTACION.md

## Backend (Flask)

### app.py

Este archivo contiene la lógica principal del backend. Aquí hay un extracto del código con las partes más importantes:

```python
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

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
    seats_html = generate_seats_html()
    return render_template('reservation.html', seats=seats_html)

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
  
    # Guardar la información de la reserva en la sesión
    session['reserved_seats'] = reserved_seats
    session['total_price'] = total_price
  
    return jsonify({
        'success': True,
        'message': 'Asientos reservados con éxito',
        'reserved_seats': reserved_seats,
        'total_price': total_price
    })

# ... (otras rutas y funciones)
```

## Frontend

### templates/index.html

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reserva de Asientos de Avión - Bienvenido</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center">
    <div class="text-center">
        <h1 class="text-4xl font-bold mb-8 text-gray-800">Bienvenido a la Reserva de Asientos de Avión</h1>
        <p class="text-xl mb-8 text-gray-600">Haga clic en el botón de abajo para comenzar su reserva</p>
        <a href="/reservation" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded text-xl transition duration-300">
            Reservar Asientos
        </a>
    </div>
</body>
</html>
```

### templates/reservation.html

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reserva de Asientos de Avión</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        economy: '#e0f7fa',
                        business: '#fff9c4',
                        firstClass: '#ffccbc',
                        secondFloor: '#c8e6c9',
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-8 text-center text-gray-800">Reserva de Asientos de Avión</h1>
        <div class="bg-white p-6 rounded-lg shadow-lg">
            <div class="airplane-container overflow-x-auto">
                <div class="inline-flex flex-col items-center mb-8">
                    <div class="w-48 h-12 bg-gray-400 rounded-t-full mb-4"></div>
                    {{ seats | safe }}
                </div>
            </div>
            <div id="selection" class="mt-8">
                <h2 class="text-xl font-semibold mb-2">Asientos seleccionados: <span id="selected-seats" class="font-normal">Ninguno</span></h2>
                <h3 class="text-lg mb-4">Precio total: $<span id="total-price" class="font-semibold">0</span></h3>
                <button id="reserve-button" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed" disabled>
                    Reservar Asientos
                </button>
            </div>
        </div>
    </div>

    <script src="{{ url_for('static', filename='app.js') }}"></script>
</body>
</html>
```

### static/app.js

```javascript
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
                    // Redirigir a la página de pago
                    window.location.href = '/payment';
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
```

### static/style.css

```css
.seat.occupied {
    background-color: #ef9a9a !important;
    cursor: not-allowed !important;
}

.seat.selected {
    border: 2px solid #2196f3;
}

.bg-second_floor {
    background-color: #c8e6c9;
}

.bg-second_floor:hover {
    background-color: #a5d6a7;
}

.second-floor {
    border-bottom: 2px dashed #9e9e9e;
    margin-bottom: 2rem;
    padding-bottom: 2rem;
}
```

## Flujo de Usuario

1. El usuario llega a la página de inicio (`index.html`).
2. Al hacer clic en "Reservar Asientos", es dirigido a la página de reserva (`reservation.html`).
3. En la página de reserva, el usuario puede:
4. Ver la disposición de los asientos del avión.
5. Seleccionar uno o más asientos disponibles.
6. Ver el resumen de su selección y el precio total.
7. Al hacer clic en "Reservar Asientos", se envía la solicitud al servidor.
8. Si la reserva es exitosa, el usuario es redirigido a la página de pago (`payment.html`).
9. En la página de pago, el usuario ve el resumen de su reserva y puede simular el proceso de pago.
10. Tras un pago exitoso simulado, el usuario es redirigido a la página de inicio.

## Funcionalidades Principales

1. **Visualización de asientos:**
2. Representación gráfica de la disposición de los asientos.
3. Diferenciación visual entre clases de asientos.
4. Indicación clara de asientos ocupados y disponibles.
5. **Selección múltiple de asientos:**
6. Los usuarios pueden seleccionar varios asientos en una sola reserva.
7. Actualización en tiempo real del resumen de selección y precio total.
8. **Reserva de asientos:**
9. Verificación de disponibilidad en el servidor.
10. Bloqueo temporal de los asientos seleccionados durante el proceso de pago.
11. **Proceso de pago simulado:**
12. Resumen detallado de la reserva antes del pago.
13. Formulario para simular el ingreso de datos de pago.
14. **Gestión de sesiones:**
15. Almacenamiento de la información de reserva en la sesión del usuario.
16. Limpieza de la sesión tras completar o cancelar una reserva.

## Seguridad

1. **Clave secreta de Flask:**
2. Generación segura de la clave secreta usando `secrets.token_hex()`.
3. **Validación de datos:**
4. Verificación en el servidor de la validez y disponibilidad de los asientos seleccionados.
5. **Protección contra reservas duplicadas:**
6. Verificación de ocupación de asientos antes de confirmar la reserva.
7. **Sesiones:**
8. Uso de sesiones de Flask para mantener la información de reserva de forma segura.

## Mejoras Potenciales

**1.Autenticación de usuarios:**

Implementar un sistema de registro y login para los usuarios.

 **2.****Persistencia de datos:**

Utilizar una base de datos para almacenar la información de reservas y usuarios.

**3.Tiempo límite de reserva:**

Implementar un sistema de timeout para liberar asientos no pagados después de cierto tiempo.

**4.Mejoras en la interfaz de usuario:**

Añadir animaciones y mejorar la respuesta visual durante la selección de asientos.

Implementar un diseño responsivo para dispositivos móviles.

**5.Gestión de reservas:**

Añadir funcionalidad para que los usuarios puedan ver y gestionar sus reservas existentes.

**6.Optimización de rendimiento:**

Implementar caché para reducir la carga del servidor en la generación de HTML de asientos.

**7.Internacionalización:**

Añadir soporte para múltiples idiomas.
