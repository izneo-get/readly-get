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
import json
import struct
import io
from io import BytesIO
import img2pdf
import os
from PIL import Image, ImageOps
import shutil
import re
import argparse
import time


def requests_retry_session(
    retries=3,
    backoff_factor=1,
    status_forcelist=(500, 502, 504),
    session=None,
):
    """Permet de gérer les cas simples de problèmes de connexions."""
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


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


class Readly:
    token: str = ""
    user_agent: str = "okhttp/3.12.1"
    output_folder = "DOWNLOADS"
    get_content = True
    get_articles = False
    img_format = "jpeg"
    img_quality = 70
    container_format = "pdf"
    no_clean = False
    pause_sec = 0
    session = requests.Session()

    def __init__(self, token, user_agent="okhttp/3.12.1") -> None:
        self.token = token
        self.user_agent = user_agent

    def decode(self, content, publication_id):
        filesize = len(content)
        unpacked = struct.unpack("c" * filesize, content)
        result = []
        for i, u in enumerate(unpacked):
            char = ord(unpacked[i]) ^ ord(publication_id[i % len(publication_id)])
            result.append(char)

        return bytearray(result)

    def download_publication(self, publication_id, save_as=""):
        download_format = "webp"
        url = f"https://api.readly.com/issue/{publication_id}/content?format={download_format}&r=2400"
        headers = {
            "X-Auth-Token": self.token,
            "User-Agent": self.user_agent,
        }
        params = ()

        r = requests_retry_session(session=self.session).get(
            url,
            # cookies=s.cookies,
            allow_redirects=True,
            headers=headers,
            params=params,
        )
        full_content = json.loads(r.text)

        if not save_as:
            save_as = publication_id
        tmp_output_folder = f"{self.output_folder}/{save_as}"
        os.makedirs(tmp_output_folder, exist_ok=True)
        if self.get_content:
            content = full_content["content"]
            for i, c_url in enumerate(content):
                print(f"Téléchargement de la page {i+1} / {len(content)}", end="\r")
                r = requests_retry_session(session=self.session).get(c_url)
                page = f"000{i}"[-3:]
                current_file = f"{tmp_output_folder}/page_{page}.{self.img_format}"
                im = Image.open(BytesIO(self.decode(r.content, publication_id)))
                im = im.convert("RGB")
                im.save(current_file, self.img_format, quality=self.img_quality)
                time.sleep(pause_sec)
            print()

        if self.get_articles:
            articles = full_content["articles"]
            for i, a in enumerate(articles):
                print(f"Page {i+1} / {len(articles)}", end="\r")
                r = requests_retry_session(session=self.session).get(a["url"])
                with open(f"{tmp_output_folder}/article_{a['key']}.zip", "wb") as f:
                    f.write(decodeImageContents(r.content, publication_id))
            print()

        if self.container_format.upper() == "PDF".upper():
            print("Création du PDF...")
            if self.img_format.upper() == "WEBP".upper():
                print(
                    "[WARNING] Le format \"WEBP\" n'est pas optimisé pour les PDF. Le fichier risque d'être d'une taille très importante."
                )
            pdf_file = self.get_unique_path(self.output_folder, save_as, "pdf")
            with open(pdf_file, "wb") as f:
                imgs = []
                for fname in os.listdir(tmp_output_folder):
                    if not fname.endswith(f".{self.img_format}"):
                        continue
                    path = os.path.join(tmp_output_folder, fname)
                    if os.path.isdir(path):
                        continue
                    imgs.append(path)
                f.write(img2pdf.convert(imgs))
            print(f'"{pdf_file}" créé avec succès !')

        if self.container_format.upper() == "CBZ".upper():
            print("Création du CBZ...")
            zip_file = self.get_unique_path(self.output_folder, save_as, "zip")
            shutil.make_archive(zip_file[:-4], "zip", tmp_output_folder)
            cbz_file = self.get_unique_path(self.output_folder, save_as, "cbz")
            os.rename(zip_file, cbz_file)
            print(f'"{cbz_file}" créé avec succès !')

        if not self.no_clean:
            shutil.rmtree(tmp_output_folder)

    def get_unique_path(self, folder, name, ext):
        filler_txt = ""
        max_attempts = 20
        while os.path.exists(f"{folder}/{name}{filler_txt}.{ext}") and max_attempts > 0:
            filler_txt += "_"
            max_attempts -= 1
        return f"{folder}/{name}{filler_txt}.{ext}"

    def get_infos(self, publication_id):
        url = f"https://d3og6tlt23zks5.cloudfront.net/content/{publication_id}"
        headers = {
            "X-Auth-Token": self.token,
            "User-Agent": self.user_agent,
        }
        params = ()

        r = requests_retry_session(session=self.session).get(
            url,
            allow_redirects=True,
            headers=headers,
        )
        infos = json.loads(r.text)
        infos["date"] = infos["publish_date"][: len("YYYY-MM-DD")]
        return infos


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
        default=None,
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

    # Lecture de l'URL.
    while url.upper() != "Q" and not re.match(
        "https://go.readly.com/(.+)/(.+?)/(.+)", url
    ):
        url = input(
            'URL de la publication au format "https://go.readly.com/{folders}/{magazine_id}/{publication_id}" ("Q" pour quitter) : '
        )
    if url.upper() == "Q":
        sys.exit()

    # Lecture du token.
    if os.path.exists(auth_token):
        auth_token = open(auth_token, "r").readline()
    category, magazine_id, publication_id = re.match(
        "https://go.readly.com/(.+)/(.+?)/(.+)", url
    ).groups()
    readly = Readly(token=auth_token)
    readly.output_folder = output_folder
    readly.img_format = image_format
    readly.img_quality = quality
    readly.container_format = container_format
    readly.pause_sec = pause_sec
    readly.no_clean = no_clean

    infos = readly.get_infos(publication_id)
    output_filename = output_pattern
    for k in infos:
        output_filename = output_filename.replace(f"{k}", str(infos[k]))

    output_filename = clean_name(output_filename)
    readly.download_publication(publication_id, save_as=output_filename)
    exit()
    to_pdf = False
    no_clean = True

    output_format = "cbz"

    print()