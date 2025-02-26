import sqlite3
import os

# Define the directory and database name
directory = '/root/Test'
db_name = 'db_test.db'
db_path = os.path.join(directory, db_name)

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Query to select all data from the table
#cursor.execute('SELECT *,  ("Current Value" - "Invested Value") AS profit FROM table_test')
cursor.execute('SELECT investment_type, invested_value, current_value, (current_value - invested_value) AS profit FROM table_test;')

# Fetch all rows from the executed query
rows = cursor.fetchall()

# Print the data
print("Investment Type | Invested Value | Current Value")
print("------------------------------------------------")
for row in rows:
    print(row)
    #investment_type, invested_value, current_value = row
    #print(f"{investment_type:<15} | {invested_value:<15} | {current_value:<15}")

# Close the connection
conn.close()
