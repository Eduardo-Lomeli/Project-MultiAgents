# Sistema Experto Multiagente: Gestión de Componentes Electrónicos

## Información del Autor
* **Nombre:** Luis Eduardo Lomeli Saavedra
* **Registro:** 23110132

## Descripción del Proyecto
Este repositorio contiene un sistema experto basado en agentes inteligentes para la gestión de un inventario de componentes electrónicos. El sistema opera localmente a través de una interfaz de línea de comandos (CLI) y es capaz de procesar solicitudes complejas en lenguaje natural, consultar disponibilidad, aplicar reglas lógicas deductivas y explicar sus decisiones al usuario.

## Arquitectura del Sistema
El funcionamiento se divide en una arquitectura de tres agentes:
1. **Agente de Atención al Cliente:** Interfaz de procesamiento de lenguaje natural (NLP). Emplea IA Generativa (Google Gemini) para interpretar el mensaje del usuario y generar un formato de datos estructurado.
2. **Agente Generador de Pedidos:** Motor de inferencia del sistema. Valida los datos estructurados contra una base de datos relacional aplicando reglas lógicas (por ejemplo, validación de stock y revisión del estado de vida del componente).
3. **Agente Supervisor:** Módulo de trazabilidad. Genera explicaciones detalladas que justifican la aprobación, modificación o cancelación de las solicitudes procesadas.

## Estructura del Repositorio
```text
/
├── docs/
│   └── GG_registro_Proy.pdf       # Documentación oficial y reporte del proyecto
├── src/
│   ├── agents/
│   │   └── sistema_multiagente.py # Lógica principal y bucle de los tres agentes
│   └── database/
│       ├── init_db.py             # Script de inicialización de tablas y datos semilla
│       └── inventario.db          # Base de datos SQLite (generada localmente)
└── README.md