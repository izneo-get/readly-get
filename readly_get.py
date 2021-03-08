# -*- coding: utf-8 -*-
__version__ = "01.00"
"""
Source : https://github.com/izneo-get/readly-get

URL list: 
https://api.readly.com/urls

"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import sys
import os
import re
import argparse
import readly



def clean_name(name):
    """Permet de supprimer les caractères interdits dans les chemins.

    Parameters
    ----------
    name : str
        La chaine de caractère d'entrée.

    Returns
    -------
    str
        La chaine purgée des tous les caractères non désirés.
    """
    chars = '\\/:*<>?"|'
    for c in chars:
        name = name.replace(c, "_")
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\.+$", "", name)
    return name

def check_version():
    latest_version_url = 'https://raw.githubusercontent.com/izneo-get/readly-get/master/VERSION'
    res = requests.get(latest_version_url)
    if res.status_code != 200:
        print(f"Version {__version__} (impossible to check official version)")
    else:
        latest_version = res.text.strip()
        if latest_version == __version__:
            print(f"Version {__version__} (official version)")
        else:
            print(f"Version {__version__} (official version is different: {latest_version})")
            print("Please check https://github.com/izneo-get/readly-get/releases/latest")
    print()




if __name__ == "__main__":
    # Parse des arguments passés en ligne de commande.
    parser = argparse.ArgumentParser(
        description="""Script pour sauvegarder une publication Readly."""
    )
    parser.add_argument(
        "url",
        type=str,
        default="",
        nargs="?",
        help="L'URL de la publication à récupérer",
    )
    parser.add_argument(
        "--token",
        type=str,
        default="auth_token",
        help="Token d'authentification ou fichier contenant le token",
    )
    parser.add_argument(
        "--output-folder",
        "-o",
        type=str,
        default="DOWNLOADS",
        help="Répertoire racine de téléchargement",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="title - issue (date)",
        help="Pattern de nommage du fichier (title, issue, date)",
    )
    parser.add_argument(
        "--image-format",
        "-i",
        type=str,
        choices=["jpeg", "webp"],
        default="jpeg",
        help="Format des images à sauvegarder",
    )
    parser.add_argument(
        "--quality",
        "-q",
        type=int,
        default=70,
        help="Qualité de sauvegarde des images (100 = meilleure qualité)",
    )
    parser.add_argument(
        "--container-format",
        "-c",
        type=str,
        choices=["pdf", "cbz"],
        default="pdf",
        help="Format du container de sortie",
    )
    parser.add_argument(
        "--user-agent", type=str, default=None, help="User agent à utiliser"
    )
    parser.add_argument(
        "--pause",
        "-p",
        type=float,
        metavar="SECONDS",
        default=0,
        help="Faire une pause (en secondes) entre chaque page",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        default=False,
        help="Ne supprime pas le répertoire temporaire dans le cas où un PDF a été généré",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        default=False,
        help="Affiche la version",
    )

    args = parser.parse_args()
    url = args.url
    auth_token = args.token
    output_folder = args.output_folder
    output_pattern = args.pattern
    image_format = args.image_format
    quality = args.quality
    container_format = args.container_format
    pause_sec = args.pause
    no_clean = args.no_clean
    version = args.version

    check_version()
    if version:
        sys.exit()

    # Lecture du token.
    if os.path.exists(auth_token):
        auth_token = open(auth_token, "r").readline()
    
    rdly = readly.Readly(auth_token)
    is_token_ok = rdly.is_token_ok()
    while not is_token_ok:
        auth_token = input("Token d'authentification : ")
        if auth_token.upper() == "Q":
            sys.exit()
        if os.path.exists(auth_token):
            auth_token = open(auth_token, "r").readline()
        rdly = readly.Readly(auth_token)
        is_token_ok = rdly.is_token_ok()
        if not is_token_ok:
            print(f"[ERROR] Token invalide (\"{auth_token}\")...")
        else:
            answer = "?"
            while answer.upper() not in ("Y", "N", "O", "Q", ""):
                answer = input("Sauvagerder le token ? [O]ui (défault) / [N]on : ")
            if answer.upper() == "Q":
                sys.exit()
            if answer.upper() in ("Y", "O", ""):
                with open("auth_token.txt", "w") as f:
                    f.write(auth_token)
                print("[INFO] Token enregistré dans \"auth_token\".")
        

    # Lecture de l'URL.
    while url.upper() != "Q" and not re.match(
        "https://go.readly.com/(.+)/(.+?)/(.+)", url
    ):
        url = input(
            'URL de la publication au format "https://go.readly.com/{folders}/{magazine_id}/{publication_id}" ("Q" pour quitter) : '
        )
    if url.upper() == "Q":
        sys.exit()
    category, magazine_id, publication_id = re.match(
        "https://go.readly.com/(.+)/(.+?)/(.+)", url
    ).groups()


    rdly.output_folder = output_folder
    rdly.img_format = image_format
    rdly.img_quality = quality
    rdly.container_format = container_format
    rdly.pause_sec = pause_sec
    rdly.no_clean = no_clean

    infos = rdly.get_infos(publication_id)
    if not infos:
        # On n'a pas d'infos, c'est peut-être un ID de magazine.
        print("[WARNING] Publication_id invalide...")
        print("[INFO] Publications disponibles : ")
        publications = rdly.get_all_publications(publication_id)
        for p in publications:
            print(f"{p['id']}\t{p['title']} - {p['issue']} ({p['date']})")
        publication_id = publications[0]['id']
        print(f"[INFO] On utilise \"{publication_id} : {publications[0]['title']} - {publications[0]['issue']} ({publications[0]['date']})\"")
        infos = rdly.get_infos(publication_id)
    output_filename = output_pattern
    for k in infos:
        output_filename = output_filename.replace(f"{k}", str(infos[k]))

    output_filename = clean_name(output_filename)
    print(f"[INFO] Format d'image : {image_format.upper()}")
    print(f"[INFO] Qualité d'image : {quality}")
    print(f"[INFO] Format du container : {container_format.upper()}")
    rdly.download_publication(publication_id, save_as=output_filename)
