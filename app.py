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
            # print(f"Connected to MySQL Server: {connection.get_server_info()}")
        return connection.cursor(buffered=True), connection
    except mysql.connector.Error as e:
        print("Error while connecting to MySQL", e)
        return None, None
# home page
@app.route("/")
def home():
    return render_template("home.html")

#camperlist
@app.route("/campers", methods=['GET'])
def campers():
    camp_date = request.args.get('campdate')
    if camp_date:
        cursor, _ = getCursor()
        cursor.execute("""
            SELECT bookings.booking_id, customers.firstname, customers.familyname, bookings.occupancy, COALESCE(sites.site_id, 'N/A') AS site_id, bookings.booking_date, bookings.nights
            FROM bookings 
            LEFT JOIN sites ON bookings.site = sites.site_id 
            JOIN customers ON bookings.customer = customers.customer_id 
            WHERE bookings.booking_date = %s;
        """, (camp_date,))
        camper_list = cursor.fetchall()
        if camper_list:
            return render_template("datepickercamper.html", camperlist=camper_list, campdate=camp_date)
        else:
            message = f"No campers found for the selected date: {camp_date}."
            return render_template("datepickercamper.html", camperlist=[], campdate=camp_date, message=message)
    return render_template("datepickercamper.html", camperlist=[], campdate=None)

# Search camper
@app.route('/search/camper', methods=['GET', 'POST'])
def search_camper():
    report = None
    message = ""
    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()

        if not search_query:
            message = "Please enter a valid search term."
        else:
            cursor, _ = getCursor()
            if cursor:
                try:
                    # Check if search query is an integer (customer ID)
                    customer_id = int(search_query)
                    cursor.execute("""
                        SELECT c.customer_id, c.firstname, c.familyname, 
                               COUNT(b.booking_id) as total_bookings, 
                               IFNULL(AVG(b.occupancy), 0) as avg_occupancy
                        FROM customers c
                        LEFT JOIN bookings b ON c.customer_id = b.customer
                        WHERE c.customer_id = %s
                        GROUP BY c.customer_id, c.firstname, c.familyname;
                    """, (customer_id,))
                    report = cursor.fetchone()
                    if not report:
                        message = f"Sorry, there is no report for customer ID '{customer_id}'."
                except ValueError:
                    # Perform a stricter search for full first name or family name matches
                    if len(search_query) < 2:
                        message = "Please enter the full first name or family name, or a valid customer ID."
                    else:
                        cursor.execute("""
                            SELECT c.customer_id, c.firstname, c.familyname, 
                                   COUNT(b.booking_id) as total_bookings, 
                                   IFNULL(AVG(b.occupancy), 0) as avg_occupancy
                            FROM customers c
                            LEFT JOIN bookings b ON c.customer_id = b.customer
                            WHERE c.firstname = %s OR c.familyname = %s
                            GROUP BY c.customer_id, c.firstname, c.familyname;
                        """, (search_query, search_query))

                        report = cursor.fetchone()
                        if not report:
                            message = f"Sorry, there is no report for '{search_query}'."
    return render_template('searchcamper.html', report=report, message=message)



#make booking--first page
@app.route("/booking", methods=['GET', 'POST'])
def booking():
    if request.method == "GET":
        return render_template("datepicker.html", currentdate=datetime.now().date())
    else:
        bookingNights = request.form.get('bookingnights')
        bookingDate = request.form.get('bookingdate')
        occupancy = request.form.get('occupancy')
        firstNight = date.fromisoformat(bookingDate)
        lastNight = firstNight + timedelta(days=int(bookingNights))

        cursor, _ = getCursor()
        cursor.execute("SELECT * FROM customers;")
        customerList = cursor.fetchall()
        cursor.execute("SELECT * FROM sites WHERE occupancy >= %s AND site_id NOT IN (SELECT site FROM bookings WHERE booking_date BETWEEN %s AND %s);",
                       (occupancy, firstNight, lastNight))
        siteList = cursor.fetchall()
        return render_template("bookingform.html",
                      customerlist=customerList, bookingdate=bookingDate, sitelist=siteList, bookingnights=
                      bookingNights, occupancy=occupancy, form_title="Make a Booking", action="add", booking_id=
                      None, selected_customer=None, selected_site=None)
