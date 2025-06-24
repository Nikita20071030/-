# backend/database.py
import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="ваш_логин",
            password="ваш_пароль",
            database="warehouse_db"
        )
        return connection
    except Error as e:
        print(f"Ошибка подключения: {e}")
        return None

def get_products():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        cursor.close()
        connection.close()
        return products