import sqlite3
import os
import datetime
import json
import getpass
from google import genai

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'inventario.db')

print("\n" + "*"*60)
print(" INICIANDO SISTEMA EXPERTO MULTIAGENTE (LOCAL) ")
print("*"*60)

api_key_segura = getpass.getpass("Ingresa tu API Key de Gemini y presiona Enter: ")
client = genai.Client(api_key=api_key_segura)

class AgenteAtencionIA:
    """Agente 1: Extrae MÚLTIPLES componentes en un arreglo JSON."""
    def procesar_solicitud(self, mensaje):
        print(f"\n[Agente 1 - Atención IA]: Analizando intención del usuario...")
        
        prompt_sistema = f"""
        Eres un agente experto en ventas de componentes electrónicos.
        Extrae todos los componentes y cantidades solicitadas del siguiente mensaje: "{mensaje}"
        
        Reglas estrictas:
        1. Responde ÚNICAMENTE con un arreglo JSON válido (una lista de objetos). No agregues texto markdown.
        2. Cada objeto debe tener las claves exactas: "componente" y "cantidad".
        3. Si no se especifica cantidad, asume que es 1.
        4. Normaliza el nombre (ej. "Motor NEMA17", "ESP32", "Capacitor 100uF", "Driver A4988").
        
        Ejemplo de respuesta esperada:
        [
            {{"componente": "Motor NEMA17", "cantidad": 3}},
            {{"componente": "Driver A4988", "cantidad": 2}}
        ]
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
    """Agente 2: Evalúa múltiples componentes usando un ciclo."""
    def evaluar_y_procesar(self, lista_solicitud):
        print("[Agente 2 - Generador]: Evaluando inventario para múltiples artículos...")
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        
        total_pedido = 0
        articulos_aprobados = []
        errores = []
        
        try:
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO pedidos (fecha, estado_orden) VALUES (?, ?)", (fecha_actual, "Procesando"))
            id_pedido = cursor.lastrowid
            
            for item in lista_solicitud:
                componente = item.get("componente")
                cantidad = item.get("cantidad", 1)
                
                cursor.execute("SELECT id, stock, estado_ciclo, precio_unitario FROM componentes WHERE nombre LIKE ?", (f"%{componente}%",))
                resultado = cursor.fetchone()
                
                if not resultado:
                    errores.append(f"El componente '{componente}' no existe en el catálogo.")
                    continue
                    
                id_comp, stock, estado_ciclo, precio = resultado
                
                if stock < cantidad:
                    errores.append(f"Stock insuficiente para {componente} (Solicitados: {cantidad}, Disponibles: {stock}).")
                    continue
                    
                if estado_ciclo == "Descontinuado":
                    errores.append(f"El componente {componente} está descontinuado y no se puede vender.")
                    continue
                
                subtotal = cantidad * precio
                total_pedido += subtotal
                nuevo_stock = stock - cantidad
                
                cursor.execute("INSERT INTO detalle_pedidos (id_pedido, id_componente, cantidad) VALUES (?, ?, ?)", (id_pedido, id_comp, cantidad))
                cursor.execute("UPDATE componentes SET stock = ? WHERE id = ?", (nuevo_stock, id_comp))
                
                articulos_aprobados.append(f"{cantidad}x {componente}")
            
            if errores:
                # Rollback
                conexion.rollback()
                return {"estado": "rechazado", "razones": errores}
            else:
                cursor.execute("UPDATE pedidos SET estado_orden = ? WHERE id_pedido = ?", ("Completado", id_pedido))
                conexion.commit()
                return {"estado": "aprobado", "id_pedido": id_pedido, "articulos": articulos_aprobados, "total": total_pedido}
                
        except Exception as e:
            conexion.rollback()
            return {"estado": "error", "razones": [str(e)]}
        finally:
            conexion.close()

class AgenteSupervisor:
    """Agente 3: Explica la decisión final detalladamente."""
    def explicar_decision(self, resultado_inferencia):
        print("[Agente 3 - Supervisor]: Generando explicación...")
        
        if resultado_inferencia["estado"] == "aprobado":
            articulos_str = ", ".join(resultado_inferencia['articulos'])
            explicacion = f"Se autorizó el pedido #{resultado_inferencia['id_pedido']}. Se validó el stock de: {articulos_str}. El inventario de la base de datos se actualizó correctamente. Total a pagar: ${resultado_inferencia['total']}."
        else:
            razones_str = "\n - ".join(resultado_inferencia['razones'])
            explicacion = f"El pedido fue cancelado. Se aplicó la regla de protección de inventario por los siguientes motivos:\n - {razones_str}"
            
        print("\n" + "="*70)
        print("EXPLICACIÓN PARA EL CLIENTE/ADMIN:")
        print("="*70)
        print(explicacion)
        print("="*70)

if __name__ == "__main__":
    agente_atencion = AgenteAtencionIA()
    agente_generador = AgenteGenerador()
    agente_supervisor = AgenteSupervisor()
    
    while True:
        mensaje_cliente = input("\nCliente (escribe 'salir' para terminar): ")
        if mensaje_cliente.lower() == 'salir':
            print("Apagando sistema...")
            break
            
        lista_estructurada = agente_atencion.procesar_solicitud(mensaje_cliente)
        if lista_estructurada:
            resultado = agente_generador.evaluar_y_procesar(lista_estructurada)
            agente_supervisor.explicar_decision(resultado)