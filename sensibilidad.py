"""Análisis de sensibilidad: efecto al excluir reglas de Bandit que dominan el resultado."""
import collections, json
from pathlib import Path
import pandas as pd
from scipy import stats

BASE = Path(__file__).parent
d = pd.read_csv(BASE / "dataset.csv")
b = json.loads((BASE / "bandit_salida.json").read_text(encoding="utf-8"))
hall = collections.defaultdict(list)
for h in b["results"]:
    hall[h["filename"].replace("\\", "/").split("/")[-1]].append(h)
out = ["# Sensibilidad (generado por sensibilidad.py)\n", "| Reglas excluidas | Control | Seguridad | χ² | p |", "|---|---|---|---|---|"]
for excl in [set(), {"B201"}, {"B201", "B104"}]:
    d["v"] = [int(any(h["issue_severity"] in ("MEDIUM", "HIGH") and h["test_id"] not in excl for h in hall.get(f, []))) for f in d.archivo_codigo]
    g = d.groupby("condicion").v.mean()
    chi, p, _, _ = stats.chi2_contingency(pd.crosstab(d.condicion, d.v), correction=False)
    out.append(f"| {', '.join(sorted(excl)) or 'ninguna'} | {g['control']:.3f} | {g['seguridad']:.3f} | {chi:.2f} | {p:.4f} |")
(BASE / "sensibilidad.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
