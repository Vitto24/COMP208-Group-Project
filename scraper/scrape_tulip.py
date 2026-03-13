#!/usr/bin/env python3
"""Scrape TULIP module detail pages for University of Liverpool modules."""

import argparse
import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup, Tag

TULIP_URL_TEMPLATE = "https://tulip.liv.ac.uk/mods/student/cm_{code}_202526.htm"


def get_section(tables: list[Tag], section_num: int) -> Tag | None:
    """Find the table containing a given numbered section (1-24)."""
    target = str(section_num) + "."
    for table in tables:
        first_td = table.find("td", class_="ddheader")
        if first_td and first_td.get_text(strip=True) == target:
            return table
    return None


def get_section_text(tables: list[Tag], section_num: int) -> str:
    """Get the text content of a numbered section's value cell."""
    table = get_section(tables, section_num)
    if not table:
        return ""
    # The value is typically in a td with colspan="2" and class "dddefault"
    # or the last dddefault cell in the row
    row = table.find("tr")
    if not row:
        return ""
    cells = row.find_all("td", class_="dddefault")
    if not cells:
        return ""
    # Return the first dddefault cell that has actual content
    for cell in cells:
        text = cell.get_text(strip=True)
        if text and text != "\xa0":
            return text
    return ""


def parse_semester(text: str) -> int | None:
    text_lower = text.lower()
    if "first" in text_lower:
        return 1
    if "second" in text_lower:
        return 2
    if "whole" in text_lower or "both" in text_lower:
        return 0  # whole year
    return None


def parse_level(text: str) -> int | None:
    match = re.search(r"Level\s+(\d+)", text)
    return int(match.group(1)) if match else None


