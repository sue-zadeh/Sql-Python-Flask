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
if __name__ == "__main__":
    app.run(debug=True)
@app.route("/")
def home():
    return render_template("base.html")

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
@app.route("/booking/add", methods=['POST'])
def makebooking():
    site = request.form.get('site')
    customer = request.form.get('customer')
    booking_date = request.form.get('bookingdate')
    occupancy = request.form.get('occupancy')
    booking_nights = int(request.form.get('bookingnights'))

    try:
        connection = getCursor()
        end_date = datetime.strptime(booking_date, '%Y-%m-%d') + timedelta(days=booking_nights)
        query = """INSERT INTO bookings (site, customer, booking_date, end_date, occupancy)
                   VALUES (%s, %s, %s, %s, %s)"""
        connection.execute(query, (site, customer, booking_date, end_date.strftime('%Y-%m-%d'), occupancy))
        connection.commit()  
        flash('Booking successfully added!')
        return redirect(url_for('booking'))
    except mysql.connector.Error as err:
        flash('Failed to add booking: {}'.format(err))
        return redirect(url_for('booking'))
    # print(request.form)
    # pass
    
    # search customers
@app.route("/search/customers", methods=['GET', 'POST'])
def search_customers():
    if request.method == 'POST':
       search_query = request.form.get('search')
       connection = getCursor()
       query = "SELECT * FROM customers WHERE firstname LIKE %s OR familyname LIKE %s"
       connection.execute(query, ('%' + search_query + '%', '%' + search_query + '%'))
       results = connection.fetchall()
       return render_template("search_results.html", results=results)
    return render_template("search_customers.html")
  
  # add customers
@app.route("/add/customer", methods=['GET', 'POST'])
def add_customer():
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
         return redirect(url_for('add_customer'))
      except mysql.connector.Error as err:
         flash('Failed to add customer: {}'.format(err))
         return render_template("add_customer.html")
    return render_template("add_customer.html")   