# ✈️ Flight Reservation System

A full-stack **Flask** web application to register, search flights, book tickets, and manage your bookings easily! 🛫

---

## 🚀 Features
- User Sign Up and Login (with password hashing)
- Search Flights by Departure, Destination, and Date
- Book Flights with Real-Time Seat Availability Check
- View Bookings and Cancel Bookings
- Flash Messages for User Feedback
- Session Management for User Authentication
- Logging and Debugging Information

---

## 🛠 Tech Stack
- **Backend**: Python (Flask)
- **Database**: MySQL
- **Frontend**: HTML, CSS (Jinja2 templates)
- **Authentication**: SHA256 Password Hashing
- **Libraries**: Flask, mysql-connector-python

---

## 📂 Project Structure
```plaintext
├── app.py
├── templates/
│   ├── home.html
│   ├── signup.html
│   ├── login.html
│   ├── search_flights.html
│   ├── booking_page.html
│   ├── booking_confirmation.html
│   ├── bookings.html
├── static/
│   └── (CSS/JS Files)
├── requirements.txt
└── README.md
```

---

## 🧠 Database Tables
You will need these tables:
- \`users\`
- \`flights\`
- \`bookings\`

Each with appropriate fields like:
- **users**: id, username, email, password
- **flights**: flight_id, departure, destination, departure_date, arrival_time, price, available_seats
- **bookings**: booking_id, flight_id, user_id, name, email, phone, num_seats, status

---

## 🏁 How to Run Locally
1. Clone the repository.
2. Set up a MySQL database and create required tables.
3. Update MySQL config inside \`app.py\`.
4. Install dependencies:
    ```bash
    pip install flask mysql-connector-python
    ```
5. Run the application:
    ```bash
    python app.py
    ```
6. Visit `http://127.0.0.1:5000/` in your browser.

---

## ⚡ Important Notes
- Remember to **set a secure secret key** in `app.secret_key`.
- Database user credentials in `db_config` should match your local MySQL setup.

---

## ❤️ Acknowledgements
- **Flask** official documentation
- **MySQL** official guides
- **Python** community


