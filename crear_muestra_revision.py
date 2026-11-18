"""Crea la muestra ciega para la revisión manual (semilla 42).

Genera en revision_manual/ciega/ (entregar solo esta carpeta al revisor):
  codigo/R01.py ...        código sin modelo, condición ni hallazgos (revisión ciega)
  muestra_revision.csv     id, tarea (enunciado) y columnas vacías para que el revisor las llene
  revision_manual/clave_analizadores.csv   (NO mostrar al revisor) id, run_id, modelo, condición y resultado de Bandit/Ruff
"""
import shutil
from pathlib import Path

import pandas as pd

import config as C

BASE = Path(__file__).parent
OUT = BASE / "revision_manual"
if OUT.exists():
    shutil.rmtree(OUT)
CIEGA = OUT / "ciega"  # lo único que ve el revisor
(CIEGA / "codigo").mkdir(parents=True)

d = pd.read_csv(BASE / "dataset.csv")
d = d[d.analizable & (d.estado == "ok") & (d.sintaxis_valida == True)]  # noqa: E712
enun = {t: e for t, _, e in C.TAREAS}

partes = []
for (m, c), g in d.groupby(["modelo", "condicion"]):
    flag = g[g.vulnerable_bandit_mh == 1]
    noflag = g[g.vulnerable_bandit_mh == 0]
    partes.append(flag.sample(min(5, len(flag)), random_state=C.SEED))
    partes.append(noflag.sample(min(5, len(noflag)), random_state=C.SEED))
m = pd.concat(partes).sample(frac=1, random_state=C.SEED).reset_index(drop=True)
m["id"] = [f"R{i:02d}" for i in range(1, len(m) + 1)]
# 20 fragmentos serán revisados por dos revisores (acuerdo entre revisores)
m["doble_revision"] = False
m.loc[m.sample(20, random_state=C.SEED).index, "doble_revision"] = True

for _, r in m.iterrows():
    shutil.copy(BASE / "codigo_extraido" / r.archivo_codigo, CIEGA / "codigo" / f"{r.id}.py")

vacias = {k: "" for k in ["vulnerable_real", "tipo_vulnerabilidad", "hay_vulnerabilidad_no_detectable_por_analizador", "comentario"]}
pd.DataFrame({"id": m.id, "archivo": [f"codigo/{i}.py" for i in m.id], "enunciado_tarea": m.task_id.map(enun),
              "doble_revision": m.doble_revision, **vacias}).to_csv(CIEGA / "muestra_revision.csv", index=False, encoding="utf-8-sig")
m[["id", "run_id", "modelo", "condicion", "task_id", "doble_revision", "n_bandit_medio_alto", "reglas_bandit",
   "n_ruff", "reglas_ruff", "vulnerable_bandit_mh", "vulnerable_cualquiera"]].to_csv(
    OUT / "clave_analizadores.csv", index=False, encoding="utf-8-sig")
print(len(m), "fragmentos;", int(m.doble_revision.sum()), "con doble revisión")
