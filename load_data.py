import pymysql
import csv

# Connection details
host = ""
user = ""
password = ""
database = ""
CSV_FILE_PATH = ''
TABLE_NAME = 'heroes'

try:
    # Connect to the database
    connection = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = connection.cursor()

    with open(CSV_FILE_PATH, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            sql = f"""
                INSERT INTO {TABLE_NAME} (id, name, hero, power, xp, color)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (row['id'], row['name'], row['hero'], row['power'], row['xp'], row['color'])
            try:
                cursor.execute(sql, values)
                print(f"Data inserted successfully for id {row['id']}")
            except Exception as e:
                print(f"Error inserting row with id {row['id']}: {e}")

    # Commit the changes to the database
    connection.commit()
    print("Data loading from CSV complete.")

except pymysql.Error as e:
    print(f"Error connecting to or interacting with the database: {e}")

finally:
    if connection:
        connection.close()
