import xml.etree.ElementTree as ET
import os
import logging

logger = logging.getLogger(__name__)

PREFERRED_GAME_EXTENSIONS_IN_SUBFOLDER = ['.gdi', '.chd', '.cdi']

def _find_primary_game_file_in_subfolder(subfolder_abs_path, subfolder_basename):
    """Scans a subfolder for a primary game file based on preferred extensions."""
    logger.debug(f"_find_primary_game_file_in_subfolder: Received path='{subfolder_abs_path}', basename='{subfolder_basename}'")
    if not os.path.isdir(subfolder_abs_path):
        return None

    # 1. Try subfolder_basename + extension
    for ext in PREFERRED_GAME_EXTENSIONS_IN_SUBFOLDER:
        potential_file = os.path.join(subfolder_abs_path, subfolder_basename + ext)
        logger.debug(f"_find_primary_game_file_in_subfolder: Trying direct match: {potential_file}")
        if os.path.isfile(potential_file):
            return potential_file

    # 2. Try any file with the preferred extensions
    for item in os.listdir(subfolder_abs_path):
        item_path = os.path.join(subfolder_abs_path, item)
        if os.path.isfile(item_path):
            for ext in PREFERRED_GAME_EXTENSIONS_IN_SUBFOLDER:
                if item.lower().endswith(ext):
                    logger.debug(f"_find_primary_game_file_in_subfolder: Found by iterating: {item_path}")
                    return item_path
    return None

def find_gamelists_paths(root_folder):
    """
    Trouve tous les fichiers gamelist.xml dans les sous-dossiers directs du dossier racine.
    Retourne un dictionnaire {system_name: gamelist_path}.
    """
    gamelists = {}
    if not os.path.isdir(root_folder):
        print(f"Erreur: Le dossier racine '{root_folder}' n'existe pas ou n'est pas un dossier.")
        return gamelists

    for item in os.listdir(root_folder):
        system_path = os.path.join(root_folder, item)
        if os.path.isdir(system_path):
            gamelist_file = os.path.join(system_path, "gamelist.xml")
            if os.path.isfile(gamelist_file):
                gamelists[item] = gamelist_file # item is the system name
            # else:
                # print(f"Info: Pas de gamelist.xml trouvé pour le système '{item}' dans {system_path}")
    return gamelists

