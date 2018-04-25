#!/usr/bin/env python3

from modules import pg8000
import configparser


# Define some useful variables
ERROR_CODE = 55929

#####################################################
##  Database Connect
#####################################################

def database_connect():
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create a connection to the database
    connection = None
    try:
        connection = pg8000.connect(database=config['DATABASE']['user'],
            user=config['DATABASE']['user'],
            password=config['DATABASE']['password'],
            host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    #return the connection to use
    return connection

#####################################################
##  Login
#####################################################

def check_login(email, password):
    # Dummy data
    #val = ['Shadow', 'Mr', 'Evan', 'Nave', '123 Fake Street, Fakesuburb', 'SIT', '01-05-2016', 'Premium', '1']
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    r = None
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT * FROM loginchk(%s,%s)"""
        cur.execute(sql, (email, password))
        r = cur.fetchone()
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error with Database")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return r


#####################################################
##  Homebay
#####################################################
def update_homebay(email, bayname):
    # TODO
    # Update the user's homebay
	
	# Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT * FROM uph1(%s)"""
        cur.execute(sql, (bayname,))
        r = cur.fetchone()
        id = r[0]
        sql2 = """UPDATE carsharing.member
		       SET homebay = %s
			   WHERE email = %s"""
        cur.execute(sql2, (id, email))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except:
        # If there were any errors, we print something nice and return false
        print("Error with Database")
    conn.rollback()
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return False

    
def update_session_homebay(email):
    #val = ['66XY99', 'Ice the Cube','Nissan', 'Cube', '2007', 'auto', 'Luxury', '5', 'SIT', '8', 'http://example.com']

    # Get details of member and return current homebay to be stored in session
    
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    r = None
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT * FROM upses(%s)"""
        cur.execute(sql, (email,))
        r = cur.fetchone()
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error with Database")
    cur.close()                     # Close the cursor
    conn.close()
    return r    
    
#####################################################
##  Booking (make, get all, get details)
#####################################################

def make_booking(email, car_rego, date, hour, duration):
    # TODO
    # Insert a new booking
    # Make sure to check for:
    #       - If the member already has booked at that time
    #       - If there is another booking that overlaps
    #       - Etc.
    # return False if booking was unsuccessful :)
    # We want to make sure we check this thoroughly
    
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    try:
        cur.execute("""SET TRANSACTION ISOLATION LEVEL SERIALIZABLE""")
        startTime = date + ' ' + hour +':00:00'
		
		#get the endTime = startTime + duration
        dur = duration + ':00:00'	
        stmt = """SELECT (to_timestamp(%s ,  'YYYY-MM-DD HH24:MI:SS')+ %s)::timestamp without time zone """
        cur.execute(stmt, (startTime, dur))
        result = cur.fetchone()
        endTime = result[0]
        
        #checks to see if car and user are free. If booked a value will be returned, if free None will be returned
        sql = """SELECT bookingid
                 FROM booking JOIN member ON (madeby = memberno)
                 WHERE (car=%s OR email = %s) AND (endtime > %s AND starttime < %s)
                """
        cur.execute(sql, (car_rego, email, startTime, endTime))
        r = cur.fetchone()
        print(r)
        
        #If None returned make the booking
        if r == None:
            
            stmt = """SELECT memberno 
                      FROM member
                      WHERE email = %s """
            cur.execute(stmt, (email,))
            result = cur.fetchone()
            memberno = result[0]
            
            stmt ="""INSERT INTO Booking(car, madeby, startTime, endTime) VALUES (%s, %s, %s, %s)"""
		
            cur.execute(stmt, (car_rego, memberno, startTime,endTime))
            
            stmt ="""UPDATE member
                     SET stat_nrofbookings = stat_nrofbookings + 1
                     WHERE email = %s"""
		
            cur.execute(stmt, (email,))
        
        #If already booked rollback and return 'booked' to display error message
        else:
            conn.rollback()
            cur.close()                     # Close the cursor
            conn.close()                    # Close the connection to the db
            return 'booked'
		
		#commit booking and update stat_nrofbookings at the same time
        conn.commit() 
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return True
    except:
        # If there were any errors, we print something nice and return false
        print("Error fetching from database")
    conn.rollback()
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return False         

def update_session_stat_nrofbookings(email):
    #val = ['66XY99', 'Ice the Cube','Nissan', 'Cube', '2007', 'auto', 'Luxury', '5', 'SIT', '8', 'http://example.com']

    # Get details of member and update current stat_nrofbookings to be stored in session
    
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    r = None
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT * FROM upses2(%s)"""
        cur.execute(sql, (email,))
        r = cur.fetchone()
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error with Database")
    cur.close()                     # Close the cursor
    conn.close()
    return r    
    
    

def get_all_bookings(email):
    #val = [['66XY99', 'Ice the Cube', '01-05-2016', '10', '4', '29-04-2016'],['66XY99', 'Ice the Cube', '27-04-2016', '16'], ['WR3KD', 'Bob the SmartCar', '01-04-2016', '6']]

    # TODO
    # Get all the bookings made by this member's email
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    r = None
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT car, name, date(starttime), date_part('hour', starttime)::int
                 FROM carsharing.booking JOIN carsharing.car ON (car = regno) JOIN carsharing.member ON (madeby = memberno)
                 WHERE email=%s
                 ORDER BY date(starttime) DESC"""
        cur.execute(sql, (email,))
        r = cur.fetchall()
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error with Database")
    cur.close()                     # Close the cursor
    conn.close()
    return r

def get_booking(b_date, b_hour, car):
    #val = ['Shadow', '66XY99', 'Ice the Cube', '01-05-2016', '10', '4', '29-04-2016', 'SIT']

    # TODO
    # Get the information about a certain booking
    # It has to have the combination of date, hour and car
    
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    r = None
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT member.nickname, booking.car, car.name, date(starttime), date_part('hour', starttime)::int, ((date_part('hour', endtime)) - (date_part('hour', starttime)))::int, date(whenbooked), carbay.name
                 FROM carsharing.booking JOIN carsharing.car ON (car = regno) JOIN carsharing.member ON (madeby = memberno) JOIN carsharing.carbay ON (parkedat = bayid)
                 WHERE date(starttime) = %s AND date_part('hour', starttime) = %s AND booking.car = %s"""
        cur.execute(sql, (b_date, b_hour, car))
        r = cur.fetchone()
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error with Database")
    cur.close()                     # Close the cursor
    conn.close()
    return r


#####################################################
##  Car (Details and List)
#####################################################

def get_car_details(regno):
    #val = ['66XY99', 'Ice the Cube','Nissan', 'Cube', '2007', 'auto', 'Luxury', '5', 'SIT', '8', 'http://example.com']
    # TODO
    # Get details of the car with this registration number
    # Return the data (NOTE: look at the information, requires more than a simple select. NOTE ALSO: ordering of columns)
    
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    r = None
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT regno, car.name, make, model, year, transmission, category, capacity, carbay.name
                 FROM car JOIN carmodel USING (make, model) JOIN carbay ON (parkedat = bayid)
                 WHERE regno=%s"""
        cur.execute(sql, (regno,))
        r = cur.fetchone()
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error with Database")
    cur.close()                     # Close the cursor
    conn.close()
    return r
   

def get_car_availability(regno):
    # TODO
    # Insert a new booking
    # Make sure to check for:
    #       - If the member already has booked at that time
    #       - If there is another booking that overlaps
    #       - Etc.
    # return False if booking was unsuccessful :)
    # We want to make sure we check this thoroughly
    
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    try:
        i = 0
        availability = []
        
        while i < 24:
            sql = """SELECT bookingid
                     FROM booking JOIN member ON (madeby = memberno)
                     WHERE car=%s AND (date(starttime) = current_date) AND ((extract(hour FROM endtime)) > %s AND (extract(hour FROM starttime)) < %s)
                    """
            cur.execute(sql, (regno, i, i + 1))
            r = cur.fetchone()
            
            if r == None:
                availability.append(' Available ')  
            else:
                availability.append(' Booked ') 
            i +=1
    except:
        # If there were any errors, we print something nice and return false
        print("Error fetching from database")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return availability        


def get_all_cars():
    #val = [ ['66XY99', 'Ice the Cube', 'Nissan', 'Cube', '2007', 'auto'], ['WR3KD', 'Bob the SmartCar', 'Smart', 'Fortwo', '2015', 'auto']]

    # TODO
    # Get all cars that PeerCar has
    # Return the results
	
	# Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        cur.execute(""" SELECT regno, name, make, model, year, transmission 
						FROM carsharing.car
						ORDER BY name ASC""")
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val
#####################################################
##  Bay (detail, list, finding cars inside bay)
#####################################################

def get_all_bays():
    #val = [['SIT', '123 Some Street, Boulevard', '2'], ['some_bay', '1 Somewhere Road, Right here', '1']]
    # TODO
    # Get all the bays that PeerCar has :)
    # And the number of bays
    # Return the results
    
	# Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        cur.execute(""" SELECT carbay.name, address, COUNT(regno)
					FROM carsharing.carbay JOIN carsharing.car ON (bayid = parkedat)
					GROUP BY carbay.name, address
					ORDER BY carbay.name ASC""")
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

def get_bay(name):
    #val = ['SIT', 'Home to many (happy?) people.', '123 Some Street, Boulevard', '-33.887946', '151.192958']

    # TODO
    # Get the information about the bay with this unique name
    # Make sure you're checking ordering ;)
    
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    r = None
    try:
        # Try executing the SQL and get from the database
        #gps_lat and gps_long are purposely in this order as the sample data/schema do not match and have lat in long and vice versa
        sql = """SELECT name, description, address, gps_long, gps_lat, walkscore, mapurl
                 FROM carbay
                 WHERE name = %s"""
        cur.execute(sql, (name,))
        r = cur.fetchone()
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error with Database")
    cur.close()  # Close the cursor
    conn.close()
    return r

def search_bays(search_term):
    #val = [['SIT', '123 Some Street, Boulevard', '-33.887946', '151.192958']]

    # TODO
    # Select the bays that match (or are similar) to the search term
    # You may like this
    
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    val = None
    try:
        search_T = '%' + search_term + '%'
        # Try getting all the information returned from the query
        sql = """ SELECT carbay.name, address, COUNT(regno)
                 FROM carsharing.carbay JOIN carsharing.car ON (bayid = parkedat)
                 WHERE (Lower(carbay.name)  LIKE Lower(%s)) OR Lower(carbay.address)  LIKE Lower(%s)
                 GROUP BY carbay.name, address
                 ORDER BY carbay.name ASC"""
        cur.execute(sql, (search_T, search_T))
        val = cur.fetchall()
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error with Database")
    cur.close()                     # Close the cursor
    conn.close()
    print(search_term)
    return val

def get_cars_in_bay(bay_name):
    #val = [ ['66XY99', 'Ice the Cube'], ['WR3KD', 'Bob the SmartCar']]

    # TODO
    # Get the cars inside the bay with the bay name
    # Cars who have this bay as their bay :)
    # Return simple details (only regno and name)

    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return ERROR_CODE
    cur = conn.cursor()
    r = None
    try:
        # Try executing the SQL and get from the database
        #gps_lat and gps_long are purposely in this order as the sample data/schema do not match and have lat in long and vice versa
        sql = """SELECT car.regno, car.name
                 FROM carsharing.carbay JOIN carsharing.car ON (bayid = parkedat)
                 WHERE carbay.name = %s"""
        cur.execute(sql, (bay_name,))
        r = cur.fetchall()
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error with Database")
    cur.close()  # Close the cursor
    conn.close()
    return r