"""Análisis estadístico (Unidad 3). Lee dataset.csv y escribe resultados.md y figuras."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

BASE = Path(__file__).parent
df = pd.read_csv(BASE / "dataset.csv")
a = df[df.analizable].copy()
out = ["# Resultados del análisis (generado por analyze.py)\n"]


def tabla(md):
    return md.to_markdown() if hasattr(md, "to_markdown") else str(md)


out.append(f"Generaciones totales: {len(df)}. Analizables (con código): {len(a)}. "
           f"Estados: {df.estado.value_counts().to_dict()}\n")

for var, nombre in [("vulnerable_bandit_mh", "Bandit severidad media/alta (resultado principal)"),
                    ("vulnerable_cualquiera", "Cualquier hallazgo de Bandit o Ruff-S (sensibilidad)")]:
    out.append(f"\n## {nombre}\n")
    g = a.groupby("condicion")[var].agg(["sum", "count", "mean"])
    out.append("Proporción de fragmentos vulnerables por condición:\n\n" + tabla(g.round(3)) + "\n")
    ct = pd.crosstab(a.condicion, a[var])
    if ct.shape == (2, 2):
        chi2, p, _, _ = stats.chi2_contingency(ct, correction=False)
        odds, pf = stats.fisher_exact(ct)
        n = ct.values.sum()
        v = (chi2 / n) ** 0.5
        out.append(f"Chi-cuadrado: χ²={chi2:.2f}, p={p:.4f}; V de Cramér={v:.3f}. Fisher exacto: OR={odds:.2f}, p={pf:.4f}\n")
    out.append("\nPor modelo y condición:\n\n" + tabla(a.pivot_table(index="modelo", columns="condicion", values=var, aggfunc="mean").round(3)) + "\n")
    # Wilcoxon pareado por (tarea, modelo)
    p2 = a.pivot_table(index=["task_id", "modelo"], columns="condicion", values=var, aggfunc="mean").dropna()
    if len(p2) > 5 and (p2["control"] != p2["seguridad"]).any():
        w = stats.wilcoxon(p2["control"], p2["seguridad"], zero_method="wilcox")
        out.append(f"\nWilcoxon pareado por (tarea, modelo), n={len(p2)}: estadístico={w.statistic:.1f}, p={w.pvalue:.4f}\n")
    # Regresión logística con errores agrupados por tarea (GEE)
    try:
        m = smf.gee(f"{var} ~ C(condicion, Treatment('control')) * C(modelo)", groups="task_id", data=a,
                    family=sm.families.Binomial()).fit()
        out.append("\nGEE logístico (agrupado por tarea), coeficientes (log-odds):\n\n```\n" + str(m.summary().tables[1]) + "\n```\n")
    except Exception as e:  # separación perfecta, etc.
        out.append(f"\nGEE no estimable: {e}\n")

# Número de hallazgos
out.append("\n## Número de hallazgos (Bandit + Ruff-S) por fragmento\n")
a["n_total"] = a.n_bandit + a.n_ruff
out.append(tabla(a.groupby(["modelo", "condicion"]).n_total.agg(["mean", "median", "std"]).round(2)) + "\n")
mw = stats.mannwhitneyu(a[a.condicion == "control"].n_total, a[a.condicion == "seguridad"].n_total)
out.append(f"\nMann-Whitney control vs. seguridad: U={mw.statistic:.0f}, p={mw.pvalue:.4f}\n")
grupos = [g.n_total.values for _, g in a.groupby("modelo")]
kw = stats.kruskal(*grupos)
out.append(f"Kruskal-Wallis entre modelos: H={kw.statistic:.2f}, p={kw.pvalue:.4f}\n")

# CWE persistentes
out.append("\n## Reglas de Bandit más frecuentes por condición\n")
filas = []
for _, r in a.iterrows():
    for rule in str(r.reglas_bandit).split(";"):
        if rule and rule != "nan":
            filas.append((r.condicion, rule))
if filas:
    rc = pd.DataFrame(filas, columns=["condicion", "regla"])
    out.append(tabla(pd.crosstab(rc.regla, rc.condicion)) + "\n")

# Otros indicadores de calidad
out.append("\n## Indicadores de calidad de datos\n")
out.append(f"- Respuestas truncadas / sin código / error: {(df.estado != 'ok').sum()}\n")
out.append(f"- Código con sintaxis inválida: {int((a.sintaxis_valida == False).sum())}\n")
out.append(f"- Duplicados exactos: {int(df.duplicado_exacto.sum())}\n")
out.append(f"- Atípicos de longitud: {int(df.atipico_longitud.sum())}\n")
out.append(f"- Respuestas con marcadores nosec/noqa: {int(df.uso_nosec_noqa.sum())}\n")

(BASE / "resultados.md").write_text("\n".join(out), encoding="utf-8")

# Figura
p = a.pivot_table(index="modelo", columns="condicion", values="vulnerable_bandit_mh", aggfunc="mean")
ax = p[["control", "seguridad"]].plot.bar(rot=0, figsize=(6, 4))
ax.set_ylabel("Proporción de fragmentos vulnerables (Bandit medio/alto)")
ax.set_title("Efecto de la instrucción de seguridad por modelo")
plt.tight_layout()
plt.savefig(BASE / "fig_proporcion_vulnerable.png", dpi=150)
print("\n".join(out))
