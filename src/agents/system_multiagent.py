import sqlite3
import os
import datetime
import json
import getpass
from google import genai

# Ruta relativa a la base de datos local
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'inventario.db')

print("\n" + "*"*60)
print(" INICIANDO SISTEMA EXPERTO MULTIAGENTE (LOCAL) ")
print("*"*60)

api_key_segura = getpass.getpass("Ingresa tu API Key de Gemini y presiona Enter: ")
client = genai.Client(api_key=api_key_segura)

class AgenteAtencionIA:
    """Agente 1: Usa IA Generativa para interpretar el mensaje natural."""
    def procesar_solicitud(self, mensaje):
        print(f"\n[Agente 1 - Atención IA]: Analizando intención del usuario...")
        
        prompt_sistema = f"""
        Eres un agente experto en ventas de componentes electrónicos.
        Extrae el nombre del componente y la cantidad solicitada del siguiente mensaje: "{mensaje}"
        
        Reglas estrictas:
        1. Responde ÚNICAMENTE con un formato JSON válido.
        2. Las claves del JSON deben ser: "componente" y "cantidad".
        3. Si no se especifica cantidad, asume que es 1.
        4. Normaliza el nombre del componente (ej. "Motor NEMA17", "ESP32", "Capacitor 100uF", "Driver A4988").
        """
        try:
            respuesta = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_sistema
            )
            texto_limpio = respuesta.text.strip().replace('```json', '').replace('```', '')
            datos_extraidos = json.loads(texto_limpio)
            print(f"[Agente 1]: Intención extraída -> {datos_extraidos}")
            return datos_extraidos
        except Exception as e:
            print(f"[Agente 1]: Error de IA: {e}")
            return None

class AgenteGenerador:
    """Agente 2: Aplica reglas de negocio e interactúa con SQLite."""
    def evaluar_y_procesar(self, datos_solicitud):
        print("[Agente 2 - Generador]: Evaluando inventario y reglas...")
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        
        componente = datos_solicitud.get("componente")
        cantidad_solicitada = datos_solicitud.get("cantidad", 1)
        
        cursor.execute("SELECT id, stock, estado_ciclo, precio_unitario FROM componentes WHERE nombre LIKE ?", (f"%{componente}%",))
        resultado = cursor.fetchone()
        
        if not resultado:
            conexion.close()
            return {"estado": "error", "razon": f"Componente '{componente}' no encontrado en el catálogo."}
            
        id_comp, stock, estado_ciclo, precio = resultado
        
        if stock < cantidad_solicitada:
            conexion.close()
            return {"estado": "rechazado", "razon": f"Stock insuficiente ({stock} disponibles). Sugerir reabastecimiento.", "stock_actual": stock}
            
        total = cantidad_solicitada * precio
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            cursor.execute("INSERT INTO pedidos (fecha, estado_orden) VALUES (?, ?)", (fecha_actual, "Completado"))
            id_pedido = cursor.lastrowid
            cursor.execute("INSERT INTO detalle_pedidos (id_pedido, id_componente, cantidad) VALUES (?, ?, ?)", (id_pedido, id_comp, cantidad_solicitada))
            nuevo_stock = stock - cantidad_solicitada
            cursor.execute("UPDATE componentes SET stock = ? WHERE id = ?", (nuevo_stock, id_comp))
            conexion.commit()
            resultado_final = {"estado": "aprobado", "total": total, "stock_actual": nuevo_stock, "precio": precio, "id_pedido": id_pedido}
        except Exception as e:
            conexion.rollback()
            resultado_final = {"estado": "error", "razon": str(e)}
        finally:
            conexion.close()
        return resultado_final

class AgenteSupervisor:
    """Agente 3: Explica la decisión final al usuario."""
    def explicar_decision(self, datos_solicitud, resultado_inferencia):
        print("[Agente 3 - Supervisor]: Generando explicación...")
        componente = datos_solicitud.get("componente")
        cantidad = datos_solicitud.get("cantidad")
        
        if resultado_inferencia["estado"] == "aprobado":
            explicacion = f"Se autorizó el pedido #{resultado_inferencia['id_pedido']} por {cantidad}x {componente}. Existe stock suficiente. El inventario se ha actualizado (quedan {resultado_inferencia['stock_actual']}). Total: ${resultado_inferencia['total']}."
        else:
            explicacion = f"Se detuvo la venta de {cantidad}x {componente}. Razón: {resultado_inferencia['razon']}"
            
        print("\n" + "="*60)
        print("EXPLICACIÓN PARA EL CLIENTE/ADMIN:")
        print("="*60)
        print(explicacion)
        print("="*60)

if __name__ == "__main__":
    agente_atencion = AgenteAtencionIA()
    agente_generador = AgenteGenerador()
    agente_supervisor = AgenteSupervisor()
    
    while True:
        mensaje_cliente = input("\nCliente (escribe 'salir' para terminar): ")
        if mensaje_cliente.lower() == 'salir':
            print("Apagando sistema...")
            break
            
        datos_estructurados = agente_atencion.procesar_solicitud(mensaje_cliente)
        if datos_estructurados:
            resultado = agente_generador.evaluar_y_procesar(datos_estructurados)
            agente_supervisor.explicar_decision(datos_estructurados, resultado)