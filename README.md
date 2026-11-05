# TP06 — Automatiser les workflows MLOps

**Abdelbaki Zakaria — 5IASDR-G6**

[![pipeline-mlops](https://github.com/ZED-abd/TP06_Automatiser_Workflows_MLOps/actions/workflows/ci.yml/badge.svg)](https://github.com/ZED-abd/TP06_Automatiser_Workflows_MLOps/actions)

Le workflow Prefect rejoue le pipeline DVC du TP3, lit les métriques, applique
`validation.seuil_f1` et journalise une notification uniquement si le modèle est accepté.
Le dépôt conserve l'historique du TP3 et ses tags `v1` et `v2`.

## Résultats vérifiés

| Essai | Résultat |
|---|---|
| Données v2 : 7 000 transactions, dont 936 fraudes | 5 250 lignes train / 1 750 lignes test |
| `max_depth: 12`, seuil 0,82 | F1 **0,8423**, précision 0,8698, rappel 0,8166 |
| `max_depth: 2` | F1 **0,25**, validation refusée, notification non exécutée |
| Restauration de `max_depth: 12` | Workflow `Completed` |
| Quick run avec `serve` | `Completed`, quatre tâches |
| Quick run après arrêt de `serve` | `Late`, sans tâche ; run d'essai ensuite supprimé |
| Quick run via `pool-tp` et `worker-tp6` | `Completed`, quatre tâches |
| GitHub Actions | Vert → rouge sur le F1 → vert après `git revert` |

Le [rapport PDF](reports/Abdelbaki_Zakaria_5IASDR_G6.pdf) contient les réponses aux
six questions et les captures réelles. La [synthèse](reports/tp6_synthese.md), les
[observations vérifiées](reports/observations.json) et les captures sont dans `reports/`.

## Installation — PowerShell

Python 3.10 ou plus ; environnement testé : Python 3.12.4, Prefect 3.9.1, DVC 3.67.1.

```powershell
git clone https://github.com/ZED-abd/TP06_Automatiser_Workflows_MLOps.git tp6-workflows
cd tp6-workflows
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si le stockage DVC est disponible à côté du clone : `dvc pull`.
Sur une autre machine, recréer la v2 sans ce stockage :

```powershell
python donnees.py
python nouvelles_donnees.py
dvc repro
python verifier_qualite.py
```

`donnees.py` recrée la v1 ; `nouvelles_donnees.py` doit ensuite être exécuté
**une seule fois** pour obtenir la v2. Repartir de `donnees.py` avant de recommencer.
Les empreintes CSV peuvent différer entre Windows et Linux à cause des fins de ligne.

## Serveur et workflow — terminaux 1 et 2

Dans chaque nouveau terminal : se placer dans le clone et activer `.venv`.

Terminal 1, à garder ouvert :

```powershell
prefect server start
```

Terminal 2 :

```powershell
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
python flow_mlops.py
```

Ouvrir [l'interface Prefect](http://127.0.0.1:4200). Les quatre tâches sont
`rejouer_pipeline`, `lire_metriques`, `valider` et `notifier`.

## Planification simple avec serve — terminal 3

```powershell
python planifier.py
```

Déploiement `reentrainement-fraude/hebdomadaire`, cron `0 6 * * 1`, **6 h UTC**.
Dans Deployments : ouvrir le déploiement, puis **Run → Quick run**.
Ce processus doit rester actif pour exécuter les runs. Il a été arrêté après
l'essai, et ce déploiement de démonstration a été mis en pause pour éviter des runs en attente.
Relancer `planifier.py` pour le réactiver.

## Work pool et worker

Terminal 2 :

```powershell
$env:TP6_PROJECT_DIR = (Get-Location).Path
$env:PYTHONIOENCODING = 'utf-8'
prefect work-pool create pool-tp --type process
prefect --no-prompt deploy --name hebdomadaire-pool
```

Si le pool existe déjà, omettre sa création. `prefect.yaml` résout
`TP6_PROJECT_DIR` lors du déploiement pour fixer le répertoire local de travail et
l'étape `set_working_directory`. Redéployer après déplacement du clone.

Terminal 3, à garder ouvert :

```powershell
prefect worker start --pool pool-tp --name worker-tp6
```

Déploiement `reentrainement-fraude/hebdomadaire-pool`, chaque lundi à **6 h,
fuseau `Africa/Casablanca`**, avec une exécution simultanée au maximum.
Le serveur et le worker doivent rester actifs, et le poste ne doit pas être en veille.
Un worker local a été démarré pour la validation ; les commandes ci-dessus permettent de le relancer.

## Intégration continue

Chaque `push` et le bouton **Run workflow** exécutent : installation des dépendances
CI, génération v2, `dvc repro`, validation du F1 et archivage des métriques et de la
matrice de confusion, même en cas d'échec.

| Run de démonstration | Commit | État |
|---|---|---|
| [Première validation](https://github.com/ZED-abd/TP06_Automatiser_Workflows_MLOps/actions/runs/42116481369) | `d28e1d4` | Succès |
| [Modèle volontairement dégradé](https://github.com/ZED-abd/TP06_Automatiser_Workflows_MLOps/actions/runs/42116743507) | `09e329d` | Échec de qualité |
| [Après git revert](https://github.com/ZED-abd/TP06_Automatiser_Workflows_MLOps/actions/runs/42117117784) | `9bbc002` | Succès |

`max_depth` est revenu à **12** dans l'état final. L'historique n'a pas été réécrit.
L'action d'archivage a été actualisée vers `actions/upload-artifact@v7` après
l'avertissement Node.js 20 de la v4. Seuls les rapports produits par le run sont archivés.

La notification du TP est un **journal**, sans envoi d'e-mail ou de message.
Une alerte d'échec réelle demanderait une automatisation Prefect et un canal configuré.

## Recréer le PDF

```powershell
python -m pip install reportlab
python scripts/generer_rapport.py
```

Le contenu textuel est aussi disponible dans [le rapport Markdown](reports/rapport_tp6.md).
