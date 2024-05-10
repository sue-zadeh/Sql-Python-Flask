# Sql-Python-Flask
please have a look on my project here: https://suezadeh.pythonanywhere.com/

![![Selwyn Campground](Selwyn Campground.png)]

	

Database Questions:
Refer to the supplied scg_local.sql file to answer the following questions:

What SQL statement creates the customer table and defines its fields/columns?

sql
Copy code
CREATE TABLE IF NOT EXISTS customers (
  customer_id INT NOT NULL AUTO_INCREMENT,
  firstname VARCHAR(45) NULL,
  familyname VARCHAR(60) NOT NULL,
  email VARCHAR(255) NULL,
  phone VARCHAR(12) NULL,
  PRIMARY KEY (customer_id)
);
Which line of SQL code sets up the relationship between the customer and booking tables?

sql
Copy code
CONSTRAINT customer : FOREIGN KEY (customer) REFERENCES scg.customers (customer_id)
ON DELETE NO ACTION ON UPDATE NO ACTION;
Which lines of SQL code insert details into the sites table?

sql
Copy code
INSERT INTO sites (site_id, occupancy) VALUES ('P1', '5');
INSERT INTO sites (site_id, occupancy) VALUES ('P4', '2');
INSERT INTO sites (site_id, occupancy) VALUES ('P2', '3');
INSERT INTO sites (site_id, occupancy) VALUES ('P5', '8');
INSERT INTO sites (site_id, occupancy) VALUES ('P3', '2');
INSERT INTO sites (site_id, occupancy) VALUES ('U1', '6');
INSERT INTO sites (site_id, occupancy) VALUES ('U2', '2');
INSERT INTO sites (site_id, occupancy) VALUES ('U3', '4');
INSERT INTO sites (site_id, occupancy) VALUES ('U4', '4');
INSERT INTO sites (site_id, occupancy) VALUES ('U5', '2');
Formatting Tips:
Use triple backticks (```) to create blocks of code. This helps in separating the SQL syntax from regular text, enhancing readability.
Use headings to separate questions or sections. This provides a clear structure to the document.
Consider linking directly to your project to make it easy for readers to access it.