# Orchestrateur ou intégration continue ? (TP06)

**Abdelbaki Zakaria — 5IASDR-G6 — 5 novembre 2026**

| Critère | Prefect (orchestrateur) | GitHub Actions (CI) |
|---|---|---|
| Ce qui déclenche l'exécution | Planification cron chaque lundi ; Quick run ; appel d'un déploiement par API ou événement. | Chaque push ; déclenchement manuel workflow_dispatch. |
| Où s'exécute le traitement | Sur le poste local : processus serve ou sous-processus lancé par le worker du pool process. | Sur une machine Linux éphémère ubuntu-latest hébergée par GitHub. |
| Qui surveille, et où | Le serveur Prefect enregistre états, durées et journaux ; consultation dans Runs, Deployments et Work Pools. | Le runner signale les résultats à GitHub ; consultation dans Actions et sur le commit. |
| Ce qui se passe en cas d'échec | Deux réessais de rejouer_pipeline à 10 s ; valider échoue sans réessai ; le flow est Failed et notifier n'est pas exécutée. Sans exécuteur, le run reste Scheduled puis Late. | L'étape sort avec un code non nul, le job devient rouge ; l'étape d'archivage avec always() conserve les rapports disponibles. Un revert correctif produit un nouveau run. |
| Type de tâche adapté | Traitements récurrents, réentraînement et suivi opérationnel des pipelines. | Vérification d'une modification du code ou des paramètres dans un environnement neuf avant son utilisation. |
| Ce qui est versionné dans Git | flow_mlops.py, planifier.py, prefect.yaml, scripts DVC et paramètres ; les états d'exécution restent dans Prefect. | .github/workflows/ci.yml, requirements-ci.txt, verifier_qualite.py, scripts et paramètres ; les états et artefacts restent dans GitHub Actions. |

## Conclusion (5 lignes)

L'intégration continue contrôle chaque modification du projet dans un environnement neuf.  
Prefect planifie, exécute et rend observables les traitements récurrents.  
La même règle F1 ≥ 0,82 bloque le modèle dégradé dans les deux systèmes.  
Le serveur conserve l'état, tandis que serve ou le worker réalise le calcul.  
CI et orchestration sont complémentaires : l'une valide le code, l'autre exploite le pipeline.
