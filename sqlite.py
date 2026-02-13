import sqlite3

##Conect to sqlite
connection = sqlite3.connect("student.db")

##Create a cursor object to insert record , create table
cursor = connection.cursor()

##Create the table 
table_info ="""
create table STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25),
SECTION VARCHAR(25),MARKS INT)
"""
cursor.execute(table_info)

##Insert some more records
cursor.execute('''Insert into STUDENT values('Krish','Data Science','A',90)''')
cursor.execute('''Insert into STUDENT values('John','Data Science','A',90)''')
cursor.execute('''Insert into STUDENT values('Pushkar','Data Science','A',90)''')
cursor.execute('''Insert into STUDENT values('Raj','Data Science','A',90)''')
cursor.execute('''Insert into STUDENT values('Krishna','Data Science','A',90)''')

##Display all the record
print("The inserted records are")
data = cursor.execute('''Select * from STUDENT''')
for row in data:
    print(row)

##Commit your changes in the database
connection.commit()
connection.close()