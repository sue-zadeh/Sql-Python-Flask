# testconnection.py
import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="123Suezx.",  # Ensure this matches the password you've confirmed works
        database="scg"
    )
    if connection.is_connected():
        db_info = connection.get_server_info()
        print("Successfully connected to MySQL database. MySQL Server version on ", db_info)
        connection.close()
except mysql.connector.Error as e:
    print("Error while connecting to MySQL", e)
