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
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

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


#camper list
@app.route("/camper_list")
def camper_list():
    cursor = getCursor()  
    cursor.execute("SELECT * FROM customers JOIN bookings ON customer = customer_id JOIN sites ON site = site_id;")
    camperList = cursor.fetchall()
    return render_template("camperlist.html", camperlist=camperList)



@app.route("/booking", methods=['GET','POST'])
def booking():
    if request.method == "GET":
        return render_template("datepicker.html", currentdate = datetime.now().date())
    else:
        bookingNights = request.form.get('bookingnights')
        bookingDate = request.form.get('bookingdate')
        occupancy = request.form.get('occupancy')
        firstNight = date.fromisoformat(bookingDate)

        lastNight = firstNight + timedelta(days=int(bookingNights))
        connection = getCursor()
        connection.execute("SELECT * FROM customers;")
        customerList = connection.fetchall()
        connection.execute("select * from sites where occupancy >= %s AND site_id not in (select site from bookings where booking_date between %s AND %s);",(occupancy,firstNight,lastNight))
        siteList = connection.fetchall()
        return render_template("bookingform.html", customerlist = customerList, bookingdate=bookingDate, sitelist = siteList, bookingnights = bookingNights)    

  # booking/add 
def makebooking():
    site = request.form.get('site')
    customer = request.form.get('customer')
    booking_date = request.form.get('bookingdate')
    occupancy = request.form.get('occupancy')
    booking_nights = int(request.form.get('bookingnights'))
    cursor = getCursor()
    end_date = datetime.strptime(booking_date, '%Y-%m-%d') + timedelta(days=booking_nights)
    try:
        cursor.execute("INSERT INTO bookings (site, customer, booking_date, end_date, occupancy) VALUES (%s, %s, %s, %s, %s)", (site, customer, booking_date, end_date.strftime('%Y-%m-%d'), occupancy))
        flash('Booking successfully added!')
        return redirect(url_for('booking'))
    except mysql.connector.Error as err:
        flash(f'Failed to add booking: {err}')
        return redirect(url_for('bookingconfirmation.html'))

@app.route("/search/customers", methods=['GET', 'POST'])
def search_customers():
    if request.method == 'POST':
        search_query = request.form.get('search')
        cursor = getCursor()
        cursor.execute("SELECT * FROM customers WHERE firstname LIKE %s OR familyname LIKE %s", ('%' + search_query + '%', '%' + search_query + '%'))
        results = cursor.fetchall()
        return render_template("searchcustomers.html", results=results)
    return render_template("searchcustomers.html")

@app.route("/add_edit_customer", methods=['GET', 'POST'])
def add_edit_customer():
    customer_id = request.args.get('id')
    customer = None
    if customer_id:
        cursor = getCursor()
        cursor.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
        customer = cursor.fetchone()

    if request.method == 'POST':
        firstname = request.form.get('firstname')
        familyname = request.form.get('familyname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        if customer:
            # Update existing customer
            cursor.execute("UPDATE customers SET firstname=%s, familyname=%s, email=%s, phone=%s WHERE id=%s", 
                           (firstname, familyname, email, phone, customer_id))
        else:
            # Insert new customer
            cursor.execute("INSERT INTO customers (firstname, familyname, email, phone) VALUES (%s, %s, %s, %s)", 
                           (firstname, familyname, email, phone))
        cursor.connection.commit()
        flash('Customer successfully added or updated!')
        return redirect(url_for('add_edit_customer'))
    
    return render_template("addeditcustomer.html", customer=customer)

if __name__ == "__main__":
    app.run(debug=True)