def parse_gamelist(gamelist_path, system_name, system_roms_path, ignore_name_patterns=None, ignore_path_extensions=None):
    """Analyse un fichier ``gamelist.xml`` pour un système donné.

    Args:
        gamelist_path (str): Chemin absolu vers le fichier ``gamelist.xml``.
        system_name (str): Nom du système (ex: ``snes``, ``nes``).
        system_roms_path (str): Chemin absolu vers le dossier des ROMs pour ce système
            (ex: ``C:/Recalbox/roms/snes``). Utilisé comme base pour résoudre les chemins
            relatifs des ROMs et des images.

    Returns:
        list: Une liste de dictionnaires représentant les jeux trouvés.
    """

    added_rom_paths = set()  # Set to track full_rom_paths of already added games
    games = []
    if not os.path.exists(gamelist_path):
        print(f"Erreur: Fichier gamelist.xml non trouvé à {gamelist_path}")
        return games

    try:
        tree = ET.parse(gamelist_path)
        xml_root = tree.getroot()
    except ET.ParseError as e:
        print(f"Erreur de parsing XML dans {gamelist_path}: {e}")
        return games

    for game_element in xml_root.findall('game'):
        game_name_tag = game_element.find('name')
        game_name = game_name_tag.text if game_name_tag is not None and game_name_tag.text else "Nom Manquant"

        rom_path_tag = game_element.find('path')
        rom_path_from_xml = rom_path_tag.text if rom_path_tag is not None and rom_path_tag.text else None

        # Generic filtering based on name patterns and path extensions
        skip_game = False
        if ignore_name_patterns:
            for pattern in ignore_name_patterns:
                if pattern.lower() in game_name.lower():
                    logger.info(f"Skipping game (name filter: '{pattern}'): Name='{game_name}', Path='{rom_path_from_xml}' for system '{system_name}'.")
                    skip_game = True
                    break 
        
        if skip_game:
            continue 

        if ignore_path_extensions and rom_path_from_xml:
            for ext in ignore_path_extensions:
                if rom_path_from_xml.lower().endswith(ext.lower()):
                    logger.info(f"Skipping game (extension filter: '{ext}'): Name='{game_name}', Path='{rom_path_from_xml}' for system '{system_name}'.")
                    skip_game = True
                    break 
        
        if skip_game:
            continue
        
        full_rom_path = "Chemin ROM Manquant"
        if rom_path_from_xml:
            # Les chemins dans gamelist.xml sont relatifs au dossier du système (system_roms_path)
            # ou parfois au gamelist.xml lui-même. system_roms_path est plus sûr.
            # Si rom_path_from_xml commence par './', il est relatif au gamelist.xml.
            # os.path.dirname(gamelist_path) est équivalent à system_roms_path ici.
            if rom_path_from_xml.startswith('./'):
                 full_rom_path = os.path.abspath(os.path.join(system_roms_path, rom_path_from_xml[2:]))
            else: # Peut être un chemin déjà complet ou relatif différemment, on le traite comme relatif à system_roms_path
                 full_rom_path = os.path.abspath(os.path.join(system_roms_path, rom_path_from_xml))
            
            if not os.path.exists(full_rom_path):
                # Tenter une seconde vérification si le chemin était censé être relatif au dossier parent du gamelist
                # Cela arrive si la structure est /roms/system/games/gamelist.xml et roms sont dans /roms/system/games/
                # Mais pour Recalbox, c'est généralement /roms/system/gamelist.xml et roms dans /roms/system/
                pass # Pour l'instant, on s'en tient à system_roms_path comme base.

        image_status = "image manquante"
        full_image_path_found = None # Variable pour stocker le chemin de l'image trouvée
        video_status = "vidéo manquante"
        full_video_path_found = None
        image_tag = game_element.find('image')

        # Extract Rating
        rating_tag = game_element.find('rating')
        game_rating = None
        if rating_tag is not None and rating_tag.text:
            try:
                game_rating = float(rating_tag.text)
            except ValueError:
                logger.warning(f"Invalid rating format for game '{game_name}': {rating_tag.text}. Setting to None.")
                game_rating = None

        # 1. Essayer de lire le chemin de l'image directement depuis la balise <image>
        if image_tag is not None and image_tag.text:
            image_path_from_xml = image_tag.text
            potential_image_path = ""
            if image_path_from_xml.startswith('./'):
                potential_image_path = os.path.abspath(os.path.join(system_roms_path, image_path_from_xml[2:]))
            else:
                potential_image_path = os.path.abspath(os.path.join(system_roms_path, image_path_from_xml))
            
            if os.path.exists(potential_image_path) and os.path.getsize(potential_image_path) > 0:
                image_status = "image présente"
                full_image_path_found = potential_image_path
            elif os.path.exists(potential_image_path):
                image_status = "image présente (vide)"
                full_image_path_found = potential_image_path # Même si vide, le chemin est correct
            else:
                image_status = "image manquante (xml invalide)" # Le chemin du XML ne mène nulle part
        else:
            image_status = "balise image absente"

        # 2. Si aucune image valide n'a été trouvée via la balise XML, tenter une recherche basée sur le nom de la ROM
        #    Ceci est utile si la balise <image> est absente ou pointe vers un fichier non existant.
        if full_image_path_found is None and rom_path_from_xml:
            rom_basename = os.path.splitext(os.path.basename(rom_path_from_xml))[0]
            # Supposer que les images sont dans un sous-dossier 'images' ou 'media/images'
            # Vous devrez peut-être ajuster ces chemins en fonction de la structure de Recalbox
            possible_image_folders = [
                os.path.join(system_roms_path, 'images'),
                os.path.join(system_roms_path, 'media', 'images'),
                os.path.join(system_roms_path, 'media', 'screenshots')
                # Ajoutez d'autres emplacements communs si nécessaire
            ]
            image_extensions = ('.png', '.jpg', '.jpeg', '.gif')

            found_in_search = False
            for img_folder in possible_image_folders:
                if os.path.isdir(img_folder):
                    for filename in os.listdir(img_folder):
                        if filename.startswith(rom_basename) and filename.lower().endswith(image_extensions):
                            potential_match = os.path.join(img_folder, filename)
                            if os.path.exists(potential_match) and os.path.getsize(potential_match) > 0:
                                image_status = "image présente (trouvée)"
                                full_image_path_found = os.path.abspath(potential_match)
                                found_in_search = True
                                break # Prendre la première correspondance
                            elif os.path.exists(potential_match):
                                image_status = "image présente (vide, trouvée)"
                                full_image_path_found = os.path.abspath(potential_match)
                                found_in_search = True
                                break # Prendre la première correspondance (même si vide)
                if found_in_search: break
            
            if not found_in_search and image_status not in ["balise image absente", "image présente (xml invalide)"]:
                 # Si la balise image était présente mais invalide, et que la recherche n'a rien donné
                 # ou si la balise était absente et la recherche n'a rien donné
                image_status = "image manquante (non trouvée)"
        elif full_image_path_found is None and image_status == "balise image absente":
            # Si la balise est absente et rom_path_from_xml est aussi absent, on ne peut pas chercher
            image_status = "image manquante (pas de balise, pas de nom rom)"

        # 3. Recherche de la vidéo basée sur le nom de la ROM
        video_tag = game_element.find('video') # Vérifier d'abord si une balise <video> existe
        if video_tag is not None and video_tag.text:
            video_path_from_xml = video_tag.text
            potential_video_path = ""
            if video_path_from_xml.startswith('./'):
                potential_video_path = os.path.abspath(os.path.join(system_roms_path, video_path_from_xml[2:]))
            else:
                potential_video_path = os.path.abspath(os.path.join(system_roms_path, video_path_from_xml))
            
            if os.path.exists(potential_video_path) and os.path.getsize(potential_video_path) > 0:
                video_status = "vidéo présente"
                full_video_path_found = potential_video_path
            elif os.path.exists(potential_video_path):
                video_status = "vidéo présente (vide)"
                full_video_path_found = potential_video_path
            else:
                video_status = "vidéo manquante (xml invalide)"
        else:
            video_status = "balise vidéo absente"

        if full_video_path_found is None and rom_path_from_xml: # Si la balise XML n'a pas donné de résultat ou était absente
            rom_basename = os.path.splitext(os.path.basename(rom_path_from_xml))[0]
            possible_video_folders = [
                os.path.join(system_roms_path, 'videos'),
                os.path.join(system_roms_path, 'media', 'videos'),
                os.path.join(system_roms_path, 'media', 'video')
            ]
            video_extensions = ('.mp4', '.avi', '.mkv') # Ajoutez d'autres extensions si nécessaire

            found_video_in_search = False
            for vid_folder in possible_video_folders:
                if os.path.isdir(vid_folder):
                    for filename in os.listdir(vid_folder):
                        if filename.startswith(rom_basename) and filename.lower().endswith(video_extensions):
                            potential_match = os.path.join(vid_folder, filename)
                            if os.path.exists(potential_match) and os.path.getsize(potential_match) > 0:
                                video_status = "vidéo présente (trouvée)"
                                full_video_path_found = os.path.abspath(potential_match)
                                found_video_in_search = True
                                break
                            elif os.path.exists(potential_match):
                                video_status = "vidéo présente (vide, trouvée)"
                                full_video_path_found = os.path.abspath(potential_match)
                                found_video_in_search = True
                                break
                if found_video_in_search: break
            
            if not found_video_in_search and video_status not in ["balise vidéo absente", "vidéo manquante (xml invalide)"]:
                video_status = "vidéo manquante (non trouvée)"
        elif full_video_path_found is None and video_status == "balise vidéo absente":
            video_status = "vidéo manquante (pas de balise, pas de nom rom)"

        game_info = {
            'system': system_name,
            'game_name': game_name,
            'rom_path': rom_path_from_xml if rom_path_from_xml else "N/A",
            'image_status': image_status,
            'image_path': full_image_path_found, # Chemin absolu vers l'image trouvée (peut être None)
            'video_status': video_status,
            'video_path': full_video_path_found, # Chemin absolu vers la vidéo trouvée (peut être None)
            'full_rom_path': full_rom_path, # Chemin absolu vers la ROM
            'gamelist_path': gamelist_path, # Chemin vers le gamelist.xml analysé
            'rating': game_rating # Ajout du rating
        }
        if game_info['full_rom_path'] != "Chemin ROM Manquant" and game_info['full_rom_path'] != "Chemin ROM Manquant (Dossier)":
            if game_info['full_rom_path'] in added_rom_paths:
                logger.info(f"Skipping duplicate game (already added): Name='{game_info['game_name']}', Full ROM Path='{game_info['full_rom_path']}'")
                continue
            else:
                added_rom_paths.add(game_info['full_rom_path'])
        games.append(game_info)

    processed_folder_paths = set() # Initialize set to track processed folder paths
    logger.debug(f"Starting to process <folder> elements in {gamelist_path}")
    # Process <folder> elements
    for folder_element in xml_root.findall('folder'):
        game_name_tag = folder_element.find('name')
        game_name = game_name_tag.text if game_name_tag is not None and game_name_tag.text else "Nom Manquant (Dossier)"

        # Filter for <folder> elements based on name, specific to Dreamcast for now
        if system_name == 'dreamcast':
            if "zzz(notgame):" in game_name.lower() or game_name.lower().endswith('.bin'):
                logger.info(f"Skipping folder (Dreamcast filter): Name='{game_name}' as it's marked as not a game or is a .bin file entry.")
                continue
        subfolder_path_from_xml_tag = folder_element.find('path')
        logger.debug(f"Processing <folder>: Name='{game_name}', XML Path='{subfolder_path_from_xml_tag.text if subfolder_path_from_xml_tag is not None and subfolder_path_from_xml_tag.text else 'N/A'}'")
        subfolder_path_from_xml = subfolder_path_from_xml_tag.text if subfolder_path_from_xml_tag is not None and subfolder_path_from_xml_tag.text else None

        actual_rom_file_relative_path = "N/A"
        full_actual_rom_path = "Chemin ROM Manquant (Dossier)"
        
        if subfolder_path_from_xml:
            # Resolve absolute path to the subfolder itself
            if subfolder_path_from_xml.startswith('./'):
                full_subfolder_path = os.path.abspath(os.path.join(system_roms_path, subfolder_path_from_xml[2:]))
            else:
                full_subfolder_path = os.path.abspath(os.path.join(system_roms_path, subfolder_path_from_xml))

            logger.debug(f"  Resolved full_subfolder_path: '{full_subfolder_path}'")
            if full_subfolder_path in processed_folder_paths:
                logger.debug(f"  Skipping already processed folder: '{full_subfolder_path}' for game '{game_name}'")
                continue
            processed_folder_paths.add(full_subfolder_path)
            if os.path.isdir(full_subfolder_path):
                subfolder_basename = os.path.basename(full_subfolder_path) # Or os.path.basename(subfolder_path_from_xml.strip('./'))
                logger.debug(f"  Attempting to find primary game file in subfolder: '{full_subfolder_path}' with basename: '{subfolder_basename}'")
                found_primary_file = _find_primary_game_file_in_subfolder(full_subfolder_path, subfolder_basename)
                if found_primary_file:
                    logger.debug(f"    SUCCESS: Found primary game file: '{found_primary_file}'")
                else:
                    logger.debug(f"    FAILURE: No primary game file found in '{full_subfolder_path}' for basename '{subfolder_basename}'.")
                if found_primary_file:
                    full_actual_rom_path = found_primary_file
                    # Make actual_rom_file_relative_path relative to system_roms_path, like './FolderName/game.gdi'
                    actual_rom_file_relative_path = './' + os.path.relpath(found_primary_file, system_roms_path).replace('\\', '/')
            else:
                # This case means the <path> in <folder> does not point to a valid directory
                # full_actual_rom_path remains "Chemin ROM Manquant (Dossier)"
                pass 

        # Image and Video logic for folders (can be similar to games, using game_name as base for search if tags are missing/invalid)
        image_status = "image manquante"
        full_image_path_found = None
        video_status = "vidéo manquante"
        full_video_path_found = None

        image_tag = folder_element.find('image')
        if image_tag is not None and image_tag.text:
            image_path_from_xml = image_tag.text
            potential_image_path = os.path.abspath(os.path.join(system_roms_path, image_path_from_xml.strip('./')))
            if os.path.exists(potential_image_path) and os.path.getsize(potential_image_path) > 0:
                image_status = "image présente"
                full_image_path_found = potential_image_path
            elif os.path.exists(potential_image_path):
                image_status = "image présente (vide)"
                full_image_path_found = potential_image_path
            else:
                image_status = "image manquante (xml invalide)"
        else:
            image_status = "balise image absente"
        
        # Fallback search for image if not found via XML (using folder name)
        if full_image_path_found is None:
            # Using game_name (folder's display name) as basename for media search
            media_basename = game_name # Or derive from subfolder_path_from_xml if more reliable
            possible_image_folders = [
                os.path.join(system_roms_path, 'images'),
                os.path.join(system_roms_path, 'media', 'images'),
                os.path.join(system_roms_path, 'media', 'screenshots')
            ]
            image_extensions = ('.png', '.jpg', '.jpeg', '.gif')
            found_in_search = False
            for img_folder in possible_image_folders:
                if os.path.isdir(img_folder):
                    for filename in os.listdir(img_folder):
                        if filename.startswith(media_basename) and filename.lower().endswith(image_extensions):
                            potential_match = os.path.join(img_folder, filename)
                            if os.path.exists(potential_match) and os.path.getsize(potential_match) > 0:
                                image_status = "image présente (trouvée)"
                                full_image_path_found = os.path.abspath(potential_match)
                                found_in_search = True; break
                            elif os.path.exists(potential_match):
                                image_status = "image présente (vide, trouvée)"
                                full_image_path_found = os.path.abspath(potential_match)
                                found_in_search = True; break
                if found_in_search: break
            if not found_in_search and image_status not in ["balise image absente", "image manquante (xml invalide)"]:
                image_status = "image manquante (non trouvée)"
            elif full_image_path_found is None and image_status == "balise image absente":
                image_status = "image manquante (pas de balise, pas de nom rom)"

        video_tag = folder_element.find('video')
        if video_tag is not None and video_tag.text:
            video_path_from_xml = video_tag.text
            potential_video_path = os.path.abspath(os.path.join(system_roms_path, video_path_from_xml.strip('./')))
            if os.path.exists(potential_video_path) and os.path.getsize(potential_video_path) > 0:
                video_status = "vidéo présente"
                full_video_path_found = potential_video_path
            elif os.path.exists(potential_video_path):
                video_status = "vidéo présente (vide)"
                full_video_path_found = potential_video_path
            else:
                video_status = "vidéo manquante (xml invalide)"
        else:
            video_status = "balise vidéo absente"

        # Fallback search for video if not found via XML (using folder name)
        if full_video_path_found is None:
            media_basename = game_name
            possible_video_folders = [
                os.path.join(system_roms_path, 'videos'),
                os.path.join(system_roms_path, 'media', 'videos'),
                os.path.join(system_roms_path, 'media', 'video')
            ]
            video_extensions = ('.mp4', '.avi', '.mkv')
            found_video_in_search = False
            for vid_folder in possible_video_folders:
                if os.path.isdir(vid_folder):
                    for filename in os.listdir(vid_folder):
                        if filename.startswith(media_basename) and filename.lower().endswith(video_extensions):
                            potential_match = os.path.join(vid_folder, filename)
                            if os.path.exists(potential_match) and os.path.getsize(potential_match) > 0:
                                video_status = "vidéo présente (trouvée)"
                                full_video_path_found = os.path.abspath(potential_match)
                                found_video_in_search = True; break
                            elif os.path.exists(potential_match):
                                video_status = "vidéo présente (vide, trouvée)"
                                full_video_path_found = os.path.abspath(potential_match)
                                found_video_in_search = True; break
                if found_video_in_search: break
            if not found_video_in_search and video_status not in ["balise vidéo absente", "vidéo manquante (xml invalide)"]:
                video_status = "vidéo manquante (non trouvée)"
            elif full_video_path_found is None and video_status == "balise vidéo absente":
                video_status = "vidéo manquante (pas de balise, pas de nom rom)"

        folder_info = {
            'system': system_name,
            'game_name': game_name,
            'rom_path': actual_rom_file_relative_path, # This now points to the .gdi (or .chd/.cdi) inside the folder
            'image_status': image_status,
            'image_path': full_image_path_found,
            'video_status': video_status,
            'video_path': full_video_path_found,
            'full_rom_path': full_actual_rom_path, # Absolute path to the .gdi (or .chd/.cdi)
            'is_folder': True, # Mark this entry as originating from a <folder> tag
            'original_folder_path_xml': subfolder_path_from_xml, # Store original folder path from XML for reference
            'gamelist_path': gamelist_path
        }
        logger.debug(f"   Appending folder_info for '{game_name}': ROM Path='{actual_rom_file_relative_path}', Full ROM Path='{full_actual_rom_path}'")
        if folder_info['full_rom_path'] != "Chemin ROM Manquant" and folder_info['full_rom_path'] != "Chemin ROM Manquant (Dossier)":
            if folder_info['full_rom_path'] in added_rom_paths:
                logger.info(f"Skipping duplicate game from folder (already added): Name='{folder_info['game_name']}', Full ROM Path='{folder_info['full_rom_path']}'")
                continue # Skip adding this folder_info as it's a duplicate ROM path
            else:
                added_rom_paths.add(folder_info['full_rom_path'])
        games.append(folder_info)

    return games

