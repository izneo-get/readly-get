# -*- coding: utf-8 -*-

import requests
from requests.adapters import HTTPAdapter
from requests.sessions import session
from urllib3.util import Retry
import json
import struct
import sys
from io import BytesIO
import img2pdf
import os
from PIL import Image, ImageOps
import shutil
import re
import argparse
import time
from pikepdf import _cpphelpers

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
    resolution = 2400
    dpi = 0
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
        url = f"https://api.readly.com/issue/{publication_id}/content?format={download_format}&r={self.resolution}"
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
        if not full_content['success']:
            print("[ERROR] Can't get publication. Please check your token.")
            sys.exit()

        if not save_as:
            save_as = publication_id
        tmp_output_folder = f"{self.output_folder}/{save_as}"
        os.makedirs(tmp_output_folder, exist_ok=True)
        if self.get_content:
            content = full_content["content"]
            for i, c_url in enumerate(content):
                print(f"Downloading page {i+1} / {len(content)}", end="\r")
                r = requests_retry_session(session=self.session).get(c_url)
                page = f"000{i}"[-3:]
                current_file = f"{tmp_output_folder}/page_{page}.{self.img_format}"
                im = Image.open(BytesIO(self.decode(r.content, publication_id)))
                im = im.convert("RGB")
                if self.dpi:
                    im.save(current_file, self.img_format, quality=self.img_quality, dpi=(self.dpi, self.dpi))
                else:
                    im.save(current_file, self.img_format, quality=self.img_quality)
                time.sleep(self.pause_sec)
            print()

        if self.get_articles:
            if "articles" in full_content:
                articles = full_content["articles"]
                for i, a in enumerate(articles):
                    print(f"Page {i+1} / {len(articles)}", end="\r")
                    r = requests_retry_session(session=self.session).get(a["url"])
                    with open(f"{tmp_output_folder}/article_{a['key']}.zip", "wb") as f:
                        f.write(self.decode(r.content, publication_id))
                    time.sleep(self.pause_sec)
                print()
            else:
                print("[INFO] No articles found.")

        if self.get_content and self.container_format.upper() == "PDF".upper():
            print("PDF creation...")
            if self.img_format.upper() == "WEBP".upper():
                print(
                    "[WARNING] Image format \"WEBP\" is not optimized for PDF container. The output file may be large."
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
                if self.dpi:
                    f.write(img2pdf.convert(imgs, dpi=self.dpi))
                else:
                    f.write(img2pdf.convert(imgs))
            print(f'"{pdf_file}" successfully created!')

        if self.get_content and self.container_format.upper() == "CBZ".upper():
            print("CBZ creation...")
            zip_file = self.get_unique_path(self.output_folder, save_as, "zip")
            shutil.make_archive(zip_file[:-4], "zip", tmp_output_folder)
            cbz_file = self.get_unique_path(self.output_folder, save_as, "cbz")
            os.rename(zip_file, cbz_file)
            print(f'"{cbz_file}" successfully created!')

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

        r = requests_retry_session(session=self.session).get(
            url,
            allow_redirects=True,
            headers=headers,
        )
        if not r.text or "NOT FOUND" in r.text.upper():
            return False
        infos = json.loads(r.text)
        infos["date"] = infos["publish_date"][: len("YYYY-MM-DD")]
        if "issue" not in infos:
            infos["issue"] = infos["date"]
        return infos

    def get_all_publications(self, magazine_id):
        for pub_type in ["magazines", "newspapers"]: 
            url = f"https://d3og6tlt23zks5.cloudfront.net/{pub_type}/{magazine_id}"
            headers = {
                "X-Auth-Token": self.token,
                "User-Agent": self.user_agent,
            }

            r = requests_retry_session(session=self.session).get(
                url,
                allow_redirects=True,
                headers=headers,
            )
            if not r.text:
                continue
            infos = json.loads(r.text)
            return [
                {
                    "id": c["id"],
                    "title": c["title"],
                    "issue": c["issue"] if "issue" in c else c["publish_date"][: len("YYYY-MM-DD")],
                    "date": c["publish_date"][: len("YYYY-MM-DD")],
                }
                for c in infos["content"]
            ]

    def is_token_ok(self):
        url = f"https://api.readly.com/subscriptions"
        headers = {
            "X-Auth-Token": self.token,
            "User-Agent": self.user_agent,
        }

        r = requests_retry_session(session=self.session).get(
            url,
            allow_redirects=True,
            headers=headers,
        )
        infos = json.loads(r.text)
        return "subscriptions" in infos and infos["subscriptions"][0]["isActive"] # and infos["subscriptions"][0]["subscriptionEnd"]

    @classmethod
    def create_token(cls, country="US"):
        unique_id = time.time()
        url = f"https://api.readly.com/account/signup"
        headers = {
            "User-Agent": cls.user_agent,
            "Accept-Version": "7",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "email": f"readly-get-{unique_id}@gmail.com",
            "password": "readlymag",
            "country": country,
            "platform": "Android",
            "id": f"00000000-4242-4242-0000-00{unique_id}",
            "platformInfo": "SDK=22;BRAND=samsung;MODEL=SM-J320H;RESOLUTION=720x1280;HEAP=256;TEXTURESIZE=4096;SCREENDIAGONALSIZE=4.83;SCREENCATEGORY=SMALL;HIRESREADER=true;INSTALLERPACKAGE=com.android.vending",
            "build": "4.8.5",
            "apiVer": "7",
            "appsflyerId": "1588711795353-1696111357546090178",
        }
        r = requests_retry_session(session=cls.session).post(
            url,
            allow_redirects=True,
            headers=headers,
            data=data
        )

        if not r.text:
            return False
        infos = json.loads(r.text)
        return infos['loginResponse']['token']
