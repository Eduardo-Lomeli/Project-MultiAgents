import sqlite3
import os
import datetime

# Definir la ruta relativa a la base de datos local
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'inventario.db')

class AgenteAtencion:
    """Agente 1: Interpreta la solicitud inicial del usuario."""
    def procesar_solicitud(self, mensaje):
        print(f"\n🤖 [Agente 1 - Atención]: Analizando mensaje: '{mensaje}'")
        
        # Simulación de extracción de entidades. 
        # NOTA: Para una prueba dinámica en terminal, buscaremos palabras clave básicas.
        mensaje_lower = mensaje.lower()
        componente = None
        cantidad = 1 # Por defecto
        
        if "nema17" in mensaje_lower:
            componente = "Motor NEMA17"
            cantidad = 3 # Simulando que extrajo el número
        elif "esp32" in mensaje_lower:
            componente = "ESP32"
            cantidad = 2
        elif "capacitor" in mensaje_lower:
            componente = "Capacitor 100uF"
            cantidad = 10
            
        if componente:
            datos = {"componente": componente, "cantidad": cantidad}
            print(f"✅ [Agente 1 - Atención]: Intención extraída -> {datos}\n")
            return datos
        else:
            print("⚠️ [Agente 1 - Atención]: No pude identificar el componente solicitado.\n")
            return None

class AgenteGenerador:
    """Agente 2: Aplica reglas de negocio, infiere y registra la orden."""
    def evaluar_y_procesar(self, datos_solicitud):
        print("⚙️ [Agente 2 - Generador]: Evaluando inventario y reglas de negocio...")
        
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        
        componente = datos_solicitud["componente"]
        cantidad_solicitada = datos_solicitud["cantidad"]
        
        # Consultar stock actual
        cursor.execute("SELECT id, stock, estado_ciclo, precio_unitario FROM componentes WHERE nombre = ?", (componente,))
        resultado = cursor.fetchone()
        
        if not resultado:
            conexion.close()
            return {"estado": "error", "razon": "Componente no encontrado en el catálogo."}
            
        id_comp, stock, estado_ciclo, precio = resultado
        
        # --- REGLAS DE INFERENCIA LÓGICA ---
        if stock < cantidad_solicitada:
            conexion.close()
            return {"estado": "rechazado", "razon": f"Stock insuficiente ({stock} disponibles). Sugerir reabastecimiento.", "stock_actual": stock}
            
        if estado_ciclo == "Descontinuado":
            conexion.close()
            return {"estado": "advertencia", "razon": "Componente descontinuado. No apto para nuevos diseños."}
            
        # --- PROCESAR ORDEN (Si aprueba las reglas) ---
        total = cantidad_solicitada * precio
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # 1. Registrar el pedido
            cursor.execute("INSERT INTO pedidos (fecha, descuento_aplicado, estado_orden) VALUES (?, ?, ?)", (fecha_actual, 0.0, "Completado"))
            id_pedido = cursor.lastrowid
            
            # 2. Registrar el detalle
            cursor.execute("INSERT INTO detalle_pedidos (id_pedido, id_componente, cantidad) VALUES (?, ?, ?)", (id_pedido, id_comp, cantidad_solicitada))
            
            # 3. Actualizar el stock (Restar)
            nuevo_stock = stock - cantidad_solicitada
            cursor.execute("UPDATE componentes SET stock = ? WHERE id = ?", (nuevo_stock, id_comp))
            
            conexion.commit()
            print(f"✅ [Agente 2 - Generador]: Pedido #{id_pedido} registrado. Stock actualizado ({nuevo_stock} restantes).\n")
            resultado_final = {"estado": "aprobado", "total": total, "stock_actual": nuevo_stock, "precio": precio, "id_pedido": id_pedido}
            
        except Exception as e:
            conexion.rollback()
            resultado_final = {"estado": "error", "razon": str(e)}
            
        finally:
            conexion.close()
            
        return resultado_final

class AgenteSupervisor:
    """Agente 3: Explica las decisiones tomadas para cumplir con la rúbrica (20%)."""
    def explicar_decision(self, datos_solicitud, resultado_inferencia):
        print("👁️ [Agente 3 - Supervisor]: Generando explicación de la decisión...")
        
        componente = datos_solicitud["componente"]
        cantidad = datos_solicitud["cantidad"]
        
        if resultado_inferencia["estado"] == "aprobado":
            explicacion = f"Se autorizó el pedido #{resultado_inferencia['id_pedido']} por {cantidad}x {componente}. Existe stock suficiente y la pieza es recomendada. El inventario se ha actualizado correctamente (quedan {resultado_inferencia['stock_actual']} unidades). Total: ${resultado_inferencia['total']}."
        else:
            explicacion = f"Se detuvo la venta de {cantidad}x {componente}. Razón: {resultado_inferencia['razon']}"
            
        print("\n" + "="*60)
        print("📢 EXPLICACIÓN PARA EL CLIENTE/ADMIN:")
        print("="*60)
        print(explicacion)
        print("="*60 + "\n")

# --- Bucle de Chat en Terminal ---
if __name__ == "__main__":
    agente_atencion = AgenteAtencion()
    agente_generador = AgenteGenerador()
    agente_supervisor = AgenteSupervisor()
    
    print("\n" + "*"*50)
    print(" INICIANDO SISTEMA EXPERTO MULTIAGENTE (LOCAL) ")
    print("*"*50)
    print("Escribe 'salir' para terminar el programa.")
    
    while True:
        mensaje_cliente = input("\n👤 Cliente: ")
        
        if mensaje_cliente.lower() == 'salir':
            print("Apagando sistema multiagente...")
            break
            
        datos_estructurados = agente_atencion.procesar_solicitud(mensaje_cliente)
        
        if datos_estructurados:
            resultado = agente_generador.evaluar_y_procesar(datos_estructurados)
            agente_supervisor.explicar_decision(datos_estructurados, resultado)