import sys
import json
import subprocess

import yaml
from prefect import flow, task, get_run_logger


@task(retries=2, retry_delay_seconds=10)  # 2 reessais si le pipeline echoue
def rejouer_pipeline():
    r = subprocess.run(
        [sys.executable, '-m', 'dvc', 'repro'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    get_run_logger().info(r.stdout[-1500:])  # fin de la sortie de dvc repro
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-800:])
    return 'pipeline rejoue'


@task
def lire_metriques():
    with open('reports/metrics.json', encoding='utf-8') as f:
        return json.load(f)


@task  # aucun reessai : voir Question 3
def valider(mets):
    with open('params.yaml', encoding='utf-8') as f:
        seuil = yaml.safe_load(f)['validation']['seuil_f1']
    if mets['f1'] < seuil:  # la regle de qualite
        raise ValueError(f"F1 {mets['f1']} < seuil {seuil} : modele refuse")
    get_run_logger().info(f"F1 {mets['f1']} >= seuil {seuil} : modele accepte")
    return True


@task
def notifier(mets):
    get_run_logger().info(
        f"NOTIFICATION equipe : nouveau modele valide,"
        f" F1 = {mets['f1']}"
    )


@flow(name='reentrainement-fraude', log_prints=True)
def reentrainement():
    rejouer_pipeline()
    mets = lire_metriques()
    valider(mets)  # leve une erreur -> la suite ne s'execute pas
    notifier(mets)


if __name__ == '__main__':
    reentrainement()
