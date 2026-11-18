"""Compara la revisión manual con Bandit y calcula falsos positivos/negativos y acuerdo entre revisores.

Lee revision_manual/resultado_revision.csv (y resultado_revision_2.csv si existe, para el kappa).
"""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent / "revision_manual"
clave = pd.read_csv(BASE / "clave_analizadores.csv")
r1 = pd.read_csv(BASE / "ciega" / "resultado_revision.csv")
m = clave.merge(r1[["id", "vulnerable_real", "tipo_vulnerabilidad", "hay_vulnerabilidad_no_detectable_por_analizador"]], on="id")
m["real"] = m.vulnerable_real.str.lower().map({"si": 1, "sí": 1, "no": 0})
n_dudoso = int(m.real.isna().sum())
m = m.dropna(subset=["real"])
out = ["# Resultado de la revisión manual (generado por evaluar_revision.py)\n",
       f"Fragmentos revisados: {len(m)} (dudosos excluidos: {n_dudoso})\n"]
for col, nombre in [("vulnerable_bandit_mh", "Bandit medio/alto"), ("vulnerable_cualquiera", "Bandit o Ruff, cualquier hallazgo")]:
    tp = int(((m[col] == 1) & (m.real == 1)).sum()); fp = int(((m[col] == 1) & (m.real == 0)).sum())
    fn = int(((m[col] == 0) & (m.real == 1)).sum()); tn = int(((m[col] == 0) & (m.real == 0)).sum())
    prec = tp / (tp + fp) if tp + fp else float("nan"); rec = tp / (tp + fn) if tp + fn else float("nan")
    out.append(f"\n## {nombre}\nVP={tp}, FP={fp}, FN={fn}, VN={tn}; precisión={prec:.2f}; sensibilidad={rec:.2f}\n")
out.append("\n## Vulnerabilidad real por condición y modelo (muestra estratificada, no extrapolar proporciones)\n")
out.append(m.pivot_table(index="modelo", columns="condicion", values="real", aggfunc="mean").round(2).to_markdown() + "\n")
r2p = BASE / "ciega" / "resultado_revision_2.csv"
if r2p.exists():
    r2 = pd.read_csv(r2p)
    j = r1.merge(r2, on="id", suffixes=("_1", "_2"))
    j = j[j.vulnerable_real_1.str.lower().isin(["si", "sí", "no"]) & j.vulnerable_real_2.str.lower().isin(["si", "sí", "no"])]
    a = j.vulnerable_real_1.str.lower().str.replace("í", "i"); b = j.vulnerable_real_2.str.lower().str.replace("í", "i")
    po = (a == b).mean()
    pe = sum(((a == x).mean() * (b == x).mean()) for x in ["si", "no"])
    kappa = (po - pe) / (1 - pe) if pe < 1 else float("nan")
    out.append(f"\n## Acuerdo entre revisores\nFragmentos con doble revisión: {len(j)}; acuerdo observado={po:.2f}; kappa de Cohen={kappa:.2f}\n")
(BASE / "resultados_revision.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
