# app/main.py
from flask import Flask, request, g
import sqlite3

app = Flask(__name__)
DATABASE = 'users.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # AQUÍ ESTABA EL ERROR: 'sqliteite3'
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/user')
def get_user():
    # ¡VULNERABILIDAD INTENCIONAL DE INYECCIÓN SQL!
    user_id = request.args.get('id')
    db = get_db()
    
    # Esta construcción de string es peligrosa
    cursor = db.execute(f"SELECT * FROM users WHERE id = {user_id}")
    
    user = cursor.fetchone()
    return str(user)

if __name__ == '__main__':
    # Configuración inicial de la BD (solo para demo)
    with app.app_context():
        db = get_db()
        db.execute("CREATE TABLE IF NOT EXISTS users (id TEXT, name TEXT)")
        db.execute("INSERT OR IGNORE INTO users (id, name) VALUES ('1', 'admin')")
        db.commit()
    
    app.run(debug=True)
