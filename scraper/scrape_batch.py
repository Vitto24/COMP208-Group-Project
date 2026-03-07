#!/usr/bin/env python3
"""Batch scrape multiple courses and import them into the database.

Runs the full pipeline for each course:
  1. scrape_course.py - get module codes from the course page
  2. scrape_tulip.py  - get module details from TULIP (skips existing)
  3. import_to_db.py  - import modules + create course + link

Usage:
    python scraper/scrape_batch.py
    python scraper/scrape_batch.py --scrape-only   # skip DB import step
"""

import argparse
import os
import subprocess
import sys
import time

# All 20 course URLs (first 5 already scraped, but we re-import them too)
COURSES = [
    # Already scraped
    "https://www.liverpool.ac.uk/courses/computer-science-bsc-hons",
    "https://www.liverpool.ac.uk/courses/computer-science-meng-hons",
    "https://www.liverpool.ac.uk/courses/computer-science-msc",
    "https://www.liverpool.ac.uk/courses/accounting-and-finance-bsc-hons",
    "https://www.liverpool.ac.uk/courses/history-ba-hons",
    # New courses
    "https://www.liverpool.ac.uk/courses/mathematics-bsc-hons",
    "https://www.liverpool.ac.uk/courses/physics-bsc-hons",
    "https://www.liverpool.ac.uk/courses/politics-ba-hons",
    "https://www.liverpool.ac.uk/courses/civil-engineering-beng-hons",
    "https://www.liverpool.ac.uk/courses/mechanical-engineering-beng-hons",
    "https://www.liverpool.ac.uk/courses/psychology-bsc-hons",
    "https://www.liverpool.ac.uk/courses/law-llb-hons",
    "https://www.liverpool.ac.uk/courses/english-ba-hons",
    "https://www.liverpool.ac.uk/courses/biological-sciences-bsc-hons",
    "https://www.liverpool.ac.uk/courses/economics-bsc-hons",
    "https://www.liverpool.ac.uk/courses/business-management-ba-hons",
    "https://www.liverpool.ac.uk/courses/architecture-ba-hons",
    "https://www.liverpool.ac.uk/courses/geography-bsc-hons",
    "https://www.liverpool.ac.uk/courses/music-ba-hons",
    "https://www.liverpool.ac.uk/courses/philosophy-ba-hons",
]

SCRAPER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRAPER_DIR)


def run_cmd(cmd, description):
    """Run a command and print its output. Returns True on success."""
    print(f"\n  >> {description}")
    print(f"     {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=False)
    if result.returncode != 0:
        print(f"  !! Command failed with exit code {result.returncode}")
        return False
    return True


def get_course_json_path(url):
    """Figure out the JSON filename that scrape_course.py will create."""
    import re
    slug = url.rstrip("/").split("/")[-1]
    slug = re.sub(r"-hons$", "", slug)
    return os.path.join(SCRAPER_DIR, "data", f"{slug}.json")


def main():
    parser = argparse.ArgumentParser(description="Batch scrape courses")
    parser.add_argument(
        "--scrape-only", action="store_true",
        help="Only scrape, don't import into database",
    )
    parser.add_argument(
        "--import-only", action="store_true",
        help="Only import existing scraped data, don't scrape",
    )
    args = parser.parse_args()

    python = sys.executable
    total = len(COURSES)

    if not args.import_only:
        # Step 1: Scrape course pages to get module codes
        print("=" * 60)
        print("STEP 1: Scraping course pages")
        print("=" * 60)

        for i, url in enumerate(COURSES):
            json_path = get_course_json_path(url)
            # always re-scrape course pages (they're fast)
            print(f"\n[{i+1}/{total}] {url}")
            run_cmd(
                [python, os.path.join(SCRAPER_DIR, "scrape_course.py"), url],
                "scrape_course.py",
            )
            time.sleep(0.5)  # small delay between course page requests

        # Step 2: Scrape TULIP pages for module details
        print("\n" + "=" * 60)
        print("STEP 2: Scraping TULIP module details (skip-existing)")
        print("=" * 60)

        for i, url in enumerate(COURSES):
            json_path = get_course_json_path(url)
            if not os.path.exists(json_path):
                print(f"\n[{i+1}/{total}] Skipping (no course JSON): {json_path}")
                continue
            print(f"\n[{i+1}/{total}] TULIP scrape for {os.path.basename(json_path)}")
            run_cmd(
                [python, os.path.join(SCRAPER_DIR, "scrape_tulip.py"),
                 "--course", json_path, "--delay", "1.0"],
                "scrape_tulip.py",
            )

    if not args.scrape_only:
        # Step 3: Import into database
        print("\n" + "=" * 60)
        print("STEP 3: Importing into database")
        print("=" * 60)

        modules_dir = os.path.join(SCRAPER_DIR, "data", "modules")
        for i, url in enumerate(COURSES):
            json_path = get_course_json_path(url)
            if not os.path.exists(json_path):
                print(f"\n[{i+1}/{total}] Skipping (no course JSON): {json_path}")
                continue
            print(f"\n[{i+1}/{total}] Importing {os.path.basename(json_path)}")
            run_cmd(
                [python, os.path.join(SCRAPER_DIR, "import_to_db.py"),
                 modules_dir, "--course", json_path],
                "import_to_db.py",
            )

    print("\n" + "=" * 60)
    print("ALL DONE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
