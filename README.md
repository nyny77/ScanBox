# Recalbox Game Manager

Application pour analyser les fichiers `gamelist.xml` de Recalbox, détecter les jeux sans image et proposer des actions.

## Fonctionnalités

*   Sélection d'un dossier racine Recalbox.
*   Analyse des `gamelist.xml` par système.
*   Détection des jeux sans image (balise `<image>` absente ou vide).
*   Affichage des résultats dans une interface graphique.
*   Filtrage pour afficher uniquement les jeux problématiques.
*   Actions : Déplacer, Copier, Supprimer les jeux sélectionnés.
*   Export des listes de jeux sans image en XML et CSV.

## Structure du Projet

*   `main.py`: Interface utilisateur principale (Tkinter) et logique d'application.
*   `game_parser.py`: Fonctions pour analyser les fichiers `gamelist.xml`.
*   `file_operations.py`: Fonctions pour gérer les actions sur les fichiers.
*   `exporter.py`: Fonctions pour exporter les listes de jeux.
*   `export/`: Dossier pour les fichiers exportés (créé par l'application).
*   `requirements.txt`: Dépendances Python.

## Installation et Lancement

1.  Assurez-vous d'avoir Python installé (version 3.x recommandée).
2.  Aucune bibliothèque externe n'est requise pour l'exécution de base, car les modules `tkinter`, `os`, `xml.etree.ElementTree`, `csv`, `shutil` sont inclus dans la bibliothèque standard de Python.
3.  Lancez l'application :
    ```bash
    python main.py
    ```

## Compilation en .exe (avec PyInstaller)

1.  Installez PyInstaller :
    ```bash
    pip install pyinstaller
    ```
2.  Depuis le dossier du projet (`C:\Users\atoda\CascadeProjects\RecalboxGameManager\`), exécutez dans votre terminal :
    ```bash
    pyinstaller --name RecalboxGameManager --onefile --windowed main.py
    ```
    *   `--onefile` : Crée un seul fichier exécutable.
    *   `--windowed` : Empêche l'ouverture d'une console en arrière-plan pour l'application GUI.
    *   `--name RecalboxGameManager` : Définit le nom de l'exécutable.

    L'exécutable se trouvera dans le dossier `dist/` créé par PyInstaller.

    Pour plus de contrôle (par exemple, pour inclure une icône ou d'autres fichiers), vous pouvez d'abord générer un fichier `.spec` :
    ```bash
    pyinstaller --name RecalboxGameManager --windowed main.py
    ```
    Modifiez ensuite le fichier `RecalboxGameManager.spec` généré, puis compilez avec :
    ```bash
    pyinstaller RecalboxGameManager.spec
    ```
