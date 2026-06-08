import sqlite3
import os

def crear_base_datos():
    db_path = os.path.join(os.path.dirname(__file__), 'inventario.db')
    
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()

    # 1. Crear tabla: componentes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS componentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        categoria TEXT NOT NULL,
        stock INTEGER NOT NULL,
        estado_ciclo TEXT NOT NULL,
        precio_unitario REAL NOT NULL
    )
    ''')

    # 2. Crear tabla: pedidos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pedidos (
        id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        descuento_aplicado REAL DEFAULT 0.0,
        estado_orden TEXT NOT NULL
    )
    ''')

    # 3. Crear tabla: detalle_pedidos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS detalle_pedidos (
        id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
        id_pedido INTEGER NOT NULL,
        id_componente INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
        FOREIGN KEY (id_componente) REFERENCES componentes(id)
    )
    ''')

    cursor.execute('DELETE FROM componentes')

    componentes_prueba = [
        ('Motor NEMA17', 'Actuador', 15, 'Recomendado', 250.50),
        ('Driver A4988', 'Controlador', 50, 'Recomendado', 45.00),
        ('ESP32', 'Microcontrolador', 5, 'Recomendado', 120.00),
        ('Capacitor 100uF', 'Pasivo', 0, 'Activo', 5.00),
        ('Arduino UNO R3', 'Placa de desarrollo', 2, 'Descontinuado', 350.00)
    ]

    cursor.executemany('''
    INSERT INTO componentes (nombre, categoria, stock, estado_ciclo, precio_unitario)
    VALUES (?, ?, ?, ?, ?)
    ''', componentes_prueba)

    # Guardar los cambios y cerrar la conexión
    conexion.commit()
    conexion.close()
    
    print(f"Base de datos inicializada correctamente en: {db_path}")
    print("Tablas creadas e inventario de prueba insertado.")

if __name__ == '__main__':
    crear_base_datos()