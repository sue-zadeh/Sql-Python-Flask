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

# dbconn = None
connection = None
# connect to the database
def getCursor():
    try:
        global connection
        connection = mysql.connector.connect(
        user=connect.dbuser,
        password=connect.dbpass,
        host=connect.dbhost,
        database=connect.dbname,
        autocommit=True)
        return connection.cursor()
    except mysql.connector.Error as err:
        print("Error while connecting to MySQL", err)
        return None
# home page
@app.route("/")
def home():
    return render_template("home.html")
@app.route("/campers", methods=['GET','POST'])
def campers():
   cursor = getCursor()
   if cursor is None:
        flash("Database connection could not be established.")
        return render_template("error_page.html")
   if request.method == "GET":
        return render_template("datepickercamper.html", currentdate = datetime.now().date())
   else:
        campDate = request.form.get('campdate')
        connection = getCursor()
        connection.execute("SELECT * FROM bookings join sites on site = site_id inner join customers on customer = customer_id where booking_date= %s;",(campDate,))
        camperList = connection.fetchall()
        return render_template("datepickercamper.html", camperlist = camperList)


#camper list
@app.route("/camper_list", methods=['GET'])
def camper_list():
   cursor = getCursor()
   if cursor is None:
        flash("Database connection could not be established.")
        return render_template("error_page.html")
   camp_date = request.args.get('campdate')
   if camp_date:
        cursor = getCursor()
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

@app.route("/booking", methods=['GET','POST'])
def booking():
   cursor = getCursor()
   if cursor is None:
        flash("Database connection could not be established.")
        return render_template("error_page.html")
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
@app.route("/make_booking", methods=['GET','POST'])
def makebooking():
   cursor = getCursor()
   if cursor is None:
        flash("Database connection could not be established.")
        return render_template("error_page.html")
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
# search customers
@app.route("/search/customers", methods=['GET', 'POST'])
def search_customers():
   cursor = getCursor()
   if cursor is None:
        flash("Database connection could not be established.")
        return render_template("error_page.html")
   if request.method == 'POST':
        search_query = request.form.get('search')
        cursor = getCursor()
        cursor.execute("SELECT * FROM customers WHERE firstname LIKE %s OR familyname LIKE %s", ('%' + search_query + '%', '%' + search_query + '%'))
        results = cursor.fetchall()
        return render_template("searchcustomers.html", results=results)
   return render_template("searchcustomers.html")

# add_edit_customer
@app.route("/add_edit_customer", methods=['GET', 'POST'])
def add_edit_customer():
   cursor = getCursor()
   if cursor is None:
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        familyname = request.form.get('familyname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        try:
            connection = getCursor()
            query = "INSERT INTO customers (firstname, familyname, email, phone) VALUES (%s, %s, %s, %s)"
            connection.execute(query, (firstname, familyname, email, phone))
            connection.commit()
            flash('Customer successfully added!')
        except mysql.connector.Error as err:
            flash('Failed to add customer: {}'.format(err))
        return redirect(url_for('add_edit_customer'))
    return render_template("addeditcustomer.html")


  # for error handeling
if __name__ == "__main__":
    app.run(debug=True)