# blockchain_python


## Prérequis

- Python 3.11 ou une version ultérieure

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
