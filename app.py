from flask import Flask, flash
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
from datetime import date
from datetime import timedelta
import mysql.connector
from mysql.connector import connect, Error
import connect

app = Flask(__name__)
app.secret_key = '88856349b11d7b1ceb5ce9eaf56feb17'  # for flash messages

dbconn = None
connection = None
# connect to the database
def getCursor():
    global connection
    try:
        if connection is None or not connection.is_connected():
            connection = mysql.connector.connect(
                user=connect.dbuser,
                password=connect.dbpass,
                host=connect.dbhost,
                database=connect.dbname,
                autocommit=True
            )
            print(f"Connected to MySQL Server: {connection.get_server_info()}")
        return connection.cursor(buffered=True), connection
    except mysql.connector.Error as e:
        print("Error while connecting to MySQL", e)
        return None, None

# home page
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/campers", methods=['GET','POST'])
def campers():
    if request.method == "GET":
        return render_template("datepickercamper.html", currentdate = datetime.now().date())
    else:
        campDate = request.form.get('campdate')
        connection = getCursor()
        connection.execute("SELECT * FROM bookings join sites on site = site_id inner join customers on customer = customer_id where booking_date= %s;",(campDate,))
        camperList = connection.fetchall()
        return render_template("datepickercamper.html", camperlist = camperList)

# Camper list
@app.route("/camper_list", methods=['GET'])
def camper_list():
    camp_date = request.args.get('campdate')
    if camp_date:
        cursor, _ = getCursor()
        cursor.execute("""
            SELECT customers.firstname, customers.familyname, sites.site_id, bookings.booking_date 
            FROM bookings 
            JOIN sites ON bookings.site = sites.site_id 
            JOIN customers ON bookings.customer = customers.customer_id 
            WHERE bookings.booking_date = %s;
        """, (camp_date,))
        camper_list = cursor.fetchall()
        return render_template("camperlist.html", camperlist=camper_list, camp_date=camp_date)
    return render_template("camperlist.html", camperlist=[], camp_date=None)

# Booking
@app.route("/booking", methods=['GET', 'POST'])
def booking():
    if request.method == "GET":
        return render_template("datepicker.html", currentdate=datetime.now().date())
    else:
        bookingNights = request.form.get('bookingnights')
        bookingDate = request.form.get('bookingdate')
        occupancy = request.form.get('occupancy')
        firstNight = date.fromisoformat(bookingDate)
        
        if firstNight < datetime.now().date():
            flash('Cannot book a past date.', 'danger')
            return redirect(url_for('booking'))
        
        lastNight = firstNight + timedelta(days=int(bookingNights))
        cursor, _ = getCursor()
        cursor.execute("SELECT * FROM customers;")
        customerList = cursor.fetchall()
        cursor.execute("""
            SELECT site_id, occupancy FROM sites 
            WHERE occupancy >= %s 
            AND site_id NOT IN (
                SELECT site FROM bookings 
                WHERE booking_date BETWEEN %s AND %s
            );
        """, (occupancy, firstNight, lastNight))
        siteList = cursor.fetchall()

        cursor.execute("""
            SELECT customers.firstname, customers.familyname, sites.site_id, bookings.booking_date 
            FROM bookings 
            JOIN sites ON bookings.site = sites.site_id 
            JOIN customers ON bookings.customer = customers.customer_id 
            WHERE bookings.booking_date = %s;
        """, (firstNight,))
        bookingResults = cursor.fetchall()

        return render_template(
            "bookingform.html", 
            customerlist=customerList, 
            bookingdate=bookingDate, 
            sitelist=siteList, 
            bookingnights=bookingNights, 
            bookingResults=bookingResults
        )
