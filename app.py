from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os

# Инициализация Flask с правильными путями
app = Flask(
    __name__,
    template_folder=os.path.abspath('../templates'),  # Путь к шаблонам
    static_folder=os.path.abspath('../static')       # Путь к статике
)
CORS(app)  # Разрешаем CORS для всех доменов

# Конфигурация подключения к MySQL (без пароля)
def create_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",      # Стандартный пользователь
            password="",      # Пустой пароль
            database="warehouse_db"
        )
    except Error as e:
        print(f"Ошибка подключения к MySQL: {e}")
        return None

# Роут для главной страницы
@app.route('/')
def home():
    return render_template('index.html')

# Отдача статических файлов
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

# ============ API для товаров ============

# Получить все товары
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    product_id as id,
                    product_name as name,
                    category,
                    quantity,
                    min_quantity as min,
                    added_date as date
                FROM products
            """)
            products = cursor.fetchall()
            return jsonify(products)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return jsonify({"error": "Database connection failed"}), 500

# Добавить новый товар
@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    
    # Проверка обязательных полей
    required_fields = ['id', 'name', 'category', 'quantity', 'min']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products 
                (product_id, product_name, category, quantity, min_quantity, added_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data['id'],
                data['name'],
                data['category'],
                int(data['quantity']),
                int(data['min']),
                data.get('date', datetime.now().strftime('%Y-%m-%d'))
            ))
            conn.commit()
            return jsonify({"status": "success", "id": data['id']}), 201
        except Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return jsonify({"error": "Database connection failed"}), 500

# Обновить товар
@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products 
                SET 
                    product_name = %s,
                    category = %s,
                    quantity = %s,
                    min_quantity = %s,
                    added_date = %s
                WHERE product_id = %s
            """, (
                data['name'],
                data['category'],
                int(data['quantity']),
                int(data['min']),
                data.get('date', datetime.now().strftime('%Y-%m-%d')),
                product_id
            ))
            conn.commit()
            return jsonify({"status": "success"})
        except Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return jsonify({"error": "Database connection failed"}), 500

# Удалить товар
@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
            conn.commit()
            return jsonify({"status": "deleted"})
        except Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return jsonify({"error": "Database connection failed"}), 500

# Запуск сервера с проверкой путей
if __name__ == '__main__':
    print("Путь к шаблонам:", os.path.abspath(app.template_folder))
    print("Путь к статике:", os.path.abspath(app.static_folder))
    app.run(debug=True, host='0.0.0.0', port=5000)