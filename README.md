# Sql-Python-Flask
please have a look on my project here: https://suezadeh.pythonanywhere.com/  

![Selwyn Campground](Selwyn_Campground.png "Selwyn Campground")

	
<picture>
  <img alt="Selwyn Campground" src="Selwyn_Campground.png">
</picture>
	Database questions:   

	Refer to the supplied scg_local.sql file to answer the following questions: 

	1- What SQL statement creates the customer table and defines its fields/columns?
   (Copy and paste the relevant lines of SQL.)      

   ```CREATE TABLE IF NOT EXISTS `customers` (
  `customer_id` INT NOT NULL AUTO_INCREMENT,
  `firstname` VARCHAR(45) NULL,
  `familyname` VARCHAR(60) NOT NULL,
  `email` VARCHAR(255) NULL,
  `phone` VARCHAR(12) NULL,
  PRIMARY KEY (`customer_id`));  
  
  
	2- Which line of SQL code sets up the relationship between the customer and booking tables?     
    
    ```CONSTRAINT `customer`
    FOREIGN KEY (`customer`)
    REFERENCES `scg`.`customers` (`customer_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);  
  
  	3- Which lines of SQL code insert details into the sites table?  

```INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P1', '5');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P4', '2');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P2', '3');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P5', '8');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P3', '2');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U1', '6');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U2', '2');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U3', '4');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U4', '4');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U5', '2');
INSERT INTO `customers` (`customer_id`, `firstname`, `familyname`, `email`, `phone`) VALUES ('563', 'Simon', 'Smith', 'simon@smith.nz', '0244881901');
INSERT INTO `customers` (`customer_id`, `firstname`, `familyname`, `email`, `phone`) VALUES ('241', 'Jasmine', 'Holiday', 'jaz@onholiday.co.nz', '0274823801');
INSERT INTO `customers` (`customer_id`, `firstname`, `familyname`, `email`, `phone`) VALUES ('1654', 'Jonty', 'Jensen', 'Jonty_Jensen@gmail.com', '041208776');
INSERT INTO `customers` (`customer_id`, `firstname`, `familyname`, `email`, `phone`) VALUES ('1655', 'Kate', 'McArthur', 'K_McArthur94@gmail.com', '0281953665');
INSERT INTO `customers` (`customer_id`, `firstname`, `familyname`, `email`, `phone`) VALUES ('1656', 'Jack', 'Hopere', 'Jack643@gmail.com', '0224972003');
INSERT INTO `customers` (`customer_id`, `firstname`, `familyname`, `email`, `phone`) VALUES ('1657', 'Chloe', 'Mathewson', 'Chloe572@gmail.com', '0236621370');
INSERT INTO `customers` (`customer_id`, `firstname`, `familyname`, `email`, `phone`) VALUES ('1658', 'Kate', 'McLeod', 'KMcLeod112@gmail.com', '0275578364');
INSERT INTO `customers` (`customer_id`, `firstname`, `familyname`, `email`, `phone`) VALUES ('1659', 'Sam', 'Dawson', 'SamDawson@gmail.com', '071721045');
INSERT INTO `customers` (`customer_id`, `firstname`, `familyname`, `email`, `phone`) VALUES ('1660', 'Heidi', 'Delaney', 'HDelaney@gmail.com', '0282942819');
INSERT INTO `customers` (`customer_id`, `firstname`, `familyname`, `email`, `phone`) VALUES ('1661', 'Michael', 'Wright', 'Michael_Wright@gmail.com', '037512653');
INSERT INTO `customers` (`customer_id`, `firstname`, `familyname`, `email`, `phone`) VALUES ('1662', 'Elizabeth', 'Preston', 'ElizabethPreston@gmail.com', '094255377');
INSERT INTO `bookings` (`booking_id`, `site`, `customer`, `booking_date`,`occupancy`) VALUES ('346', 'P1', '1659', '2024-05-12','2');
INSERT INTO `bookings` (`booking_id`, `site`, `customer`, `booking_date`,`occupancy`) VALUES ('347', 'P1', '1659', '2024-05-13','2');
INSERT INTO `bookings` (`booking_id`, `site`, `customer`, `booking_date`,`occupancy`) VALUES ('348', 'P1', '1659', '2024-05-14','2');
INSERT INTO `bookings` (`booking_id`, `site`, `customer`, `booking_date`,`occupancy`) VALUES ('231', 'P5', '563', '2024-06-01','7');
INSERT INTO `bookings` (`booking_id`, `site`, `customer`, `booking_date`,`occupancy`) VALUES ('232', 'P5', '563', '2024-06-02','7');
INSERT INTO `bookings` (`booking_id`, `site`, `customer`, `booking_date`,`occupancy`) VALUES ('233', 'P5', '563', '2024-06-03','7');
INSERT INTO `bookings` (`booking_id`, `site`, `customer`, `booking_date`,`occupancy`) VALUES ('234', 'P5', '563', '2024-06-04','7');
INSERT INTO `bookings` (`booking_id`, `site`, `customer`, `booking_date`,`occupancy`) VALUES ('235', 'U2', '241', '2024-06-02','2');
INSERT INTO `bookings` (`booking_id`, `site`, `customer`, `booking_date`,`occupancy`) VALUES ('236', 'U2', '241', '2024-06-05','2');
INSERT INTO `bookings` (`booking_id`, `site`, `customer`, `booking_date`,`occupancy`) VALUES ('237', 'U2', '241', '2024-07-05','2');
INSERT INTO `bookings` (`booking_id`, `site`, `customer`, `booking_date`,`occupancy`) VALUES ('238', 'U2', '241', '2024-07-06','2'); 

	4- Suppose that as part of an audit trail, the time and date a booking was added to the database needed to be recorded. What fields/columns would you need to add to which tables? Provide the table name, new column name and the data type. (Do not implement this change in your app.) 

•	table name: Bookings    
•	new column name: created_at    
•	data type: datetime or TimeStamp         
	
	5- Suppose the ability for customers to make their own bookings was added. Describe two different changes that would be needed to the data model to implement this. (Do not implement these changes in your app.)     

• Adding a user authentication system: This usually involves creating a new table such as users with fields user_id, username, password_hash, ..... Each client can be linked to a user to be able having a secure login. 

• Modify the reservations table to include a status field: this will track the status of each reservation (for example pending, confirmed, canceled). It helps manage bookings to be done directly by customers, including changes or cancellations.        
	
  

      