#add booking
@app.route("/booking/add", methods=['POST'])
def makebooking():
    site = request.form.get('site')
    customer = request.form.get('customer')
    booking_date = request.form.get('bookingdate')
    occupancy = request.form.get('occupancy')
    booking_nights = int(request.form.get('bookingnights'))
    cursor, conn = getCursor()
    end_date = datetime.strptime(booking_date, '%Y-%m-%d') + timedelta(days=booking_nights)
    
    # Check for existing bookings on the same site and date
    cursor.execute("SELECT * FROM bookings WHERE site = %s AND booking_date = %s", (site, booking_date))
    existing_booking = cursor.fetchone()
    if existing_booking:
        flash('The site is already booked for the selected date.', 'danger')
    else:
     bookingresults = []
     message = ""
     if request.method == 'POST':
       booking_query = request.form.get('booking', '').strip()  
    if booking_query:
       cursor, _ = getCursor()   
    try:
      if cursor:
            cursor.execute("INSERT INTO bookings (site, customer, booking_date, end_date, occupancy) VALUES (%s, %s, %s, %s, %s)", (site, customer, booking_date, end_date.strftime('%Y-%m-%d'), occupancy))
            conn.commit()
            bookingresults = cursor.fetchall()
            message = f"Sorry, there site already booked for '{booking_query}'."
            flash(f'Booking successfully added! {customer} booked for site {site} starting from {booking_date} for {booking_nights} nights, for {occupancy} people.', 'success')
    except mysql.connector.Error as err:
            flash(f'Failed to add booking: {err}')
    
    # Re-fetch booking results to display on the same page
    cursor.execute("""
        SELECT customers.firstname, customers.familyname, sites.site_id, bookings.booking_date 
        FROM bookings 
        JOIN sites ON bookings.site = sites.site_id 
        JOIN customers ON bookings.customer = customers.customer_id 
        WHERE bookings.booking_date = %s;
    """, (booking_date,))
    bookingResults = cursor.fetchall()
    cursor.execute("SELECT * FROM customers;")
    customerList = cursor.fetchall()
    cursor.execute("""
        SELECT site_id, occupancy FROM sites 
        WHERE occupancy >= %s 
        AND site_id NOT IN (
            SELECT site FROM bookings 
            WHERE booking_date BETWEEN %s AND %s
        );
    """, (occupancy, booking_date, end_date))
    siteList = cursor.fetchall()

    return render_template(
        "bookingform.html",
        booking_query=booking_query,
        message=message, 
        customerlist=customerList, 
        bookingdate=booking_date, 
        sitelist=siteList, 
        bookingnights=booking_nights, 
        bookingResults=bookingResults
    )


# search customers
@app.route("/search/customers", methods=['GET', 'POST'])
def search_customers():
    results = []
    message = ""
    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()
        if search_query:
            cursor, _ = getCursor()
            if cursor:
                cursor.execute("SELECT * FROM customers WHERE firstname LIKE %s OR familyname LIKE %s", 
                               ('%' + search_query + '%', '%' + search_query + '%'))
                results = cursor.fetchall()
                if not results:
                    message = f"Sorry, there are no results for '{search_query}'."
    return render_template("searchcustomers.html", results=results, message=message)

# add_edit_customer
@app.route('/add_edit_customer', methods=['GET', 'POST'])
def add_edit_customer():
    customer_id = request.args.get('id') or request.form.get('customer_id')
    cursor, conn = getCursor()
    customer = None
    if customer_id:
        # Fetch customer data from the database if id is provided
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()

    if request.method == 'POST':
        firstname = request.form.get('firstname')
        familyname = request.form.get('familyname')
        email = request.form.get('email')
        phone = request.form.get('phone')

        if customer_id:  # Update existing customer
            if customer and (firstname, familyname, email, phone) == (customer[1], customer[2], customer[3], customer[4]):
                flash('Customer information is the same, no changes.', 'info')
            else:
                cursor.execute("""
                    UPDATE customers SET firstname=%s, familyname=%s, email=%s, phone=%s 
                    WHERE customer_id=%s
                """, (firstname, familyname, email, phone, customer_id))
                conn.commit()
                flash('Customer updated successfully!', 'success')
                return redirect(url_for('add_edit_customer'))
        else:  # Add new customer
            cursor.execute("SELECT * FROM customers WHERE familyname = %s", (familyname,))
            existing_customer = cursor.fetchone()
            if existing_customer:
                flash('A customer with this family name already exists!', 'danger')
            else:
                cursor.execute("""
                    INSERT INTO customers (firstname, familyname, email, phone) 
                    VALUES (%s, %s, %s, %s)
                """, (firstname, familyname, email, phone))
                conn.commit()
                flash('Customer added successfully!', 'success')
        return redirect(url_for('add_edit_customer', id=customer_id))

    mode = 'Edit' if customer_id else 'Add'
    return render_template("addeditcustomer.html", customer=customer, mode=mode)

# for error handling
if __name__ == "__main__":
    app.run(debug=True)