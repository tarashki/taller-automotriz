from flask import Flask, request, redirect, render_template, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'clave_secreta_taller'

def get_db_connection():
    conn = sqlite3.connect('bd_taller.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            precio REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            telefono TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mantenimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            servicio_id INTEGER NOT NULL,
            cliente_id INTEGER NOT NULL,
            FOREIGN KEY (servicio_id) REFERENCES servicios (id) ON DELETE CASCADE,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def seed_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM servicios')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO servicios (descripcion, precio) VALUES (?, ?)
        ''', [
            ('Cambio de Aceite y Filtro', 150.0),
            ('Alineación y Balanceo', 120.0),
            ('Diagnóstico Escáner Computarizado', 80.0)
        ])

        cursor.executemany('''
            INSERT INTO clientes (nombre, apellidos, telefono) VALUES (?, ?, ?)
        ''', [
            ('Carlos', 'Mendoza Quispe', '71234567'),
            ('Maria', 'Flores Choque', '77654321'),
            ('Javier', 'Mamani Aliaga', '68001122')
        ])

        cursor.executemany('''
            INSERT INTO mantenimientos (fecha, servicio_id, cliente_id) VALUES (?, ?, ?)
        ''', [
            ('2026-03-01', 1, 1),
            ('2026-03-02', 2, 1),
            ('2026-03-05', 3, 3)
        ])

        conn.commit()

    conn.close()

init_db()
seed_db()

@app.route('/')
def index():
    return redirect(url_for('clientes'))

# --- CLIENTES ---
@app.route('/clientes')
def clientes():
    conn = get_db_connection()
    clientes = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes)

@app.route("/cliente/nuevo", methods=["GET", "POST"])
def nuevo_cliente():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        telefono = request.form["telefono"]
        
        conn = get_db_connection()
        conn.execute("INSERT INTO clientes (nombre, apellidos, telefono) VALUES (?, ?, ?)", (nombre, apellidos, telefono))
        conn.commit()
        conn.close()
        flash("Cliente registrado exitosamente.", "success")
        return redirect(url_for("clientes"))
    return render_template("form_cliente.html")

@app.route('/cliente/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    conn = get_db_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        telefono = request.form['telefono']
        
        conn.execute('UPDATE clientes SET nombre = ?, apellidos = ?, telefono = ? WHERE id = ?', (nombre, apellidos, telefono, id))
        conn.commit()
        conn.close()
        flash("Cliente actualizado exitosamente.", "success")
        return redirect(url_for('clientes'))
        
    conn.close()
    return render_template('form_cliente.html', cliente=cliente)

@app.route('/cliente/eliminar/<int:id>')
def eliminar_cliente(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash("Cliente eliminado exitosamente.", "success")
    return redirect(url_for('clientes'))

if __name__ == '__main__':
    app.run(debug=True)