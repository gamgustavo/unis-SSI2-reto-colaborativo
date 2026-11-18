"""Recolección automatizada: genera código con cada modelo y condición y guarda evidencias.

Uso: python run_experiment.py [--limit N]
Es reanudable: las ejecuciones ya registradas en runs.jsonl se omiten.
"""
import argparse, hashlib, json, random, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.config import Config

import config as C

BASE = Path(__file__).parent
RAW = BASE / "datos_crudos"
RUNS = BASE / "runs.jsonl"
LOG = BASE / "recoleccion.log"
lock = threading.Lock()


def log(msg):
    linea = f"{datetime.now(timezone.utc).isoformat()} {msg}"
    with lock:
        print(linea, flush=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(linea + "\n")


def lista_ejecuciones():
    corridas = []
    for tid, cwe, enun in C.TAREAS:
        for mkey in C.MODELOS:
            for cond in ("control", "seguridad"):
                for rep in range(1, C.REPETICIONES + 1):
                    corridas.append({
                        "run_id": f"{tid}_{mkey}_{cond}_{rep}",
                        "task_id": tid, "cwe_esperada": cwe, "modelo": mkey,
                        "model_id": C.MODELOS[mkey], "condicion": cond, "repeticion": rep,
                        "prompt": C.construir_prompt(enun, cond),
                    })
    random.Random(C.SEED).shuffle(corridas)
    for i, r in enumerate(corridas, 1):
        r["orden"] = i
    return corridas


def llamar(client, r):
    inicio = time.time()
    for intento in range(6):
        try:
            resp = client.converse(
                modelId=r["model_id"],
                system=[{"text": C.SYSTEM_PROMPT}],
                messages=[{"role": "user", "content": [{"text": r["prompt"]}]}],
                inferenceConfig={"maxTokens": C.MAX_TOKENS, "temperature": C.TEMPERATURA},
            )
            texto = "".join(b.get("text", "") for b in resp["output"]["message"]["content"])
            return {
                "estado_api": "ok", "texto": texto,
                "stop_reason": resp.get("stopReason"),
                "tokens_entrada": resp["usage"]["inputTokens"],
                "tokens_salida": resp["usage"]["outputTokens"],
                "latencia_ms": int((time.time() - inicio) * 1000),
            }
        except Exception as e:  # reintento con espera exponencial
            err = f"{type(e).__name__}: {str(e)[:200]}"
            if intento == 5 or "AccessDenied" in err or "Validation" in err:
                return {"estado_api": "error", "texto": "", "error": err,
                        "latencia_ms": int((time.time() - inicio) * 1000)}
            time.sleep(2 ** intento)


def procesar(client, r):
    res = llamar(client, r)
    ts = datetime.now(timezone.utc).isoformat()
    texto = res.pop("texto")
    (RAW / f"{r['run_id']}.txt").write_text(texto, encoding="utf-8")
    reg = {k: v for k, v in r.items() if k != "prompt"}
    reg.update(res)
    reg.update({
        "timestamp_utc": ts, "temperatura": C.TEMPERATURA, "max_tokens": C.MAX_TOKENS,
        "hash_respuesta": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
        "caracteres": len(texto),
    })
    with lock:
        with open(RUNS, "a", encoding="utf-8") as f:
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")
    log(f"{r['orden']:>3} {r['run_id']} {res['estado_api']} {res.get('latencia_ms')}ms")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    hechas = set()
    if RUNS.exists():
        hechas = {json.loads(l)["run_id"] for l in RUNS.read_text(encoding="utf-8").splitlines() if l.strip()}
    pend = [r for r in lista_ejecuciones() if r["run_id"] not in hechas]
    if a.limit:
        pend = pend[: a.limit]
    log(f"INICIO pendientes={len(pend)} ya_hechas={len(hechas)} seed={C.SEED}")
    session = boto3.Session(profile_name=C.PROFILE, region_name=C.REGION)
    client = session.client("bedrock-runtime", config=Config(retries={"max_attempts": 2}, read_timeout=120))
    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(lambda r: procesar(client, r), pend))
    log("FIN")


if __name__ == "__main__":
    main()
