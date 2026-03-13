#!/usr/bin/env python3
"""Scrape UoL undergraduate and postgraduate taught course listing pages."""

import json
import os
import re

import requests
from bs4 import BeautifulSoup

LISTING_PAGES = {
    "undergraduate": "https://www.liverpool.ac.uk/courses/undergraduate",
    "postgraduate_taught": "https://www.liverpool.ac.uk/courses/postgraduate-taught",
}

INTEGRATED_MASTERS = {
    "MEng", "MChem", "MPhys", "MMath", "MBiol", "MArch", "MPlan", "MPharm", "MBChB",
}


def get_level(degree_type: str, source: str) -> str:
    """Determine course level from degree type and source page."""
    if source == "postgraduate_taught":
        return "postgraduate_taught"
    prefix = degree_type.split()[0] if degree_type else ""
    if prefix in INTEGRATED_MASTERS:
        return "integrated_masters"
    return "undergraduate"


def parse_rb_cards(soup: BeautifulSoup, source: str) -> list[dict]:
    """Parse courses from section.rb-card elements."""
    courses = []
    for card in soup.select("section.rb-card"):
        h3 = card.find("h3", class_="rb-card__title")
        if not h3:
            continue
        link = h3.find("a")
        if not link or not link.get("href", "").startswith("/courses/"):
            continue

        name = link.get_text(strip=True)
        url = "https://www.liverpool.ac.uk" + link["href"]

        # Degree type from rb-tags <dd><span>
        degree_type = ""
        tags_dl = card.find("dl", class_="rb-tags")
        if tags_dl:
            dd = tags_dl.find("dd")
            if dd:
                degree_type = dd.get_text(strip=True)

        # Key info from rb-key-information <dl>
        ucas_code = ""
        duration = ""
        info_dl = card.find("dl", class_="rb-key-information")
        if info_dl:
            for div in info_dl.find_all("div"):
                dt = div.find("dt")
                dd = div.find("dd")
                if not dt or not dd:
                    continue
                label = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                if label == "UCAS code:":
                    ucas_code = value
                elif label == "Full-time:":
                    duration = value

        courses.append({
            "name": name,
            "degree_type": degree_type,
            "ucas_code": ucas_code or None,
            "duration": duration,
            "level": get_level(degree_type, source),
            "url": url,
        })

    return courses


def scrape_course_list() -> list[dict]:
    """Scrape undergraduate and postgraduate taught listing pages."""
    all_courses = []
    seen_urls = set()

    for source, url in LISTING_PAGES.items():
        print(f"Scraping {url} ...")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        courses = parse_rb_cards(soup, source)
        print(f"  Found {len(courses)} courses on {source} page")

        for course in courses:
            if course["url"] not in seen_urls:
                seen_urls.add(course["url"])
                all_courses.append(course)

    # Sort by name, then degree_type
    all_courses.sort(key=lambda c: (c["name"].lower(), c["degree_type"].lower()))
    return all_courses


def main():
    courses = scrape_course_list()
    print(f"Total: {len(courses)} courses (after deduplication)")

    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "all_courses.json")
    with open(out_path, "w") as f:
        json.dump(courses, f, indent=2)

    # Print summary by level
    levels = {}
    for c in courses:
        levels[c["level"]] = levels.get(c["level"], 0) + 1
    for level, count in sorted(levels.items()):
        print(f"  {level}: {count}")

    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
