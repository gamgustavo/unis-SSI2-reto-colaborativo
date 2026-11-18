# Bitácora de preprocesamiento (generada por preprocess.py)

| Fecha UTC | Paso | Qué se hizo | Registros antes | Registros después | Nota |
|---|---|---|---|---|---|
| 2026-11-18 04:24 | Deduplicar run_id | Se conservó el último registro por run_id | 600 | 600 |  |
| 2026-11-18 04:24 | Extracción de código | Se extrajo el bloque de código mayor de cada respuesta; se clasificó el estado | 600 | 600 | {'ok': 596, 'truncado': 4} |
| 2026-11-18 04:24 | Validación de sintaxis | ast.parse sobre cada fragmento | 600 | 595 | Los fragmentos inválidos se conservan y se marcan; no se excluyen del análisis principal |
| 2026-11-18 04:24 | Duplicados | Código idéntico en misma tarea, modelo y condición (se marca, no se elimina) | 600 | 38 | Con temperatura baja se esperan algunas repeticiones idénticas; es un hallazgo, no un error |
| 2026-11-18 04:24 | Atípicos de longitud | Regla IQR (Q3 + 1.5·IQR) por modelo, sobre líneas de código | 600 | 15 | Se marcan y se conservan; se revisa su influencia en el análisis |
| 2026-11-18 04:24 | Análisis estático | Bandit 2026-11-18 y Ruff reglas S | 600 | 412 | errores de Bandit: 5 |
