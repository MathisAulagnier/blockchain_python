# blockchain_python

## Installation

1. Clonez le dépôt :

    ```sh
    git clone <URL_DU_DEPOT>
    cd blockchain_python
    ```

2. Créez un environnement virtuel et activez-le :

    ```sh
    python -m venv venv
    source venv/bin/activate
    ```

3. Installez les dépendances (s'il y en a) :

    ```sh
    pip install -r requirements.txt
    ```

## Lancer les tests

Pour lancer les tests de la classe [Block](src/block.py), utilisez la commande suivante depuis la racine du projet :
```sh
python -m unittest test.test_block
```

Pour l'ensemble des tests, utilisez la commande suivante :
```sh
python -m unittest discover test
```

## Exécution

Pour exécuter le script [main.py](src/main.py), utilisez la commande suivante depuis la racine du projet :
```sh
python -m src.main
```

## Contributeurs
Pour ajouter, commit et push vos modifications, utilisez les commandes suivantes :

1. Assurez-vous que tous les tests passent avant de committer vos modifications :

    ```sh
    make test
    ```

2. Si tous les tests passent, vous pouvez ajouter, commit et push vos modifications en une seule commande :

    ```sh
    make commit
    ```

La commande `make commit` va :
- Exécuter les tests pour s'assurer qu'ils passent.
- Ajouter tous les fichiers modifiés.
- Créer un commit avec un message listant les fichiers modifiés.
- Pousser les changements vers le dépôt distant.
