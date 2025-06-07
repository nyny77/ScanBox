
import os
import shutil

def move_game_file(source_path, destination_full_path):
    """
    Déplace un fichier de source_path vers destination_full_path.
    destination_full_path inclut le nom du fichier à la destination.
    Crée le dossier de destination si nécessaire.
    """
    if not source_path or not os.path.exists(source_path):
        raise FileNotFoundError(f"Fichier source non trouvé : {source_path}")
    
    destination_folder = os.path.dirname(destination_full_path)
    if not os.path.exists(destination_folder):
        try:
            os.makedirs(destination_folder)
            print(f"Dossier créé : {destination_folder}")
        except OSError as e:
            raise OSError(f"Impossible de créer le dossier de destination {destination_folder}: {e}")

    try:
        shutil.move(source_path, destination_full_path)
        print(f"Fichier déplacé : {source_path} -> {destination_full_path}")
    except Exception as e:
        raise Exception(f"Erreur lors du déplacement de {source_path} vers {destination_full_path}: {e}")

def copy_game_file(source_path, destination_full_path):
    """
    Copie un fichier de source_path vers destination_full_path.
    destination_full_path inclut le nom du fichier à la destination.
    Crée le dossier de destination si nécessaire.
    """
    if not source_path or not os.path.exists(source_path):
        raise FileNotFoundError(f"Fichier source non trouvé : {source_path}")

    destination_folder = os.path.dirname(destination_full_path)
    if not os.path.exists(destination_folder):
        try:
            os.makedirs(destination_folder)
            print(f"Dossier créé : {destination_folder}")
        except OSError as e:
            raise OSError(f"Impossible de créer le dossier de destination {destination_folder}: {e}")
    
    try:
        shutil.copy2(source_path, destination_full_path) # copy2 préserve plus de métadonnées
        print(f"Fichier copié : {source_path} -> {destination_full_path}")
    except Exception as e:
        raise Exception(f"Erreur lors de la copie de {source_path} vers {destination_full_path}: {e}")

def delete_game_file(file_path):
    """
    Supprime le fichier spécifié.
    """
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"Fichier à supprimer non trouvé : {file_path}")
    
    try:
        os.remove(file_path)
        print(f"Fichier supprimé : {file_path}")
    except Exception as e:
        raise Exception(f"Erreur lors de la suppression de {file_path}: {e}")

import xml.etree.ElementTree as ET

def remove_game_from_gamelist(gamelist_path, rom_path_from_xml):
    """
    Remove a <game> entry from the gamelist.xml whose <path> matches rom_path_from_xml.
    Returns True if a game was removed, False otherwise.
    """
    if not os.path.exists(gamelist_path):
        raise FileNotFoundError(f"gamelist.xml not found: {gamelist_path}")
    tree = ET.parse(gamelist_path)
    root = tree.getroot()
    removed = False
    for game_elem in root.findall('game'):
        path_elem = game_elem.find('path')
        if path_elem is not None and path_elem.text == rom_path_from_xml:
            root.remove(game_elem)
            removed = True
    if removed:
        tree.write(gamelist_path, encoding='utf-8', xml_declaration=True)
    return removed

def clean_orphaned_entries_in_gamelist(gamelist_path, system_roms_path):
    """
    Supprime toutes les entrées <game> du gamelist.xml dont le fichier ROM n'existe plus.
    Retourne le nombre d'entrées supprimées.
    """
    if not os.path.exists(gamelist_path):
        raise FileNotFoundError(f"gamelist.xml not found: {gamelist_path}")
    import xml.etree.ElementTree as ET
    tree = ET.parse(gamelist_path)
    root = tree.getroot()
    to_remove = []
    for game_elem in root.findall('game'):
        path_elem = game_elem.find('path')
        if path_elem is None or not path_elem.text:
            to_remove.append(game_elem)
            continue
        rom_relative_path = path_elem.text.lstrip('./')
        full_rom_path = os.path.join(system_roms_path, rom_relative_path)
        if not os.path.exists(full_rom_path):
            to_remove.append(game_elem)
    for elem in to_remove:
        root.remove(elem)
    if to_remove:
        tree.write(gamelist_path, encoding='utf-8', xml_declaration=True)
    return len(to_remove)

