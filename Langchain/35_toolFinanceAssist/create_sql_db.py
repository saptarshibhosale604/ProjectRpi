import sqlite3
import os

# Define the directory and database name
directory = '/root/Test'
db_name = 'db_test.db'
db_path = os.path.join(directory, db_name)

# Create the directory if it doesn't exist
os.makedirs(directory, exist_ok=True)

# Connect to the SQLite database (it will create the database if it doesn't exist)
conn = sqlite3.connect(db_path)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create the table with the specified structure
cursor.execute('''
CREATE TABLE IF NOT EXISTS table_test (
    investment_type TEXT,
    invested_value INTEGER,
    current_value INTEGER
)
''')

# Insert the data into the table
data = [
    ('Physical', 7100, 7100),
    ('Stocks', 45800, 49100),
    ('MF', 75000, 87600),
    ('FD', 120000, 120000),
    ('Saving', 14800, 14800)
]

cursor.executemany('INSERT INTO table_test (investment_type, invested_value, current_value) VALUES (?, ?, ?)', data)

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"Database created and saved at: {db_path}")

