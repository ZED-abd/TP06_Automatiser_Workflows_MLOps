import json
import subprocess
import yaml
import pandas as pd
import mlflow

mlflow.set_tracking_uri('http://127.0.0.1:5000')
mlflow.set_experiment('tp3-dvc')

P = yaml.safe_load(open('params.yaml', encoding='utf-8'))
ticket = yaml.safe_load(open('data/transactions.csv.dvc', encoding='utf-8'))['outs'][0]
mets = json.load(open('reports/metrics.json'))
commit = subprocess.getoutput('git rev-parse --short HEAD')
n = len(pd.read_csv('data/transactions.csv'))

with mlflow.start_run(run_name=f"donnees-{ticket['md5'][:8]}"):
    mlflow.log_params(P['entrainement'])
    mlflow.log_metrics(mets)
    mlflow.set_tags({'commit': commit,             # quel code
                     'donnees_md5': ticket['md5'], # quelles donnees, exactement
                     'donnees_lignes': n})
    mlflow.log_artifact('dvc.lock')                # la photo complete du pipeline

print('run MLflow cree : donnees', ticket['md5'][:8], '-', n, 'lignes')
