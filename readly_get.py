# -*- coding: utf-8 -*-
__version__ = "01.05"
"""
Source : https://github.com/izneo-get/readly-get

URL list: 
https://api.readly.com/urls

"""

import requests
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
    latest_version_url = "https://raw.githubusercontent.com/izneo-get/readly-get/main/VERSION"
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


def is_valid_url(url):
    return (
        re.match("https://go.readly.com(.*)/(.+?)/(.+)", url)
        or re.match("https://(.+?).readly.com/products/(.+)", url)
        or re.match("([\d\w]{24})", url)
    )


if __name__ == "__main__":
    # Parse des arguments passés en ligne de commande.
    parser = argparse.ArgumentParser(description="""Script to save a Readly publication.""")
    parser.add_argument(
        "url",
        type=str,
        default="",
        nargs="?",
        help="URL of the desired publication or publication_id.",
    )
    parser.add_argument(
        "--token",
        type=str,
        default="auth_token",
        help='Authentication token or file containing the token. Default="auth_token".',
    )
    parser.add_argument(
        "--output-folder",
        "-o",
        type=str,
        default="DOWNLOADS",
        help='Folder to save your publication. Default="DOWNLOADS".',
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="title - issue (date)",
        help='Pattern to name your file (available: "title", "issue", "date"). Default="title - issue (date)".',
    )
    parser.add_argument(
        "--image-format",
        "-i",
        type=str,
        choices=["jpeg", "webp"],
        default="jpeg",
        help='Image format saved (available: "jpeg", "webp"). Default="jpeg".',
    )
    parser.add_argument(
        "--quality",
        "-q",
        type=int,
        default=85,
        help='Image quality (100 = best quality). Default="85".',
    )
    parser.add_argument(
        "--container-format",
        "-c",
        type=str,
        choices=["pdf", "cbz"],
        default="pdf",
        help='Output file type (available: "cbz", "pdf"). Default="pdf".',
    )
    parser.add_argument(
        "--low-quality",
        action="store_true",
        default=False,
        help="Get default low quality images instead of HQ images.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help='Image DPI (0 = original DPI). Default="300".',
    )
    parser.add_argument("--user-agent", type=str, default=None, help="User-agent to use.")
    parser.add_argument(
        "--pause",
        "-p",
        type=float,
        metavar="SECONDS",
        default=0,
        help='Make a pause (in seconds) between two pages. Default="0"',
    )
    parser.add_argument(
        "--max-dl",
        type=int,
        default=1,
        help='Max number of issues to download. Default="1".',
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        default=False,
        help="Don't delete the temp folder where the images are stored.",
    )
    parser.add_argument(
        "--get-articles",
        action="store_true",
        default=False,
        help='Also download attached articles. Use with "--no-clean" option, or files will be deleted.',
    )
    parser.add_argument(
        "--get-articles-only",
        action="store_true",
        default=False,
        help='Download only attached articles (no image). Won\'t create PDF / CBZ file. Will force "--no-clean" option.',
    )
    parser.add_argument(
        "--create-token",
        action="store_true",
        default=False,
        help="Create a new token.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        default=False,
        help="Current version.",
    )

    args = parser.parse_args()
    url = args.url
    auth_token = args.token
    output_folder = args.output_folder
    output_pattern = args.pattern
    image_format = args.image_format
    quality = args.quality
    container_format = args.container_format
    use_default = args.low_quality
    dpi = args.dpi
    pause_sec = args.pause
    no_clean = args.no_clean
    version = args.version
    create_token = args.create_token
    max_dl = args.max_dl
    get_articles = args.get_articles
    get_articles_only = args.get_articles_only

    if create_token:
        new_token = readly.Readly.create_token()
        if new_token:
            print(f"{new_token}")
            answer = "?"
            while answer.upper() not in ("Y", "N", "O", "Q", ""):
                answer = input("Save token? [Y]es (default) / [N]o: ")
            if answer.upper() == "Q":
                sys.exit()
            if answer.upper() in ("Y", "O", ""):
                auth_token_file = "auth_token"
                if os.path.exists(auth_token_file):
                    answer = "?"
                    while answer.upper() not in ("Y", "N", "O", "Q", ""):
                        answer = input("File already exists. Overwrite? [Y]es / [N]o (default): ")
                    if answer.upper() == "Q":
                        sys.exit()
                else:
                    answer = "Y"
                if answer.upper() in ("Y", "O"):
                    with open(auth_token_file, "w") as f:
                        f.write(new_token)
                    print(f'[INFO] Token saved in "{auth_token_file}".')
        else:
            print("[ERROR] Impossible to create a new token...")
        sys.exit()

    check_version()
    if version:
        sys.exit()

    # Lecture du token.
    if os.path.exists(auth_token):
        auth_token = open(auth_token, "r").readline().strip()

    rdly = readly.Readly(auth_token)
    is_token_ok = rdly.is_token_ok()
    if not is_token_ok:
        print(f'[ERROR] Invalid token ("{auth_token}")...')
    while not is_token_ok:
        auth_token = input("Authentication token: ")
        if auth_token.upper() == "Q":
            sys.exit()
        if os.path.exists(auth_token):
            auth_token = open(auth_token, "r").readline()
        rdly = readly.Readly(auth_token)
        is_token_ok = rdly.is_token_ok()
        if not is_token_ok:
            print(f'[ERROR] Invalid token ("{auth_token}")...')
        else:
            answer = "?"
            while answer.upper() not in ("Y", "N", "O", "Q", ""):
                answer = input("Save token? [Y]es (default) / [N]o: ")
            if answer.upper() == "Q":
                sys.exit()
            if answer.upper() in ("Y", "O", ""):
                auth_token_file = "auth_token"
                if os.path.exists(auth_token_file):
                    answer = "?"
                    while answer.upper() not in ("Y", "N", "O", "Q", ""):
                        answer = input("File already exists. Overwrite? [Y]es / [N]o (default): ")
                    if answer.upper() == "Q":
                        sys.exit()
                else:
                    answer = "Y"
                if answer.upper() in ("Y", "O"):
                    with open(auth_token_file, "w") as f:
                        f.write(auth_token)
                    print(f'[INFO] Token saved in "{auth_token_file}".')

    rdly.output_folder = output_folder
    rdly.img_format = image_format
    rdly.img_quality = quality
    rdly.container_format = container_format
    rdly.pause_sec = pause_sec
    rdly.no_clean = no_clean
    rdly.get_articles = get_articles
    rdly.dpi = dpi
    rdly.use_default = use_default

    is_command_line = True

    # Lecture de l'URL.
    all_urls = []
    if not os.path.isfile(url):
        # C'est une URL ou un ID qui nous a été donné.
        while not is_valid_url(url):
            url = input('URL of publication or publication_id ("Q" to quit): ')
            is_command_line = False
            if url.upper() == "Q":
                sys.exit()
        all_urls.append(url)
    else:
        # C'est un fichier d'URLs qui nous a été donné.
        all_urls = [
            line.strip()
            for line in open(url, "r", encoding="utf-8").readlines()
            if len(line.strip()) > 0 and line.strip()[0] != "#"
        ]

    # On boucle sur toutes les URLs.
    for url in all_urls:
        print(f"[INFO] URL: {url}")
        # Id de publication
        match = re.match("([\d\w]{24})", url)
        if match:
            publication_id = match[1]
        else:
            # URL indirecte.
            if re.match("https://(.+?).readly.com/products/(.+)", url):
                res = requests.get(url)
                if res.status_code != 200:
                    print(f'[ERROR] Invalid URL "{url}".')
                    sys.exit()
                else:
                    match = re.search(r"\"publication_id\":\"([\d\w]+)\"", res.text)
                    if not match or not match[1]:
                        print(f'[ERROR] Invalid URL "{url}".')
                        sys.exit()
                    url = f"https://go.readly.com/magazines/{match[1]}"

            match = re.match("https://go.readly.com(.*)/(.+?)/(.+)", url)
            if not match:
                print(f'[ERROR] Invalid URL "{url}".')
                sys.exit()
            category, magazine_id, publication_id = match.groups()
            magazine_id = magazine_id.replace("/", "")
            publication_id = publication_id.replace("/", "")

        def download_issue(publication_id: str, infos: dict):
            print(
                f"[INFO] {publication_id} : \"{infos['title']} - {infos['issue']} ({infos['date']})\" will be downloaded."
            )
            output_filename = output_pattern
            for k in infos:
                output_filename = output_filename.replace(f"{k}", str(infos[k]))

            # Préparation du nom de sortie.
            output_filename = clean_name(output_filename)

            if get_articles_only:
                rdly.no_clean = True
                rdly.get_articles = True
                rdly.get_content = False
                print(f"[INFO] Articles only.")
            else:
                print(f"[INFO] Image format: {image_format.upper()}")
                print(f"[INFO] Image quality : {quality}")
                print(f"[INFO] Container format : {container_format.upper()}")
            rdly.download_publication(publication_id, save_as=output_filename)

        # Lecture des infos.
        infos = rdly.get_infos(publication_id)
        if not infos:
            # On n'a pas d'infos, c'est peut-être un ID de magazine.
            print(f'[WARNING] Invalid publication_id "{publication_id}"...')
            print(f'[INFO] Available publications for magazine_id "{publication_id}": ')
            publications = rdly.get_all_publications(publication_id)
            for p in publications:
                print(f"{p['id']}\t{p['title']} - {p['issue']} ({p['date']})")
            print(f"[INFO] {len(publications)} publications found.")

            if not is_command_line:
                res = "?"
                while not res.isdigit():
                    res = input(
                        f"How many issues do you want to download? (number or 'Q' to quit) (default: {max_dl}): "
                    )
                    if res.upper() == "Q":
                        sys.exit()
                    if not res:
                        res = str(max_dl)
                max_dl = int(res)
            for p in publications[:max_dl]:
                publication_id = p["id"]
                infos = rdly.get_infos(publication_id)
                if infos:
                    download_issue(publication_id, infos)
                else:
                    print(f'[ERROR] Invalid publication_id "{publication_id}"...')
        else:
            download_issue(publication_id, infos)
