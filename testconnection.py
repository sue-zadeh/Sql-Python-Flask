cursor = cnx.cursor()
cursor.execute("SELECT * FROM customers LIMIT 5;")
results = cursor.fetchall()
for row in results:
    print(row)
cursor.close()
cnx.close()
