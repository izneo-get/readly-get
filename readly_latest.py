# -*- coding: utf-8 -*-
__version__ = "01.00"

import requests
import json
import sys
import argparse

if __name__ == "__main__":
    # Parse des arguments passés en ligne de commande.
    parser = argparse.ArgumentParser(
        description="""Script to display Readly latest publications."""
    )
    parser.add_argument(
        "--type",
        "-t",
        type=str,
        default="magazines,newspapers",
        help='Type of publications ("magazines", "newspapers" or "magazines,newspapers"). Default="magazines,newspapers".',
    )
    parser.add_argument(
        "--limit",
        "-i",
        metavar="NUMBER",
        type=int,
        default=25,
        help="Number of issues per type. Default=25",
    )
    parser.add_argument(
        "--countries",
        "-c",
        type=str,
        default="",
        help='Coutries of publications (2-letters format) coma separated. Default="" (all coutries).',
    )
    parser.add_argument(
        "--languages",
        "-l",
        type=str,
        default="",
        help='Languages of publications (2-letters format) coma separated. Default="" (all languages).',
    )
    parser.add_argument(
        "--categories",
        "-a",
        type=str,
        default="",
        help='Categories of publications coma separated. Default="" (all categories).',
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        metavar="OUTPUT_FILE",
        default="",
        help="Output to a file.",
    )

    args = parser.parse_args()
    pub_type = args.type
    per_page = args.limit
    origin = ""
    countries = args.countries  # FR%2CUS%2CGB%2CIE%2CAU%2CNZ%2CCA
    countries = countries.replace(",", "%2C")
    languages = args.languages  # en%2Cfr
    languages = languages.replace(",", "%2C")
    categories = args.categories  #
    categories = categories.replace(",", "%2C")
    output_file = args.output

    fo = None
    if output_file:
        fo = open(output_file, "w", encoding="utf-8")
    for p_type in pub_type.split(","):
        print(f"# {p_type.upper()}", file=fo)
        url = f"https://d3og6tlt23zks5.cloudfront.net/{p_type}?ppage=1&per_page={per_page}&origin={origin}&countries={countries}&languages={languages}&categories={categories}"

        res = requests.get(url)
        if res.status_code != 200:
            print("[ERROR] Can't find latest.")
            sys.exit()

        issues = json.loads(res.text)

        for issue in issues["content"]:
            issue["date"] = issue["publish_date"][: len("YYYY-MM-DD")]
            if "issue" not in issue:
                issue["issue"] = issue["date"]

            print(f"# {issue['title']} - {issue['issue']} ({issue['date']})", file=fo)
            print(f"{issue['id']}", file=fo)
        print("", file=fo)