# --- Exemple d'utilisation pour tests directs du module ---
if __name__ == '__main__':
    print("Test du module file_operations.py")
    
    # Créer des fichiers et dossiers de test
    test_dir_source = "test_source_files"
    test_dir_dest_move = "test_dest_files_move"
    test_dir_dest_copy = "test_dest_files_copy"

    if not os.path.exists(test_dir_source):
        os.makedirs(test_dir_source)
    
    # Nettoyer les dossiers de destination précédents s'ils existent
    if os.path.exists(test_dir_dest_move):
        shutil.rmtree(test_dir_dest_move)
    if os.path.exists(test_dir_dest_copy):
        shutil.rmtree(test_dir_dest_copy)
    
    # Créer des fichiers factices
    file1_path = os.path.join(test_dir_source, "game1.rom")
    file2_path = os.path.join(test_dir_source, "game2.rom")
    file3_path = os.path.join(test_dir_source, "game3_to_delete.rom")

    with open(file1_path, "w") as f: f.write("dummy content game1")
    with open(file2_path, "w") as f: f.write("dummy content game2")
    with open(file3_path, "w") as f: f.write("dummy content game3")

    print(f"\nFichiers de test créés dans : {os.path.abspath(test_dir_source)}")

    # Test de copie
    print("\n--- Test de copie ---")
    dest_file1_copy = os.path.join(test_dir_dest_copy, "game1_copied.rom")
    try:
        copy_game_file(file1_path, dest_file1_copy)
        if os.path.exists(dest_file1_copy) and os.path.exists(file1_path):
            print(f"SUCCÈS: {file1_path} copié vers {dest_file1_copy} et l'original existe toujours.")
        else:
            print(f"ÉCHEC: La copie de {file1_path} a échoué ou l'original a été supprimé.")
    except Exception as e:
        print(f"ERREUR lors du test de copie : {e}")

    # Test de déplacement
    print("\n--- Test de déplacement ---")
    dest_file2_move = os.path.join(test_dir_dest_move, "subfolder", "game2_moved.rom") # Test avec sous-dossier
    try:
        move_game_file(file2_path, dest_file2_move)
        if os.path.exists(dest_file2_move) and not os.path.exists(file2_path):
            print(f"SUCCÈS: {file2_path} déplacé vers {dest_file2_move} et l'original n'existe plus.")
        else:
            print(f"ÉCHEC: Le déplacement de {file2_path} a échoué ou l'original existe toujours.")
    except Exception as e:
        print(f"ERREUR lors du test de déplacement : {e}")

    # Test de suppression
    print("\n--- Test de suppression ---")
    try:
        delete_game_file(file3_path)
        if not os.path.exists(file3_path):
            print(f"SUCCÈS: {file3_path} supprimé.")
        else:
            print(f"ÉCHEC: La suppression de {file3_path} a échoué.")
    except Exception as e:
        print(f"ERREUR lors du test de suppression : {e}")

    # Test de suppression d'un fichier inexistant
    print("\n--- Test de suppression (fichier inexistant) ---")
    try:
        delete_game_file("non_existent_file.rom")
    except FileNotFoundError as e:
        print(f"SUCCÈS (attendu): {e}")
    except Exception as e:
        print(f"ERREUR inattendue: {e}")

    # Nettoyage (optionnel, décommentez pour nettoyer après test)
    # print("\nNettoyage des fichiers et dossiers de test...")
    # if os.path.exists(test_dir_source):
    #     shutil.rmtree(test_dir_source)
    # if os.path.exists(test_dir_dest_move):
    #     shutil.rmtree(test_dir_dest_move)
    # if os.path.exists(test_dir_dest_copy):
    #     shutil.rmtree(test_dir_dest_copy)
    # print("Nettoyage terminé.")