from flow_mlops import reentrainement


if __name__ == '__main__':
    # Laisser ce processus ouvert pour executer les runs planifies.
    # Ce premier deploiement suit l'heure UTC, comme dans l'enonce.
    reentrainement.serve(
        name='hebdomadaire',
        cron='0 6 * * 1',
    )
