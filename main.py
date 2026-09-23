import json
import os
import requests
# Cargar base de datos simulada de pedidos
def cargar_base_datos():
    path = os.path.join("database", "mock_orders.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Función para consultar a un LLM usando la API de Groq (modelo Llama-3)
def consultar_llm(prompt):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "ERROR: No se encontró el API Key de Groq. Asegúrate de configurar la variable de entorno GROQ_API_KEY."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Modelos recomendados y soportados por Groq
    candidate_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-20b"
    ]
    
    for model_name in candidate_models:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 800
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.ok:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
        except Exception:
            continue

    # Fallback: Auto-descubrir modelo activo de texto en Groq
    try:
        models_resp = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
        if models_resp.ok:
            available = [m['id'] for m in models_resp.json().get('data', []) if 'whisper' not in m['id'] and 'guard' not in m['id']]
            if available:
                payload = {
                    "model": available[0],
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "max_tokens": 800
                }
                res = requests.post(url, headers=headers, json=payload, timeout=60)
                if res.ok:
                    return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error al consultar Groq: {e}"

    return "Error: No se pudo conectar a ningún modelo de texto activo de Groq."


# Ejercicio 1A: Prompt de Solicitud de Pedido (Básico)
def generar_prompt_estado_pedido_basico(tracking_number, db_pedidos):
    # Agregar el documento/texto con el estado de los pedidos al prompt
    db_texto = json.dumps(db_pedidos, indent=2, ensure_ascii=False)
    prompt = f"Dame el estado del pedido {tracking_number}.\n\nBase de datos:\n{db_texto}"
    return prompt

# Ejercicio 1B: Prompt de Solicitud de Pedido (Mejorado)
def generar_prompt_estado_pedido_mejorado(tracking_number, db_pedidos):
    # Agregar el documento/texto con el estado de los pedidos al prompt
    db_texto = json.dumps(db_pedidos, indent=2, ensure_ascii=False)
    
    system_prompt = (
        "Actúa como un agente de servicio al cliente amable, profesional y empático de la empresa EcoMarket. "
        "Tu objetivo es informar al cliente sobre el estado de su pedido basándote EXCLUSIVAMENTE en la base de datos proporcionada. "
        "Si el estado es 'Retrasado', debes ofrecer una sincera disculpa en nombre de EcoMarket y una breve explicación comercial comprensiva. "
        "Incluye siempre la estimación de la fecha de entrega y el enlace oficial para rastrear el paquete en tiempo real. "
        "IMPORTANTE: Responde de manera muy concisa, utilizando un máximo de dos párrafos cortos para no saturar al cliente."
    )
    
    user_context = f"[BASE DE DATOS DE PEDIDOS]\n{db_texto}"
    
    instruction = f"Por favor redacta la respuesta formal para el cliente solicitando el estado del pedido: {tracking_number}."
    
    prompt_final = f"{system_prompt}\n\n{user_context}\n\nInstrucción: {instruction}"
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
        "incluso si la devolución física no es posible.\n"
        "IMPORTANTE: Sé directo y conciso. La respuesta debe ser de un máximo de dos o tres párrafos."
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
    
    print("=== PRUEBA EJERCICIO 1A: Estado de Pedido (PROMPT BÁSICO) ===" )
    prompt_p1_basico = generar_prompt_estado_pedido_basico("ECO-1003", db)
    print("-> Prompt generado:\n", prompt_p1_basico[:120] + "\n\n... [Documento de pedidos JSON truncado para no llenar la consola] ...")
    print("\n-> Respuesta del LLM (Groq - Llama 3):")
    print(consultar_llm(prompt_p1_basico))
    
    print("\n" + "="*50 + "\n")
    
    print("=== PRUEBA EJERCICIO 1B: Estado de Pedido (PROMPT MEJORADO) ===" )
    prompt_p1_mejorado = generar_prompt_estado_pedido_mejorado("ECO-1003", db)
    print("-> Prompt generado:\n", prompt_p1_mejorado[:390] + "\n\n... [Documento de pedidos JSON truncado para no llenar la consola] ...\n\nInstrucción: Por favor redacta...")
    print("\n-> Respuesta del LLM (Groq - Llama 3):")
    print(consultar_llm(prompt_p1_mejorado))
    
    print("\n" + "="*50 + "\n")
    
    print("=== PRUEBA EJERCICIO 2: Devolución (Producto de Higiene - No elegible) ===")
    prompt_p2 = generar_prompt_devolucion(
        producto="Cepillo de dientes de bambú usado / Kit de afeitar", 
        categoria="Higiene personal", 
        motivo="El cliente cambió de opinión tras abrir el empaque."
    )
    print("-> Prompt generado:\n", prompt_p2)
    print("\n-> Respuesta del LLM (Groq - Llama 3):")
    print(consultar_llm(prompt_p2))