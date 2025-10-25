"""
app/main.py

A simple and **intentionally vulnerable** Flask application designed as a
scanning target for the DevSecOps AI pipeline.

WARNING: DO NOT USE IN PRODUCTION.
"""

import sqlite3
from flask import Flask, request, g, jsonify

app = Flask(__name__)
DATABASE = 'users.db'

def get_db():
    """
    Establishes or retrieves a connection to the SQLite database.
    Uses the Flask global context (g) to manage the connection.

    Returns:
        sqlite3.Connection: A connection to the database.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    """
    Closes the database connection at the end of the request.
    
    Args:
        exception (Exception, optional): An exception if one was raised.
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/user')
def get_user():
    """
    Retrieves a user from the database based on a query parameter.
    
    **INTENTIONAL VULNERABILITY**: This function contains a critical
    SQL Injection vulnerability for demonstration purposes.
    
    Returns:
        str: A string representation of the user, or an error.
    """
    user_id = request.args.get('id')
    db = get_db()
    
    #
    # --- 🔴 INTENTIONAL VULNERABILITY: SQL INJECTION ---
    # WARNING: This uses an f-string to build a query, which allows
    # for SQL Injection. This is the vulnerability our AI scanner
    # is designed to find.
    #
    cursor = db.execute(f"SELECT * FROM users WHERE id = {user_id}")
    
    user = cursor.fetchone()
    
    #
    # --- 🔴 INTENTIONAL BAD PRACTICE: Data Leakage ---
    # WARNING: Returning the raw tuple as a string can leak
    # unexpected data. A professional implementation would use
    # jsonify with specific fields.
    #
    return str(user)

def init_db():
    """
    Initializes the database with the required schema and demo data.
    This function is intended for setup and is not part of the main app logic.
    """
    with app.app_context():
        db = get_db()
        db.execute("CREATE TABLE IF NOT EXISTS users (id TEXT, name TEXT)")
        db.execute("INSERT OR IGNORE INTO users (id, name) VALUES ('1', 'admin')")
        db.commit()

if __name__ == '__main__':
    init_db()
    
    #
    # --- 🔴 INTENTIONAL BAD PRACTICE: Debug Mode ---
    # WARNING: Running with debug=True in a production-like
    # environment is a security risk. This is another finding
    # for our AI scanner.
    #
    app.run(debug=True)