# --- Exemple d'utilisation pour tests directs du module ---
if __name__ == '__main__':
    print("Test du module game_parser.py")
    # Pour tester parse_gamelist, vous aurez besoin d'un vrai gamelist.xml
    # et d'un chemin vers le dossier des roms du système correspondant.
    
    # Exemple (à adapter avec vos propres fichiers pour un test réel):
    # test_gamelist_path = "C:/path/to/your/recalbox/roms/snes/gamelist.xml"
    # test_system_roms_path = "C:/path/to/your/recalbox/roms/snes"
    # test_system_name = "snes"
    # if os.path.exists(test_gamelist_path) and os.path.isdir(test_system_roms_path):
    #     print(f"\nAnalyse de {test_gamelist_path} pour le système {test_system_name}...")
    #     parsed_games_data = parse_gamelist(test_gamelist_path, test_system_name, test_system_roms_path)
    #     if parsed_games_data:
    #         print(f"{len(parsed_games_data)} jeux trouvés.")
    #         for i, game in enumerate(parsed_games_data[:3]): # Afficher les 3 premiers
    #             print(f"  Jeu {i+1}: {game['game_name']} - ROM: {game['rom_path']} - Image: {game['image_status']}")
    #             print(f"    Full ROM Path: {game['full_rom_path']}")
    #     else:
    #         print("Aucun jeu trouvé ou erreur lors de l'analyse.")
    # else:
    #     print("\nChemin de test pour gamelist.xml ou dossier roms système non valide. Veuillez configurer pour tester.")
    
    # La fonction find_gamelists_paths n'est plus utilisée par main.py mais peut être testée séparément si besoin.
    # print("\nTest de find_gamelists_paths (si vous avez un dossier roms complet pour tester)")
    # test_root_roms_folder = "C:/path/to/your/recalbox/roms" # Adaptez ce chemin
    # if os.path.isdir(test_root_roms_folder):
    #     gamelists = find_gamelists_paths(test_root_roms_folder)
    #     if gamelists:
    #         print(f"Gamelists trouvés pour les systèmes : {list(gamelists.keys())}")
    #     else:
    #         print("Aucun gamelist.xml trouvé.")
    # else:
    #     print("Chemin racine des ROMs pour test de find_gamelists_paths non valide.")
    pass # Le test direct est commenté pour éviter les erreurs si les chemins ne sont pas configurés.