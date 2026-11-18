# Vulnerabilidades en código Python generado por modelos de lenguaje de proveedores alternativos en Amazon Bedrock (DeepSeek, Amazon y Mistral AI): efecto de la instrucción de seguridad en el prompt

Experimento de Seminario de Investigación 2 (Maestría en Ciberseguridad, UNIS).

**Alcance:** tres modelos de lenguaje de propósito general de tres proveedores, accedidos por la API Converse de Amazon Bedrock (us-east-2, noviembre de 2026): DeepSeek V3.2, Amazon Nova Pro y Mistral Large 3. Se llaman "alternativos" porque no se incluyeron los modelos de frontera de mayor capacidad de otros proveedores (por ejemplo, las familias de Anthropic y OpenAI). Los resultados no se extrapolan a otros modelos, lenguajes ni versiones. Diseño factorial 2 (condición: control / seguridad) × 3 (modelo) × 20 tareas × 5 repeticiones = 600 generaciones.

## Estructura
| Archivo | Función |
|---|---|
| `config.py` | Parámetros fijos, 20 tareas con su CWE esperada, plantillas de prompt |
| `run_experiment.py` | Recolección automatizada vía Amazon Bedrock (API Converse). Reanudable, con reintentos y registro |
| `preprocess.py` | Extracción de código, validación, duplicados, atípicos, Bandit y Ruff; genera `dataset.csv` y la bitácora |
| `analyze.py` | Pruebas estadísticas y figura; genera `resultados.md` |
| `datos_crudos/` | Respuesta cruda de cada ejecución (`<run_id>.txt`) |
| `runs.jsonl` | Metadatos por ejecución: hora UTC, modelo, parámetros, tokens, latencia, hash SHA-256 |
| `recoleccion.log` | Registro de la recolección |
| `piloto_1_descartado/` | Evidencia del primer piloto (descartado: un modelo sin acceso y límite de tokens bajo) |

## Reproducir
```bash
python -m venv .venv && source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
aws configure --profile <perfil>        # credenciales con permiso bedrock:InvokeModel
# editar PROFILE y REGION en config.py
python run_experiment.py --limit 10      # piloto
python run_experiment.py                 # corrida completa (reanuda si se interrumpe)
python preprocess.py
python analyze.py
```

## Parámetros fijos
Región `us-east-2`, temperatura 0.2, `max_tokens` 3000, semilla de ordenamiento 42, prompt de sistema único, Python como único lenguaje. Los modelos son `deepseek.v3.2`, `us.amazon.nova-pro-v1:0` y `mistral.mistral-large-3-675b-instruct`. La API no fija una semilla de muestreo, por lo que hay variación entre corridas; por eso hay 5 repeticiones por celda.

## Seguridad y ética
El código generado **nunca se ejecuta**: solo se analiza de forma estática. No hay datos personales. No subir credenciales al repositorio.

## Limitaciones conocidas
- Bandit y Ruff-S son analizadores estáticos con falsos positivos y negativos; no detectan bien XSS, SSRF ni path traversal. Se recomienda revisión manual de una muestra.
- Solo Python, 20 tareas, 3 modelos y una versión de cada uno en una fecha concreta.
- Los modelos pueden cambiar de versión sin aviso; se registran identificador y fecha.
- No se evaluaron modelos de frontera: los de Anthropic requerían un formulario de uso no completado en la cuenta, por lo que la exclusión responde en parte a una restricción de acceso.
