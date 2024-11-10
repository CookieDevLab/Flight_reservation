from flask import Flask, flash, render_template, request, redirect, url_for, session
import mysql.connector as mysqltor
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key

# MySQL Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'test',
    'database': 'flight_reservation'
}

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        db = mysqltor.connect(**db_config)
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        db = mysqltor.connect(**db_config)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            session['user_id'] = user[0]
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

# Search Flights Route
@app.route('/search', methods=['GET', 'POST'])
def search_flights():
    if request.method == 'POST':
        departure = request.form['departure']
        destination = request.form['destination']
        date = request.form['departure_date']

        db = mysqltor.connect(**db_config)
        cursor = db.cursor()

        # Query exact matches
        cursor.execute(
            "SELECT * FROM flights WHERE departure=%s AND destination=%s AND departure_date=%s",
            (departure, destination, date)
        )
        flights = cursor.fetchall()

        # Query similar flights if no exact match
        similar_flights = []
        if not flights:
            cursor.execute(
                "SELECT * FROM flights WHERE departure=%s OR destination=%s OR departure_date=%s",
                (departure, destination, date)
            )
            similar_flights = cursor.fetchall()

        cursor.close()
        db.close()
        
        return render_template('search_flights.html', flights=flights, similar_flights=similar_flights)
    
    return render_template('search_flights.html')

@app.route('/booking_page/<int:flight_id>', methods=['POST'])
def booking_page(flight_id):
    return render_template('booking_page.html', flight_id=flight_id)

@app.route('/process_booking/<int:flight_id>', methods=['POST'])
def process_booking(flight_id):
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    num_seats = int(request.form['num_seats'])

    db = mysqltor.connect(**db_config)
    cursor = db.cursor()

    # Updated query to use the correct column name
    cursor.execute("SELECT flight_id, departure, destination, departure_date, arrival_time, price, available_seats FROM flights WHERE flight_id = %s", (flight_id,))
    flight = cursor.fetchone()

    if flight and flight[6] >= num_seats:  # Check if enough seats are available
        flight_id = flight[0]
        departure = flight[1]
        destination = flight[2]
        departure_date = flight[3]  # Updated to use the correct name
        arrival_time = flight[4]
        price = flight[5]
        total_price = price * num_seats

        # Insert booking into the database, ensure user_id is included
        cursor.execute("INSERT INTO bookings (flight_id, user_id, name, email, phone, num_seats) VALUES (%s, %s, %s, %s, %s, %s)",
                       (flight_id, session['user_id'], name, email, phone, num_seats))
        
        # Update available seats
        cursor.execute("UPDATE flights SET available_seats = available_seats - %s WHERE flight_id = %s", (num_seats, flight_id))
        db.commit()
        
        cursor.close()
        db.close()

        # Render booking confirmation page
        return render_template('booking_confirmation.html', 
                               flight_id=flight_id, 
                               departure=departure, 
                               destination=destination, 
                               departure_date=departure_date,  
                               arrival_time=arrival_time,
                               price=price, 
                               num_seats=num_seats, 
                               total_price=total_price,
                               name=name, 
                               email=email, 
                               phone=phone)
    else:
        flash("Not enough available seats.", "danger")
        db.close()
        return redirect(url_for('search_flights'))

@app.route('/my_bookings')
def my_bookings():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    db = mysqltor.connect(**db_config)
    cursor = db.cursor()
    
    query = """
        SELECT bookings.booking_id, bookings.flight_id, bookings.user_id, bookings.status, 
               flights.departure_date 
        FROM bookings 
        JOIN flights ON bookings.flight_id = flights.flight_id 
        WHERE bookings.user_id = %s
    """
    cursor.execute(query, (user_id,))
    bookings = cursor.fetchall()
    print("Bookings fetched from database:", bookings)

    print(bookings)  # Add this line to see the fetched data in the console
    
    cursor.close()
    db.close()

    return render_template('bookings.html', bookings=bookings)

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_flight_booking(booking_id):  # Changed function name here
    if 'user_id' in session:
        db = mysqltor.connect(**db_config)
        cursor = db.cursor()

        # Update the booking status to "Canceled"
        cursor.execute("UPDATE bookings SET status='Canceled' WHERE booking_id=%s AND user_id=%s", (booking_id, session['user_id']))
        db.commit()
        
        cursor.close()
        db.close()
        flash("Booking canceled successfully.", "success")
    else:
        flash("You must be logged in to cancel a booking.", "danger")
    
    return redirect(url_for('my_bookings'))


def fetch_bookings_for_user(user_id):
    db = mysqltor.connect(**db_config)
    cursor = db.cursor()
    cursor.execute("SELECT bookings.booking_id, flights.departure, flights.destination, flights.departure_date, flights.arrival_time, bookings.num_seats, bookings.status FROM bookings JOIN flights ON bookings.flight_id = flights.flight_id WHERE bookings.user_id = %s", (user_id,))
    bookings = cursor.fetchall()
    cursor.close()
    db.close()
    return bookings

# Cancel Booking Route
@app.route('/cancel_booking/<int:booking_id>')
def cancel_booking(booking_id):
    if 'user_id' in session:
        db = mysqltor.connect(**db_config)
        cursor = db.cursor()
        cursor.execute("UPDATE bookings SET status='Canceled' WHERE booking_id=%s", (booking_id,))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('my_bookings'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
