import csv
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

def ensure_export_dir(directory_path):
    """Crée le répertoire spécifié s'il n'existe pas. Retourne True si succès, False sinon."""
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Répertoire créé : {directory_path}")
            return True
        except OSError as e:
            print(f"Erreur lors de la création du répertoire {directory_path}: {e}")
            return False
    return True

def export_to_csv(games_data, target_directory, filename_prefix="jeux_sans_image"):
    """Exporte les données des jeux au format CSV dans le répertoire cible spécifié."""
    if not games_data:
        print("Aucune donnée de jeu à exporter en CSV.")
        return None

    if not ensure_export_dir(target_directory):
        print(f"Échec de la création/accès au répertoire d'exportation CSV : {target_directory}")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    filepath = os.path.join(target_directory, filename)

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['system', 'game_name', 'rom_path', 'image_status', 'full_rom_path', 'gamelist_path']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for game in games_data:
                writer.writerow(game)
        print(f"Données exportées avec succès vers {filepath}")
        return filepath
    except IOError as e:
        print(f"Erreur d'IO lors de l'écriture du fichier CSV {filepath}: {e}")
        return None
    except Exception as e:
        print(f"Erreur inattendue lors de l'export CSV vers {filepath}: {e}")
        return None

def export_to_xml(games_data, target_directory, filename_prefix="jeux_sans_image"):
    """Exporte les données des jeux au format XML dans le répertoire cible spécifié."""
    if not games_data:
        print("Aucune donnée de jeu à exporter en XML.")
        return None

    if not ensure_export_dir(target_directory):
        print(f"Échec de la création/accès au répertoire d'exportation XML : {target_directory}")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.xml"
    filepath = os.path.join(target_directory, filename)

    root_element = ET.Element("gameList")
    for game_dict in games_data:
        game_element = ET.SubElement(root_element, "game")
        for key, val in game_dict.items():
            child = ET.SubElement(game_element, key)
            child.text = str(val) if val is not None else ""

    try:
        xml_str = ET.tostring(root_element, encoding='utf-8')
        # Utilisation de minidom pour un affichage plus lisible (indentation)
        parsed_str = minidom.parseString(xml_str)
        pretty_xml_str = parsed_str.toprettyxml(indent="  ", encoding="utf-8")

        with open(filepath, "wb") as f: # wb car toprettyxml avec encoding retourne des bytes
            f.write(pretty_xml_str)
        print(f"Données exportées avec succès vers {filepath}")
        return filepath
    except IOError as e:
        print(f"Erreur d'IO lors de l'écriture du fichier XML {filepath}: {e}")
        return None
    except Exception as e:
        print(f"Erreur inattendue lors de l'export XML vers {filepath}: {e}")
        return None

def export_data_to_files(games_data, export_directory, export_format="all", filename_prefix="recalbox_export"):
    """
    Exporte les données des jeux vers des fichiers CSV et/ou XML dans le répertoire spécifié.
    Retourne un dictionnaire avec les chemins des fichiers créés ou None en cas d'échec.
    """
    if not games_data:
        print("Export annulé : aucune donnée de jeu à exporter.")
        return None # Ou {'csv': None, 'xml': None} pour plus de clarté

    # Vérification initiale du répertoire de destination principal
    if not ensure_export_dir(export_directory):
        print(f"Échec de la création/accès au répertoire d'exportation principal : {export_directory}")
        return {'csv': None, 'xml': None} # Indiquer l'échec pour tous les formats

    results = {'csv': None, 'xml': None}
    filename_prefix_csv = f"{filename_prefix}_csv"
    filename_prefix_xml = f"{filename_prefix}_xml"

    if export_format == "all" or export_format == "csv":
        csv_path = export_to_csv(games_data, export_directory, filename_prefix_csv)
        results['csv'] = csv_path

    if export_format == "all" or export_format == "xml":
        xml_path = export_to_xml(games_data, export_directory, filename_prefix_xml)
        results['xml'] = xml_path
    
    if results['csv'] or results['xml']:
        print(f"Exportation terminée. Fichiers sauvegardés dans : {export_directory}")
        return results
    else:
        print("Aucun fichier n'a été exporté avec succès.")
        return results # Retourne {'csv': None, 'xml': None} si échec des deux

if __name__ == '__main__':
    # Exemple de données de jeu pour test
    sample_games_data = [
        {'system': 'snes', 'game_name': 'Super Mario World', 'rom_path': './smw.zip', 'image_status': 'image présente', 'full_rom_path': '/path/to/roms/snes/smw.zip', 'gamelist_path': '/path/to/roms/snes/gamelist.xml'},
        {'system': 'nes', 'game_name': 'Contra', 'rom_path': './contra.nes', 'image_status': 'image manquante', 'full_rom_path': '/path/to/roms/nes/contra.nes', 'gamelist_path': '/path/to/roms/nes/gamelist.xml'}
    ]
    
    # Définir un répertoire de test pour les exports (sera créé s'il n'existe pas)
    test_export_dir = os.path.join(os.getcwd(), "test_exports_module") 
    print(f"Début du test d'exportation dans : {test_export_dir}")

    # Test d'exportation CSV et XML
    export_results = export_data_to_files(sample_games_data, test_export_dir, export_format="all", filename_prefix="test_recalbox_data")

    if export_results:
        if export_results.get('csv'):
            print(f"Fichier CSV de test créé : {export_results['csv']}")
        else:
            print("Échec de la création du fichier CSV de test.")
        
        if export_results.get('xml'):
            print(f"Fichier XML de test créé : {export_results['xml']}")
        else:
            print("Échec de la création du fichier XML de test.")
    else:
        print("Échec du processus d'exportation de test.")

    # Vous pouvez vérifier manuellement le contenu du dossier 'test_exports_module'
    # et le supprimer ensuite si vous le souhaitez.
    # import shutil
    # if os.path.exists(test_export_dir):
    #     shutil.rmtree(test_export_dir)
    #     print(f"Répertoire de test supprimé : {test_export_dir}")