#make booking--second page
@app.route("/booking/add", methods=['POST'])
def make_booking():
    bookingDate = request.form.get('bookingdate')
    bookingNights = request.form.get('bookingnights')
    occupancy = request.form.get('occupancy')
    customer = request.form.get('customer')
    site = request.form.get('site')
    
    cursor, conn = getCursor()
    cursor.execute("INSERT INTO bookings (booking_date, nights, occupancy, customer, site) VALUES (%s, %s, %s, %s, %s);",
                   (bookingDate, bookingNights, occupancy, customer, site))
    conn.commit()
    flash('Booking added successfully!', 'success')
    return redirect(url_for('booking_list'))
  
# booking list -show booking result 
@app.route("/booking_list", methods=['GET'])
def booking_list():
    cursor, _ = getCursor()
    cursor.execute("""
        SELECT b.booking_id, c.customer_id, c.firstname, c.familyname, c.phone, c.email, b.occupancy, b.site, b.booking_date, b.nights
        FROM bookings b
        JOIN customers c ON b.customer = c.customer_id;
    """)
    bookings = cursor.fetchall()
    booking_to_delete = request.args.get('booking_to_delete', None)
    if booking_to_delete:
       cursor.execute("""
        SELECT b.booking_id, c.customer_id, c.firstname, c.familyname, c.phone, c.email, b.booking_date 
            FROM bookings b 
            JOIN customers c ON b.customer = c.customer_id 
            WHERE b.booking_id = %s;
        """, (booking_to_delete,))
       booking_to_delete = cursor.fetchone()
    return render_template("bookinglistedit.html", bookings=bookings, booking_to_delete=booking_to_delete )
# edit booking
@app.route("/booking/edit/<int:booking_id>", methods=['GET', 'POST'])
def edit_booking(booking_id):
    cursor, conn = getCursor()
    if request.method == 'GET':
        cursor.execute("SELECT * FROM bookings WHERE booking_id = %s;", (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            flash('Booking not found!', 'danger')
            return redirect(url_for('booking_list'))

        cursor.execute("SELECT * FROM customers;")
        customerList = cursor.fetchall()
        cursor.execute("SELECT * FROM sites;")
        siteList = cursor.fetchall()
        return render_template("bookingform.html", booking=booking, customerlist=customerList, sitelist=siteList, bookingdate=booking[3], bookingnights=booking[5], occupancy=booking[2], form_title="Edit Booking", action="edit", booking_id=booking_id, selected_customer=booking[1], selected_site=booking[4])
    else:
        bookingDate = request.form.get('bookingdate')
        bookingNights = request.form.get('bookingnights')
        occupancy = request.form.get('occupancy')
        customer = request.form.get('customer')
        site = request.form.get('site')

        cursor.execute("""
            UPDATE bookings SET booking_date=%s, nights=%s, occupancy=%s, customer=%s, site=%s
            WHERE booking_id=%s;
        """, (bookingDate, bookingNights, occupancy, customer, site, booking_id))
        conn.commit()
        flash('Booking updated successfully!', 'success')
        return redirect(url_for('booking_list'))
# delet booking
@app.route("/booking/delete/<int:booking_id>", methods=['GET', 'POST'])
def confirm_delete_booking(booking_id):
    cursor, conn = getCursor()
    if request.method == 'POST':
        cursor.execute("DELETE FROM bookings WHERE booking_id = %s;", (booking_id,))
        conn.commit()
        flash(f'Booking {booking_id} deleted successfully!', 'success')
        return redirect(url_for('booking_list'))
    else:
        cursor.execute("""
            SELECT b.booking_id, c.firstname, c.familyname, b.booking_date, b.occupancy, b.site
            FROM bookings b
            JOIN customers c ON b.customer = c.customer_id
            WHERE b.booking_id = %s;
        """, (booking_id,))
        booking = cursor.fetchone()
        return render_template("confirmdelete.html", booking=booking)

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
                cursor.execute("SELECT customer_id, firstname, familyname, email, phone FROM customers WHERE firstname LIKE %s OR familyname LIKE %s", 
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
        # Fetch customer data from the database 
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()

    if request.method == 'POST':
        customer_id = request.form.get('customer_id') 
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