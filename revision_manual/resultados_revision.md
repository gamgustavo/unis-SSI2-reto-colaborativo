# Resultado de la revisión manual (generado por evaluar_revision.py)

Fragmentos revisados: 60 (dudosos excluidos: 0)


## Bandit medio/alto
VP=21, FP=9, FN=8, VN=22; precisión=0.70; sensibilidad=0.72


## Bandit o Ruff, cualquier hallazgo
VP=26, FP=18, FN=3, VN=13; precisión=0.59; sensibilidad=0.90


## Vulnerabilidad real por condición y modelo (muestra estratificada, no extrapolar proporciones)

| modelo     |   control |   seguridad |
|:-----------|----------:|------------:|
| deepseek32 |       0.6 |         0.1 |
| mistral3   |       0.5 |         0.4 |
| novapro    |       0.7 |         0.6 |
