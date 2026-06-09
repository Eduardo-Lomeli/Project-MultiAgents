import sqlite3
import os

# Definir la ruta relativa a la base de datos local
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'inventario.db')

class AgenteAtencion:
    """Agente 1: Interpreta la solicitud inicial del usuario."""
    def procesar_solicitud(self, mensaje):
        print(f"[Agente 1 - Atención]: Recibiendo mensaje: '{mensaje}'")
        
        # En una versión avanzada, aquí usarías NLP (Procesamiento de Lenguaje Natural) 
        # para extraer las entidades. Por ahora, simulamos que interpretó la intención.
        # Simulamos que entendió: "Hola, necesito 3 motores NEMA17..."
        datos_extraidos = {"componente": "Motor NEMA17", "cantidad": 3}
        print(f"[Agente 1 - Atención]: Intención extraída -> {datos_extraidos}\n")
        return datos_extraidos

class AgenteGenerador:
    """Agente 2: Aplica reglas de negocio e inferencias sobre el inventario."""
    def evaluar_pedido(self, datos_solicitud):
        print("[Agente 2 - Generador]: Conectando a BD y evaluando reglas de negocio...")
        
        # Conexión a la base de datos obligatoria
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        
        componente = datos_solicitud["componente"]
        cantidad_solicitada = datos_solicitud["cantidad"]
        
        cursor.execute("SELECT id, stock, estado_ciclo, precio_unitario FROM componentes WHERE nombre = ?", (componente,))
        resultado = cursor.fetchone()
        conexion.close()
        
        if not resultado:
            return {"estado": "error", "razon": "Componente no encontrado en el inventario."}
            
        id_comp, stock, estado_ciclo, precio = resultado
        
        # --- REGLAS DE INFERENCIA LÓGICA ---
        
        # Regla 1: Validar stock
        if stock < cantidad_solicitada:
            return {
                "estado": "rechazado", 
                "razon": "Stock insuficiente. Sugerir reabastecimiento.", 
                "stock_actual": stock
            }
            
        # Regla 2: Validar ciclo de vida del componente
        if estado_ciclo == "Descontinuado":
            return {
                "estado": "advertencia", 
                "razon": "El componente está descontinuado. No se recomienda para nuevos diseños."
            }
            
        # Si aprueba todas las reglas de negocio
        total = cantidad_solicitada * precio
        print("[Agente 2 - Generador]: Inferencias completadas. Pedido viable.\n")
        return {"estado": "aprobado", "total": total, "stock_actual": stock, "precio": precio}

class AgenteSupervisor:
    """Agente 3: Explica de manera transparente las decisiones tomadas."""
    def explicar_decision(self, datos_solicitud, resultado_inferencia):
        print("[Agente 3 - Supervisor]: Generando explicación de la decisión del sistema...")
        
        componente = datos_solicitud["componente"]
        cantidad = datos_solicitud["cantidad"]
        
        # Estructurar la explicación basada en el resultado
        if resultado_inferencia["estado"] == "aprobado":
            explicacion = f"Se detectó que el cliente solicitó {cantidad} unidades de {componente}. Existe stock suficiente ({resultado_inferencia['stock_actual']} disponibles en almacén). El pedido es viable y el total a pagar es de ${resultado_inferencia['total']}."
        else:
            explicacion = f"Se detuvo la solicitud de {cantidad} unidades de {componente}. Razón del sistema: {resultado_inferencia['razon']}"
            
        print("\n" + "="*50)
        print("EXPLICACIÓN FINAL PARA EL USUARIO:")
        print("="*50)
        print(explicacion)
        print("="*50 + "\n")

# --- Orquestador Principal (Ejecución Local) ---
if __name__ == "__main__":
    # 1. Instanciar los 3 agentes
    agente_atencion = AgenteAtencion()
    agente_generador = AgenteGenerador()
    agente_supervisor = AgenteSupervisor()
    
    # 2. Simular la entrada del cliente por consola
    print("\n--- INICIANDO SISTEMA MULTIAGENTE ---\n")
    mensaje_cliente = "Hola, necesito 3 motores NEMA17 para mi proyecto de robótica."
    
    # 3. Flujo de comunicación entre agentes
    datos_estructurados = agente_atencion.procesar_solicitud(mensaje_cliente) # Agente 1
    resultado = agente_generador.evaluar_pedido(datos_estructurados)          # Agente 2
    agente_supervisor.explicar_decision(datos_estructurados, resultado)       # Agente 3