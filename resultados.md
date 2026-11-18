# Resultados del análisis (generado por analyze.py)

Generaciones totales: 600. Analizables (con código): 600. Estados: {'ok': 596, 'truncado': 4}


## Bandit severidad media/alta (resultado principal)

Proporción de fragmentos vulnerables por condición:

| condicion   |   sum |   count |   mean |
|:------------|------:|--------:|-------:|
| control     |   160 |     300 |  0.533 |
| seguridad   |    98 |     300 |  0.327 |

Chi-cuadrado: χ²=26.14, p=0.0000; V de Cramér=0.209. Fisher exacto: OR=0.42, p=0.0000


Por modelo y condición:

| modelo     |   control |   seguridad |
|:-----------|----------:|------------:|
| deepseek32 |      0.48 |        0.3  |
| mistral3   |      0.53 |        0.23 |
| novapro    |      0.59 |        0.45 |


Wilcoxon pareado por (tarea, modelo), n=60: estadístico=38.0, p=0.0007


GEE logístico (agrupado por tarea), coeficientes (log-odds):

```
=========================================================================================================================================
                                                                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------------------------------------------------------
Intercept                                                                -0.0800      0.422     -0.190      0.849      -0.907       0.747
C(condicion, Treatment('control'))[T.seguridad]                          -0.7673      0.354     -2.169      0.030      -1.461      -0.074
C(modelo)[T.mistral3]                                                     0.2002      0.315      0.635      0.525      -0.418       0.818
C(modelo)[T.novapro]                                                      0.4440      0.255      1.741      0.082      -0.056       0.944
C(condicion, Treatment('control'))[T.seguridad]:C(modelo)[T.mistral3]    -0.5612      0.503     -1.116      0.264      -1.547       0.424
C(condicion, Treatment('control'))[T.seguridad]:C(modelo)[T.novapro]      0.2026      0.450      0.451      0.652      -0.679       1.084
=========================================================================================================================================
```


## Cualquier hallazgo de Bandit o Ruff-S (sensibilidad)

Proporción de fragmentos vulnerables por condición:

| condicion   |   sum |   count |   mean |
|:------------|------:|--------:|-------:|
| control     |   229 |     300 |  0.763 |
| seguridad   |   183 |     300 |  0.61  |

Chi-cuadrado: χ²=16.39, p=0.0001; V de Cramér=0.165. Fisher exacto: OR=0.48, p=0.0001


Por modelo y condición:

| modelo     |   control |   seguridad |
|:-----------|----------:|------------:|
| deepseek32 |      0.71 |        0.59 |
| mistral3   |      0.75 |        0.55 |
| novapro    |      0.83 |        0.69 |


Wilcoxon pareado por (tarea, modelo), n=60: estadístico=125.0, p=0.0154


GEE logístico (agrupado por tarea), coeficientes (log-odds):

```
=========================================================================================================================================
                                                                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------------------------------------------------------
Intercept                                                                 0.8954      0.458      1.955      0.051      -0.002       1.793
C(condicion, Treatment('control'))[T.seguridad]                          -0.5314      0.431     -1.232      0.218      -1.377       0.314
C(modelo)[T.mistral3]                                                     0.2032      0.307      0.661      0.508      -0.399       0.805
C(modelo)[T.novapro]                                                      0.6902      0.369      1.871      0.061      -0.033       1.413
C(condicion, Treatment('control'))[T.seguridad]:C(modelo)[T.mistral3]    -0.3665      0.516     -0.711      0.477      -1.377       0.644
C(condicion, Treatment('control'))[T.seguridad]:C(modelo)[T.novapro]     -0.2541      0.580     -0.438      0.661      -1.391       0.883
=========================================================================================================================================
```


## Número de hallazgos (Bandit + Ruff-S) por fragmento

|                             |   mean |   median |   std |
|:----------------------------|-------:|---------:|------:|
| ('deepseek32', 'control')   |   2.11 |        2 |  2.09 |
| ('deepseek32', 'seguridad') |   1.59 |        2 |  1.75 |
| ('mistral3', 'control')     |   1.54 |        2 |  1    |
| ('mistral3', 'seguridad')   |   1.67 |        1 |  2.72 |
| ('novapro', 'control')      |   2.32 |        2 |  1.8  |
| ('novapro', 'seguridad')    |   1.89 |        2 |  1.61 |


Mann-Whitney control vs. seguridad: U=51016, p=0.0025

Kruskal-Wallis entre modelos: H=15.20, p=0.0005


## Reglas de Bandit más frecuentes por condición

| regla   |   control |   seguridad |
|:--------|----------:|------------:|
| B101    |         0 |           1 |
| B103    |         0 |           1 |
| B104    |         6 |          51 |
| B105    |        59 |          51 |
| B106    |        13 |          20 |
| B107    |         0 |          10 |
| B108    |         0 |           1 |
| B110    |         3 |          14 |
| B113    |        16 |           4 |
| B201    |       107 |          26 |
| B301    |         9 |           4 |
| B307    |        13 |           6 |
| B314    |        15 |           5 |
| B403    |        13 |           9 |
| B404    |        10 |          15 |
| B405    |        15 |          10 |
| B602    |         0 |           2 |
| B603    |        10 |          13 |
| B605    |         5 |           0 |
| B607    |         5 |           2 |
| B608    |         0 |           1 |
| B704    |         0 |           4 |


## Indicadores de calidad de datos

- Respuestas truncadas / sin código / error: 4

- Código con sintaxis inválida: 5

- Duplicados exactos: 38

- Atípicos de longitud: 15

- Respuestas con marcadores nosec/noqa: 0
