#!/usr/bin/env python3
"""Scrape a University of Liverpool course page to extract module codes by year."""

import argparse
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

WORD_TO_NUM = {
    "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8",
}


def scrape_course(url: str) -> dict:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract course name from <title>
    title_tag = soup.find("title")
    course_name = title_tag.text.split("|")[0].strip() if title_tag else ""

    years = {}
    # Each year/semester is inside a <details> with a <summary> like "Year one" or "Semester one"
    for details in soup.find_all("details"):
        summary = details.find("summary")
        if not summary:
            continue
        summary_text = summary.get_text(strip=True)
        # Match "Year one", "Semester one", or "Final project"
        match = re.match(r"(?:Year|Semester)\s+(\w+)", summary_text, re.IGNORECASE)
        is_final = summary_text.lower().startswith("final project")

        if not match and not is_final:
            continue

        if is_final:
            year_num = "FP"
        else:
            period_word = match.group(1).lower()
            period_num = WORD_TO_NUM.get(period_word)
            if not period_num:
                continue  # Skip "Year in China", "Year abroad", etc.
            # Use "S1", "S2" keys for semester-based courses, "1", "2" for year-based
            is_semester = summary_text.lower().startswith("semester")
            year_num = f"S{period_num}" if is_semester else period_num

        compulsory = []
        optional = []

        for table in details.find_all("table", class_="rb-table"):
            thead = table.find("thead")
            if not thead:
                continue
            header_text = thead.get_text(strip=True).lower()
            is_optional = "optional" in header_text

            tbody = table.find("tbody")
            if not tbody:
                continue

            for row in tbody.find_all("tr"):
                td = row.find("td")
                if not td:
                    continue
                cell_text = td.get_text(strip=True)
                # Module code is in parentheses, e.g. "COMPUTER SYSTEMS (COMP124)"
                code_match = re.search(r"\(([A-Z]{3,5}\d{3})\)", cell_text)
                if code_match:
                    code = code_match.group(1)
                    if is_optional:
                        optional.append(code)
                    else:
                        compulsory.append(code)

        years[year_num] = {"compulsory": compulsory, "optional": optional}

    return {
        "course_name": course_name,
        "course_url": url,
        "years": years,
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape a UoL course page for module codes")
    parser.add_argument("url", help="Course page URL")
    parser.add_argument("-o", "--output", help="Output JSON path (default: auto-generated in scraper/data/)")
    args = parser.parse_args()

    print(f"Scraping {args.url} ...")
    data = scrape_course(args.url)

    if not data["years"]:
        print("ERROR: No year/module data found. Check the URL.", file=sys.stderr)
        sys.exit(1)

    # Auto-generate output filename from URL slug
    if args.output:
        out_path = args.output
    else:
        slug = args.url.rstrip("/").split("/")[-1]
        # Shorten common suffixes
        slug = re.sub(r"-hons$", "", slug)
        out_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{slug}.json")

    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    total = sum(
        len(y["compulsory"]) + len(y["optional"])
        for y in data["years"].values()
    )
    print(f"Found {total} modules across {len(data['years'])} years")
    for yr, mods in sorted(data["years"].items()):
        print(f"  Year {yr}: {len(mods['compulsory'])} compulsory, {len(mods['optional'])} optional")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
