import sys
import json

import yaml


with open('reports/metrics.json', encoding='utf-8') as f:
    f1 = json.load(f)['f1']
with open('params.yaml', encoding='utf-8') as f:
    seuil = yaml.safe_load(f)['validation']['seuil_f1']

print(f'F1 = {f1} | seuil = {seuil}')
if f1 < seuil:
    print('ECHEC : modele refuse')
    sys.exit(1)
print('OK : modele accepte')
