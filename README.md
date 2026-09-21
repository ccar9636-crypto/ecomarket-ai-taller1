# Desarrollo del Taller Práctico #1: EcoMarket

## Integrantes:

- [Deibi Bastidas Cerón]
- [Camilo Arciniegas Forero]

## Fase 1: Selección y Justificación del Modelo de IA

### 1. Tipo de modelo de IA generativa adecuado

Para resolver el cuello de botella de **EcoMarket**, donde el 80 % de las consultas son repetitivas y transaccionales, mientras que el 20 % restante requiere empatía y mayor capacidad de razonamiento, la arquitectura más idónea es una **solución híbrida basada en un Modelo de Lenguaje Pequeño (SLM) o Grande (LLM) de código abierto**, de propósito general, potenciado con una arquitectura **RAG (Retrieval-Augmented Generation)** y un sistema de enrutamiento de intenciones (*Intent Routing*).

Específicamente, se propone el uso de un modelo *open-source* eficiente como **Llama-3-8B-Instruct** o **Mistral-7B-Instruct**, ejecutado mediante un pipeline híbrido:

- **Para el 80 % transaccional (Pedidos, Envíos, Catálogo):** Se acopla el SLM con una base de datos relacional y un sistema RAG determinista que consulta en tiempo real el estado de los pedidos, evitando alucinaciones.
- **Para el 20 % complejo (Quejas, Soporte técnico, Empatía):** Se utiliza el mismo modelo base, pero con un *System Prompt* avanzado que prioriza la sensibilidad, derivando automáticamente los casos críticos a agentes humanos cuando la polaridad del sentimiento del cliente sea negativa.

### 2. ¿Por qué este modelo y no otro?

- **Precisión vs. fluidez:** Un modelo cerrado masivo, como GPT-4, ofrecería alta fluidez, pero podría generar mayores costos operativos para miles de consultas diarias en una empresa en crecimiento. Un modelo *open-source* de 7B a 8B parámetros ofrece un balance entre capacidad para mantener un tono empático y agilidad para integrarse localmente o en servidores propios, favoreciendo además el control sobre los datos.

- **Control de alucinaciones en datos transaccionales:** Al separar la lógica de negocio mediante RAG, el modelo no debe "adivinar" el estado del pedido, sino consultar directamente la información disponible en la base de datos o en los datos estructurados suministrados al contexto.

### 3. Arquitectura propuesta y escalabilidad

- **Capa de recepción:** APIs multicanal (chat web, WhatsApp y redes sociales) gestionadas mediante **FastAPI**.

- **Capa de enrutamiento (*Intent Classifier*):** Un clasificador ligero que detecta si la consulta corresponde a categorías como *Estado de Pedido*, *Devolución* u *Otro (Humano)*.

- **Capa de datos (RAG):** Conexión segura mediante microservicios con la base de datos transaccional de EcoMarket, utilizando **PostgreSQL** para el catálogo de productos y la información de envíos.

- **Costo y escalabilidad:** Al utilizar un modelo *open-source*, el costo marginal por consulta puede reducirse frente a APIs comerciales de pago, permitiendo escalar horizontalmente mediante la incorporación de más instancias de GPU según la demanda estacional.

---

## Fase 2: Evaluación de Fortalezas, Limitaciones y Riesgos Éticos

### Fortalezas

- **Reducción drástica del tiempo de respuesta:** El tiempo de atención podría reducirse de un promedio de 24 horas a menos de 5 segundos en las consultas automatizadas, sujeto al rendimiento de la infraestructura y la integración con los sistemas de información.

- **Disponibilidad 24/7:** Cobertura continua para los usuarios, independientemente de la zona horaria o del día de la semana.

- **Eficiencia operativa:** Puede absorber de manera autónoma una parte significativa de la carga repetitiva, permitiendo que el equipo humano se concentre principalmente en casos complejos y de mayor valor.

### Limitaciones

- **Empatía artificial:** Aunque los modelos pueden generar respuestas que aparentan comprensión y empatía, no poseen inteligencia emocional real. Ante clientes extremadamente frustrados por pérdidas de paquetes, una respuesta automatizada e inadecuada podría empeorar la experiencia.

- **Dependencia del dato estructurado:** Si la base de datos de envíos presenta retrasos en su actualización o errores de registro, el sistema podría transmitir información incorrecta con un alto nivel de confianza.

### Riesgos éticos

- **Alucinaciones:** Existe el riesgo de que el modelo genere información incorrecta, como políticas de devolución inexistentes o números de guía que no corresponden a un pedido. Para reducir este riesgo se deben imponer restricciones estrictas al sistema y validar la información contra las fuentes oficiales.

- **Sesgo algorítmico:** Pueden presentarse sesgos en la interpretación del lenguaje natural de clientes con dialectos regionales, expresiones locales o diferentes formas de comunicación, lo que podría afectar la calidad de la atención.

- **Privacidad de datos:** El manejo de PII (*Personally Identifiable Information*), como direcciones, nombres e historiales de compra, requiere medidas de protección adecuadas, incluyendo cifrado en tránsito y en reposo. También debe establecerse una política clara sobre el uso de los datos y evitar que la información de los clientes sea utilizada para entrenar modelos públicos de terceros sin autorización.

- **Impacto laboral:** El objetivo estratégico de EcoMarket **no es reemplazar al personal de atención al cliente, sino potenciarlo**. La automatización permitiría transformar el rol de los agentes, pasando de atender consultas repetitivas a gestionar casos complejos, resolver conflictos y supervisar la calidad de las respuestas generadas por la IA.