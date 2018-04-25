DROP TABLE IF EXISTS CarModel CASCADE;
DROP TABLE IF EXISTS Car CASCADE;
DROP TABLE IF EXISTS CarBay CASCADE;
DROP TABLE IF EXISTS Booking CASCADE;
DROP TABLE IF EXISTS Member CASCADE;
DROP TABLE IF EXISTS Phone CASCADE;
DROP TABLE IF EXISTS MembershipPlan CASCADE;
DROP TABLE IF EXISTS PaymentMethod CASCADE;
DROP TABLE IF EXISTS BankAccount CASCADE;
DROP TABLE IF EXISTS PayPal CASCADE;
DROP TABLE IF EXISTS CreditCard CASCADE;

--Carbay stores all information about the bay. Latitude and longitude are stored as reals for precision and checked to be within possible boundaries
CREATE TABLE CarBay(
  name VARCHAR(50) PRIMARY KEY,
  address VARCHAR(100) NOT NULL,
  description VARCHAR(500) NOT NULL,
  latitude REAL NOT NULL,
  longitude REAL NOT NULL
  CONSTRAINT latmax CHECK (latitude BETWEEN -180 AND 180),
  CONSTRAINT longmax CHECK (latitude BETWEEN -180 AND 180)
  );


  
--CarModel table where make & model together form the PK.
CREATE TABLE CarModel(
  make VARCHAR(20),
  model VARCHAR(20),
  category VARCHAR(20) NOT NULL,
  capacity INTEGER NOT NULL,
  PRIMARY KEY (make, model),
  CONSTRAINT validCapacity CHECK (capacity > 1)
  );

  
 --Creates table of cars with all information required. Regno must be unique and assumed to be standard 6 characters in Australia. Transmission constrained to either automatic or manual.
CREATE TABLE Car(
  regno CHAR(6) PRIMARY KEY,--it is assumed all cars have a std rego plate of 6 characters
  name VARCHAR(50) NOT NULL UNIQUE,
  year INTEGER NOT NULL,
  transmission VARCHAR(10) NOT NULL
  CONSTRAINT validTransmission CHECK (transmission='Automatic' OR transmission='Manual'),
  carBay VARCHAR(50) NOT NULL REFERENCES CarBay(name) ON UPDATE CASCADE ON DELETE CASCADE,
  make VARCHAR(20) NOT NULL,
  model VARCHAR(20) NOT NULL,
  FOREIGN KEY(make, model) REFERENCES CarModel(make, model) ON UPDATE CASCADE ON DELETE CASCADE
  );

 


CREATE TABLE Member(
  email VARCHAR(50) PRIMARY KEY, --MAX EMAIL POSSIBLE IS 254 CHARS?!?!
  userPassword VARCHAR(20) NOT NULL,
  title VARCHAR(4) NOT NULL, --assumed to be abbreviated and simple (Mrs, Ms, Miss, Mr, Dr etc)
  familyName VARCHAR(20) NOT NULL,
  givenName VARCHAR(20) NOT NULL,
  nickname VARCHAR(15) UNIQUE,
  licenseNr INTEGER NOT NULL,
  licenseExpires DATE NOT NULL,
  address VARCHAR(100) NOT NULL,
  birthdate DATE NOT NULL,
  memberSince DATE NOT NULL,
  carBay VARCHAR(50) REFERENCES CarBay(name) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT licenseExpiryCheck CHECK (licenseExpires > CURRENT_DATE),
  CONSTRAINT titleCheck CHECK (title='Mrs' OR title='Ms' OR title='Miss' OR title='Mr' OR title='Dr'),
  CONSTRAINT datesCheck CHECK (birthdate < memberSince),
  CONSTRAINT ageCheck CHECK (age(birthdate) > interval '25 years')
  );



CREATE TABLE Phone(
  phone VARCHAR(60) PRIMARY KEY,
  email VARCHAR(50) NOT NULL REFERENCES Member(email) ON UPDATE CASCADE ON DELETE CASCADE
  );

CREATE TABLE Booking(
  startDate DATE,
  startHour TIME,
  duration INTEGER NOT NULL,
  whenBooked TIMESTAMP CONSTRAINT SET DEFAULT CURRENT_TIMESTAMP,
regno CHAR(6) NOT NULL REFERENCES Car(regno) ON UPDATE CASCADE ON DELETE CASCADE,
  email VARCHAR(50) NOT NULL REFERENCES Member(email) ON UPDATE CASCADE ON DELETE CASCADE,
  PRIMARY KEY (email, startDate,startHour)
  );
  
CREATE TABLE MembershipPlan(
  title VARCHAR(20) PRIMARY KEY,
  monthly_fee REAL NOT NULL,
  hourly_rate REAL NOT NULL,
  km_rate REAL NOT NULL,
  daily_km_rate REAL NOT NULL,
  daily_km_included INTEGER NOT NULL,
  email VARCHAR(50) NOT NULL REFERENCES Member(email) ON UPDATE CASCADE ON DELETE CASCADE
  );
  
CREATE TABLE PaymentMethod(
  num INTEGER,
  email VARCHAR(50) REFERENCES Member(email) ON UPDATE CASCADE ON DELETE CASCADE,
  PRIMARY KEY(num, email)
  );