def parse_credits(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else None


def parse_prerequisites(text: str) -> list[str]:
    """Extract module codes from a prerequisites string.

    e.g. "COMP122 Object-Oriented Programming 2024-25" -> ["COMP122"]
    """
    codes = re.findall(r"[A-Z]{3,5}\d{3}", text)
    return list(dict.fromkeys(codes))  # deduplicate, preserve order


def parse_assessment(tables: list[Tag]) -> list[dict]:
    """Parse section 19 assessment table."""
    section_table = get_section(tables, 19)
    if not section_table:
        return []

    # The assessment data is in an HTML <table> embedded inside the section's
    # content. We need to find rows where the first <td>/<p> is a digit (1, 2, 3...).
    # To avoid duplicates from nested table levels, collect all <tr> elements
    # and deduplicate by using a set of (index, form, weight).
    assessments = []
    seen = set()

    for row in section_table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        cell_texts = [c.get_text(strip=True) for c in cells]
        # First cell should be a number (assessment index)
        if not cell_texts[0].isdigit():
            continue

        form = cell_texts[1].replace("\r", "").replace("\n", "")  # "Written Exam", "Coursework", etc.
        try:
            weight = int(cell_texts[2])
        except (ValueError, IndexError):
            continue

        # Deduplicate
        key = (cell_texts[0], form, weight)
        if key in seen:
            continue
        seen.add(key)

        # Extract a short title from the details field
        details = cell_texts[4] if len(cells) > 4 else ""
        # Try to extract the title from parenthesized prefix like "(219.2) Assignment 2"
        title_match = re.search(r"\)\s*(.+?)(?:\s+There|\s+Standard|\.|$)", details)
        title = title_match.group(1).strip().replace("\r", " ") if title_match else form

        # Normalize form to type
        form_lower = form.lower()
        if "exam" in form_lower:
            atype = "exam"
        elif "coursework" in form_lower:
            atype = "coursework"
        elif "practical" in form_lower:
            atype = "practical"
        else:
            atype = form_lower

        assessments.append({
            "type": atype,
            "title": title,
            "weight": weight,
        })

    return assessments


def get_long_section_text(tables: list[Tag], section_num: int) -> str:
    """Get text from sections that have nested tables (20, 21, 23).

    These sections have a structure like:
      <table> (outer - has section number)
        <tr> header row </tr>
        <tr>
          <td colspan="2">
            <table> (inner)
              <tr><td class="dddefault"> content </td></tr>
            </table>
            ... possibly more inner tables for section 21 ...
          </td>
        </tr>
      </table>
    """
    section_table = get_section(tables, section_num)
    if not section_table:
        return ""

    # Find only the innermost dddefault cells that contain actual content
    # (cells that don't themselves contain nested tables)
    texts = []
    for td in section_table.find_all("td", class_="dddefault"):
        # Skip cells that contain nested tables (they're wrapper cells)
        if td.find("table"):
            continue
        # Skip cells that are just spacing
        text = td.get_text(strip=True)
        if text and text != "\xa0" and text != "&nbsp":
            texts.append(text)
    return "\n".join(texts)


def scrape_course_description(module_page_url: str) -> str:
    """Fetch the student-friendly description from a course module page.

    e.g. https://www.liverpool.ac.uk/courses/computer-science-bsc-hons/modules/comp208
    The description is in <main id="main-content"> > section.rb-content-flow > p tags.
    """
    try:
        resp = requests.get(module_page_url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException:
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    main = soup.find("main", id="main-content")
    if not main:
        return ""
    section = main.find("section", class_="rb-content-flow")
    if not section:
        return ""
    paragraphs = section.find_all("p")
    return "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))


def scrape_module(code: str, course_module_url: str = "") -> dict | None:
    """Scrape a single TULIP module page, optionally enriching with course page description."""
    url = TULIP_URL_TEMPLATE.format(code=code)
    resp = requests.get(url, timeout=30)
    if resp.status_code == 404:
        print(f"  WARNING: {code} not found on TULIP (404)")
        return None
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    tables = soup.find_all("table")

    if not tables:
        print(f"  WARNING: {code} page has no tables")
        return None

    # Section 1: Module Title
    name = get_section_text(tables, 1)
    # Section 2: Module Code
    scraped_code = get_section_text(tables, 2)
    # Section 4: Originating Department
    department = re.sub(r'^School of\s+', '', get_section_text(tables, 4))
    # Section 6: Semester
    semester_text = get_section_text(tables, 6)
    semester = parse_semester(semester_text)
    # Section 7: CATS Level
    level_text = get_section_text(tables, 7)
    level = parse_level(level_text)
    # Section 8: CATS Value (credits)
    credits_text = get_section_text(tables, 8)
    credits = parse_credits(credits_text)

    # Section 9: Module Leader - nested table with name, dept, email in separate cells
    lecturer = ""
    section9 = get_section(tables, 9)
    if section9:
        # Find the innermost table (staff details) and get just the name cell
        inner_tables = section9.find_all("table")
        for inner in inner_tables:
            first_td = inner.find("td", class_="dddefault")
            if first_td:
                lecturer = first_td.get_text(strip=True)
                break

    # Section 17: Prerequisites — parse to list of module codes
    prereq_text = get_long_section_text(tables, 17)
    prereq_text = re.sub(
        r"^Pre-requisites.*?:\s*", "", prereq_text, flags=re.IGNORECASE
    ).strip()
    prerequisites = parse_prerequisites(prereq_text)

    # Section 19: Assessment
    assessment = parse_assessment(tables)

    # Student-friendly description from course module page only
    description = ""
    if course_module_url:
        description = scrape_course_description(course_module_url)

    return {
        "code": scraped_code or code,
        "name": name,
        "department": department,
        "semester": semester,
        "level": level,
        "credits": credits,
        "lecturer": lecturer,
        "description": description,
        "prerequisites": prerequisites,
        "assessment": assessment,
        "course_url": course_module_url or None,
        "tulip_url": url,
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape TULIP module detail pages")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--code", help="Single module code (e.g. COMP219)")
    group.add_argument("--course", help="Path to course JSON from scrape_course.py")
    parser.add_argument(
        "--delay", type=float, default=1.0,
        help="Delay in seconds between requests (default: 1.0)",
    )
    parser.add_argument("-o", "--output-dir", help="Output directory for module JSONs")
    args = parser.parse_args()

    out_dir = args.output_dir or os.path.join(os.path.dirname(__file__), "data", "modules")
    os.makedirs(out_dir, exist_ok=True)

    # Build list of (code, course_module_url) tuples
    if args.code:
        modules = [(args.code.upper(), "")]
    else:
        with open(args.course) as f:
            course_data = json.load(f)
        # Collect all unique module codes across years
        course_base_url = course_data.get("course_url", "")
        modules = []
        seen = set()
        for year_data in course_data["years"].values():
            for entry in year_data.get("compulsory", []) + year_data.get("optional", []):
                code = entry["code"] if isinstance(entry, dict) else entry
                if code not in seen:
                    # Derive course module page URL from course base URL
                    url = f"{course_base_url}/modules/{code.lower()}" if course_base_url else ""
                    modules.append((code, url))
                    seen.add(code)
        print(f"Found {len(modules)} unique modules in {os.path.basename(args.course)}")

    success = 0
    skipped = 0
    failed = []
    for i, (code, course_module_url) in enumerate(modules):
        out_path = os.path.join(out_dir, f"{code}.json")
        if os.path.exists(out_path):
            print(f"[{i+1}/{len(modules)}] Skipping {code} (already exists)")
            skipped += 1
            continue
        print(f"[{i+1}/{len(modules)}] Scraping {code} ...")
        try:
            data = scrape_module(code, course_module_url)
            if data:
                with open(out_path, "w") as f:
                    json.dump(data, f, indent=2)
                print(f"  -> {data['name']} ({data['credits']} credits, semester {data['semester']})")
                success += 1
            else:
                failed.append(code)
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            failed.append(code)

        if i < len(modules) - 1:
            time.sleep(args.delay)

    print(f"\nDone: {success} scraped, {skipped} skipped, {len(failed)} failed")
    if failed:
        print(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
