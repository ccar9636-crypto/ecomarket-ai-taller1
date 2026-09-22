import json
import os
import requests
import google.generativeai as genai
# Cargar base de datos simulada de pedidos
def cargar_base_datos():
    path = os.path.join("database", "mock_orders.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Función para consultar a un LLM usando la SDK oficial de Google Gemini
def consultar_llm(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "ERROR: No se encontró el API Key de Gemini. Asegúrate de configurar la variable de entorno GEMINI_API_KEY."
    
    try:
        # Configurar la llave
        genai.configure(api_key=api_key)
        
        # Instanciar el modelo oficial recomendado por Google
        model = genai.GenerativeModel("gemini-3.6-flash")
        
        # Generar contenido
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.5,
                max_output_tokens=1024,
            )
        )
        return response.text.strip()
    except Exception as e:
        return f"Error al consultar Gemini: {e}"


# Ejercicio 1: Prompt de Solicitud de Pedido con Contexto Integrado
def generar_prompt_estado_pedido(tracking_number, db_pedidos):
    # Buscar el pedido en la base de datos local (simulando RAG)
    pedido_info = next((p for p in db_pedidos if p["tracking_number"] == tracking_number), None)
    
    if not pedido_info:
        return "El número de seguimiento proporcionado no existe en nuestros registros."

    # Estructura avanzada del prompt con Rol, Contexto Estricto y Restricciones
    system_prompt = (
        "Actúa como un agente de servicio al cliente amable, profesional y empático de la empresa EcoMarket. "
        "Tu objetivo es informar al cliente sobre el estado de su pedido basándote EXCLUSIVAMENTE en el contexto proporcionado. "
        "Si el estado es 'Retrasado', debes ofrecer una sincera disculpa en nombre de EcoMarket y una breve explicación comercial comprensiva. "
        "Incluye siempre la estimación de la fecha de entrega y el enlace oficial para rastrear el paquete en tiempo real."
    )
    
    user_context = f"""
    [CONTEXTO DE DATOS DEL PEDIDO]
    - Número de seguimiento: {pedido_info['tracking_number']}
    - Cliente: {pedido_info['cliente']}
    - Estado actual: {pedido_info['estado']}
    - Fecha estimada de entrega: {pedido_info['fecha_estimada']}
    - Enlace de rastreo: {pedido_info['url_rastreo']}
    """
    
    instruction = f"Por favor redacta la respuesta formal para el cliente solicitando el estado del pedido: {tracking_number}."
    
    prompt_final = f"{system_prompt}\n{user_context}\nInstrucción: {instruction}"
    return prompt_final

# Ejercicio 2: Prompt de Devolución de Producto con Distinción de Políticas
def generar_prompt_devolucion(producto, categoria, motivo):
    system_prompt = (
        "Actúa como un asesor experto en políticas de satisfacción al cliente de EcoMarket. "
        "Debes guiar al cliente en el proceso de devolución aplicando estrictamente las siguientes reglas:\n"
        "1. REGLA CRÍTICA: Los productos perecederos (alimentos, cosméticos abiertos) y productos de higiene personal "
        "NO admiten devolución por normativas de salud y seguridad.\n"
        "2. Los productos sostenibles estándar (ropa ecológica, utensilios reutilizables, accesorios) SÍ admiten devolución dentro de los primeros 30 días.\n"
        "3. La respuesta debe ser sumamente clara, respetuosa y empática, ofreciendo alternativas (como bonos o notas de crédito) "
        "incluso si la devolución física no es posible."
    )
    
    user_context = f"""
    [DETALLES DE LA SOLICITUD DE DEVOLUCIÓN]
    - Producto: {producto}
    - Categoría: {categoria}
    - Motivo del cliente: {motivo}
    """
    
    instruction = "Redacta la respuesta empática y fundamentada indicando si procede o no la devolución y cuáles son los pasos a seguir."
    
    prompt_final = f"{system_prompt}\n{user_context}\nInstrucción: {instruction}"
    return prompt_final

if __name__ == "__main__":
    db = cargar_base_datos()
    
    print("=== PRUEBA EJERCICIO 1: Estado de Pedido (Retrasado) ===" )
    prompt_p1 = generar_prompt_estado_pedido("ECO-1003", db)
    print("-> Prompt generado:\n", prompt_p1)
    print("\n-> Respuesta del LLM (Gemini):")
    print(consultar_llm(prompt_p1))
    
    print("\n" + "="*50 + "\n")
    
    print("=== PRUEBA EJERCICIO 2: Devolución (Producto de Higiene - No elegible) ===")
    prompt_p2 = generar_prompt_devolucion(
        producto="Cepillo de dientes de bambú usado / Kit de afeitar", 
        categoria="Higiene personal", 
        motivo="El cliente cambió de opinión tras abrir el empaque."
    )
    print("-> Prompt generado:\n", prompt_p2)
    print("\n-> Respuesta del LLM (Gemini):")
    print(consultar_llm(prompt_p2))