CREATE TABLE BankAccount(
  num INTEGER,
  email VARCHAR(50),
  name VARCHAR(40),
  bsb INTEGER,
  account INTEGER,
  CONSTRAINT BSBlimit CHECK (bsb BETWEEN 000000 AND 999999),
  CONSTRAINT AccountLimit CHECK (account BETWEEN 00000000 AND 99999999),
  FOREIGN KEY(num, email) REFERENCES PaymentMethod(num,email)ON UPDATE CASCADE ON DELETE CASCADE
  );
  
CREATE TABLE PayPal(
  num INTEGER,
  email VARCHAR(50) NOT NULL,
  paypaylEmail VARCHAR(50),
  FOREIGN KEY(num, email) REFERENCES PaymentMethod(num,email)ON UPDATE CASCADE ON DELETE CASCADE
  );
  
CREATE TABLE CreditCard(
  num INTEGER,
  email VARCHAR(50) NOT NULL,
  name VARCHAR(40),
  brand VARCHAR(20),
  FOREIGN KEY(num, email) REFERENCES PaymentMethod(num,email)ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION YOUSHALLNOTPASS() RETURNS trigger AS $$
DECLARE
wtol INTEGER;
 BEGIN
SELECT count(email) INTO wtol
FROM PaymentMethod
WHERE email IN (
SELECT email
FROM PaymentMethod
GROUP BY email
Having count(email) > 3) -- If there are more than 3 exact same emails, the count will be more than 3
;
IF
(wtol > 1) -- If there is more than 3 then it raises an exception
THEN
 RAISE EXCEPTION 'More than 3 payment methods are restricted'; -- you can't provide more than 3 payment methods for an email
END IF;
RETURN NEW;
 END
$$ LANGUAGE plpgsql VOLATILE;


CREATE TRIGGER WTFFF
 BEFORE INSERT ON PaymentMethod
 FOR EACH STATEMENT
 EXECUTE PROCEDURE YOUSHALLNOTPASS()
 ;









INSERT INTO CarBay VALUES ('Boolean Rd', '120 Boolean Rd, Redford','Northern end of Boolean Road near the post box', 69.000, 54.000);
INSERT INTO CarBay VALUES ('Spencey Shops', '240 Spencer St, Vergetown','Northern end of Boolean Road near the post box', 69.000, 54.000);
INSERT INTO CarModel VALUES ('Tesla', 'Model S', 'Electric', 5);
INSERT INTO CarModel VALUES ('Tesla', 'Model X', 'Electric', 4);
INSERT INTO Car VALUES ('WTH420', 'Dream Machine', 2012, 'Automatic', 'Spencey Shops', 'Tesla', 'Model S');
INSERT INTO Car VALUES ('JAB210', 'The Speed Demon', 2013, 'Manual', 'Boolean Rd', 'Tesla', 'Model X');
INSERT INTO Member VALUES ('MAKEYOUROWNEMAIL@gmail.com', 'secretPassword1234', 'Mr', 'Damian', 'Martelli', 'Mr Cool','514575','2017-10-11','78 Phillips Street','1985-05-11','2012-07-09');
INSERT INTO Member VALUES ('WutWut567@gmail.com', 'KeepThisSilent295', 'Mr', 'Fuad', 'Soudah', 'WOLO','514575','2017-10-11','120 Roscoe Street','1986-07-02','2013-02-08');
INSERT INTO Member VALUES ('Alibada@gmail.com', 'MUTHAMUTHA', 'Mr', 'Uruguay', 'Moshinima', 'NOBODY','514575','2017-10-11','120 Roscoe Street','1967-07-05','2014-02-01');
INSERT INTO Phone VALUES ('0412345982', 'MAKEYOUROWNEMAIL@gmail.com');
INSERT INTO Phone VALUES ('0293420927', 'MAKEYOUROWNEMAIL@gmail.com');
INSERT INTO Booking VALUES ('2016-05-22', '20:50:28.862298', 3, CURRENT_TIMESTAMP, 'JAB210',  'MAKEYOUROWNEMAIL@gmail.com');
INSERT INTO MembershipPlan VALUES ('Ultimate',20,3,1,1,1, 'MAKEYOUROWNEMAIL@gmail.com');
INSERT INTO PaymentMethod VALUES(1, 'MAKEYOUROWNEMAIL@gmail.com');
INSERT INTO PaymentMethod VALUES(2, 'MAKEYOUROWNEMAIL@gmail.com');
INSERT INTO PaymentMethod VALUES(3, 'MAKEYOUROWNEMAIL@gmail.com');
INSERT INTO PaymentMethod VALUES(4, 'WutWut567@gmail.com');
INSERT INTO PaymentMethod VALUES(5, 'WutWut567@gmail.com');
INSERT INTO PaymentMethod VALUES(6, 'Alibada@gmail.com');
INSERT INTO BankAccount VALUES (1,'MAKEYOUROWNEMAIL@gmail.com','Damian Martelli',286543,43679562);
INSERT INTO BankAccount VALUES (2,'MAKEYOUROWNEMAIL@gmail.com','Damian Martelli',643865,34657890);
INSERT INTO PayPal VALUES (4,'WutWut567@gmail.com','Crazywaddo583@gmail.com');
INSERT INTO PayPal VALUES (3,'MAKEYOUROWNEMAIL@gmail.com','MAKEYOUROWNEMAIL@gmail.com');
INSERT INTO CreditCard VALUES (6,'Alibada@gmail.com','Uruguay','Moshinima');




DELETE FROM Car WHERE regno = 'WTF420'; --ON DELETE WORKS!
UPDATE Car SET regno = 'TAR234' WHERE regno='JAB210'; --ON UPDATE WORKS!

SELECT *
FROM MembershipPlan;
