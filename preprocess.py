"""Preprocesamiento + análisis estático. Genera dataset.csv y bitacora_preprocesamiento.md."""
import ast, hashlib, json, re, subprocess, sys, shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
RAW = BASE / "datos_crudos"
CODE = BASE / "codigo_extraido"
BIT = []


def bit(paso, que, antes, despues, nota=""):
    BIT.append((datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"), paso, que, antes, despues, nota))


df = pd.DataFrame([json.loads(l) for l in (BASE / "runs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()])
n0 = len(df)

# 1. Reintentos: si una corrida quedó duplicada se conserva la última
df = df.sort_values("timestamp_utc").drop_duplicates("run_id", keep="last").reset_index(drop=True)
bit("Deduplicar run_id", "Se conservó el último registro por run_id", n0, len(df))

# 2. Extracción de código
BLOQUE = re.compile(r"```(?:python|py)?[ \t]*\r?\n(.*?)```", re.S | re.I)
ABIERTO = re.compile(r"```(?:python|py)?[ \t]*\r?\n(.*)$", re.S | re.I)


def extraer(texto):
    bloques = BLOQUE.findall(texto)
    if bloques:
        return max(bloques, key=len), len(bloques)
    m = ABIERTO.search(texto)  # bloque sin cerrar (respuesta truncada)
    if m:
        return m.group(1), 1
    return None, 0


def normalizar(codigo):
    codigo = codigo.replace("\r\n", "\n").replace("\t", "    ")
    # Los marcadores nosec/noqa desactivan al analizador: se retiran para no ocultar hallazgos
    codigo = re.sub(r"#\s*(nosec|noqa)[^\n]*", "", codigo, flags=re.I)
    return codigo.strip() + "\n"


codigos, nbloques, estados, nosec = [], [], [], []
for _, r in df.iterrows():
    texto = (RAW / f"{r.run_id}.txt").read_text(encoding="utf-8") if r.estado_api == "ok" else ""
    cod, nb = extraer(texto)
    nosec.append(bool(re.search(r"#\s*(nosec|noqa)", texto, re.I)))
    nbloques.append(nb)
    if r.estado_api != "ok":
        estados.append("error_api"); codigos.append(None)
    elif cod is None:
        estados.append("sin_codigo"); codigos.append(None)
    else:
        estados.append("truncado" if r.stop_reason == "max_tokens" else "ok"); codigos.append(normalizar(cod))
df["estado"] = estados
df["n_bloques_codigo"] = nbloques
df["uso_nosec_noqa"] = nosec
bit("Extracción de código", "Se extrajo el bloque de código mayor de cada respuesta; se clasificó el estado",
    len(df), int(sum(c is not None for c in codigos)), df["estado"].value_counts().to_dict().__str__())

# 3. Validación de sintaxis
valido = []
for c in codigos:
    if c is None:
        valido.append(None); continue
    try:
        ast.parse(c); valido.append(True)
    except SyntaxError:
        valido.append(False)
df["sintaxis_valida"] = valido
bit("Validación de sintaxis", "ast.parse sobre cada fragmento", int(sum(c is not None for c in codigos)),
    int(sum(v is True for v in valido)), "Los fragmentos inválidos se conservan y se marcan; no se excluyen del análisis principal")

# 4. Guardar código normalizado y hash
if CODE.exists():
    shutil.rmtree(CODE)
CODE.mkdir()
df["archivo_codigo"] = None
df["hash_codigo"] = None
for i, c in enumerate(codigos):
    if c is None:
        continue
    f = CODE / f"{df.run_id[i]}.py"
    f.write_text(c, encoding="utf-8", newline="\n")
    df.loc[i, "archivo_codigo"] = f.name
    df.loc[i, "hash_codigo"] = hashlib.sha256(c.encode("utf-8")).hexdigest()
df["lineas_codigo"] = [len(c.splitlines()) if c else None for c in codigos]

# 5. Duplicados exactos de código dentro de la misma tarea y condición
dup = df[df.hash_codigo.notna()].duplicated(["task_id", "condicion", "modelo", "hash_codigo"], keep="first")
df["duplicado_exacto"] = False
df.loc[dup[dup].index, "duplicado_exacto"] = True
bit("Duplicados", "Código idéntico en misma tarea, modelo y condición (se marca, no se elimina)", len(df), int(df.duplicado_exacto.sum()),
    "Con temperatura baja se esperan algunas repeticiones idénticas; es un hallazgo, no un error")

# 6. Atípicos en longitud (regla del rango intercuartil por modelo)
df["atipico_longitud"] = False
for m, g in df[df.lineas_codigo.notna()].groupby("modelo"):
    q1, q3 = g.lineas_codigo.quantile([0.25, 0.75])
    lim = q3 + 1.5 * (q3 - q1)
    df.loc[g.index[g.lineas_codigo > lim], "atipico_longitud"] = True
bit("Atípicos de longitud", "Regla IQR (Q3 + 1.5·IQR) por modelo, sobre líneas de código", int(df.lineas_codigo.notna().sum()),
    int(df.atipico_longitud.sum()), "Se marcan y se conservan; se revisa su influencia en el análisis")

# 7. Análisis estático: Bandit y Ruff (reglas S, equivalentes a flake8-bandit)
def correr(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


b = correr([sys.executable, "-m", "bandit", "-r", str(CODE), "-f", "json", "-q"])
bandit = json.loads(b.stdout) if b.stdout.strip() else {"results": [], "errors": []}
rf = correr(["ruff", "check", str(CODE), "--select", "S", "--output-format", "json", "--no-cache", "--isolated"])
ruff = json.loads(rf.stdout) if rf.stdout.strip() else []
(BASE / "bandit_salida.json").write_text(json.dumps(bandit, indent=1), encoding="utf-8")
(BASE / "ruff_salida.json").write_text(json.dumps(ruff, indent=1), encoding="utf-8")

df["n_bandit"] = 0
df["n_bandit_medio_alto"] = 0
df["cwe_bandit"] = ""
df["reglas_bandit"] = ""
df["n_ruff"] = 0
df["reglas_ruff"] = ""
idx = {Path(f).name: i for i, f in enumerate(df.archivo_codigo) if f}
idx = {df.archivo_codigo[i]: i for i in range(len(df)) if df.archivo_codigo[i]}
from collections import defaultdict
bcwe, brul = defaultdict(set), defaultdict(set)
for h in bandit["results"]:
    i = idx[Path(h["filename"]).name]
    df.loc[i, "n_bandit"] += 1
    if h["issue_severity"] in ("MEDIUM", "HIGH"):
        df.loc[i, "n_bandit_medio_alto"] += 1
    bcwe[i].add(f"CWE-{h['issue_cwe']['id']}")
    brul[i].add(h["test_id"])
for i in bcwe:
    df.loc[i, "cwe_bandit"] = ";".join(sorted(bcwe[i]))
    df.loc[i, "reglas_bandit"] = ";".join(sorted(brul[i]))
rr = defaultdict(set)
for h in ruff:
    if not h.get("code"):  # errores de sintaxis no son hallazgos de seguridad
        continue
    i = idx[Path(h["filename"]).name]
    df.loc[i, "n_ruff"] += 1
    rr[i].add(h["code"])
for i in rr:
    df.loc[i, "reglas_ruff"] = ";".join(sorted(rr[i]))

# Variables de resultado
df["analizable"] = df.archivo_codigo.notna()
df["vulnerable_bandit_mh"] = ((df.n_bandit_medio_alto > 0) & df.analizable).astype(int)
df["vulnerable_cualquiera"] = (((df.n_bandit > 0) | (df.n_ruff > 0)) & df.analizable).astype(int)
bit("Análisis estático", f"Bandit {bandit.get('generated_at','')[:10]} y Ruff reglas S", int(df.analizable.sum()),
    int(df.vulnerable_cualquiera.sum()), f"errores de Bandit: {len(bandit.get('errors', []))}")

df.to_csv(BASE / "dataset.csv", index=False, encoding="utf-8-sig")

tabla = "| Fecha UTC | Paso | Qué se hizo | Registros antes | Registros después | Nota |\n|---|---|---|---|---|---|\n"
tabla += "\n".join(f"| {a} | {b_} | {c} | {d} | {e} | {f} |" for a, b_, c, d, e, f in BIT)
(BASE / "bitacora_preprocesamiento.md").write_text("# Bitácora de preprocesamiento (generada por preprocess.py)\n\n" + tabla + "\n", encoding="utf-8")
print(tabla)
