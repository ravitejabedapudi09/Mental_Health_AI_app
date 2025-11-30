import mysql.connector

def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin123",
        database="chatapp"
    )

def register_user(username, email, password):
    conn = create_connection()
    cursor = conn.cursor()

    # Check if email OR username exists
    cursor.execute("SELECT * FROM users WHERE email=%s OR username=%s", (email, username))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return False  # Already exists

    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                   (username, email, password))
    conn.commit()
    conn.close()
    return True

def validate_login(email, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user
