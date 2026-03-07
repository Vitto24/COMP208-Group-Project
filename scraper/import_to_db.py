#!/usr/bin/env python3
"""Import scraped module JSON data into the Django database.

Usage:
    # From the project root (where manage.py lives):
    python scraper/import_to_db.py scraper/data/modules/
    python scraper/import_to_db.py scraper/data/modules/COMP219.json

    # With a course file to also create Course + ModuleCourse links:
    python scraper/import_to_db.py scraper/data/modules/ --course scraper/data/computer-science-bsc.json

    # Dry run (no DB changes):
    python scraper/import_to_db.py scraper/data/modules/ --dry-run
"""

import argparse
import json
import os
import re
import sys

# Set up Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uni_tracker.settings")

import django  # noqa: E402
django.setup()

from modules.models import Module, Course, ModuleCourse  # noqa: E402


def guess_degree_level(course_name: str) -> str:
    """Try to figure out the degree level from the course name."""
    name = course_name.lower()
    if 'meng' in name:
        return 'MEng'
    elif 'msc' in name:
        return 'MSc'
    elif 'beng' in name:
        return 'BEng'
    elif 'llb' in name:
        return 'LLB'
    elif 'ba' in name:
        return 'BA'
    else:
        return 'BSc'


def make_slug(course_name: str) -> str:
    """Turn a course name into a URL-friendly slug."""
    # strip stuff in brackets like "(Hons)"
    cleaned = re.sub(r'\(.*?\)', '', course_name).strip()
    slug = cleaned.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


def load_course_data(course_path: str) -> dict:
    """Load course JSON and build a code -> {year, compulsory} mapping.

    Also returns the course metadata (name, url, slug, degree_level).
    """
    with open(course_path) as f:
        data = json.load(f)

    course_name = data.get("course_name", "Unknown Course")
    course_meta = {
        "name": course_name,
        "url": data.get("course_url", ""),
        "slug": make_slug(course_name),
        "degree_level": guess_degree_level(course_name),
    }

    # Build mapping of module code -> year + compulsory info
    code_info = {}
    for year_key, year_data in data.get("years", {}).items():
        for entry in year_data.get("compulsory", []):
            code = entry["code"] if isinstance(entry, dict) else entry
            code_info[code] = {"year": year_key, "compulsory": True}
        for entry in year_data.get("optional", []):
            code = entry["code"] if isinstance(entry, dict) else entry
            code_info[code] = {"year": year_key, "compulsory": False}

    return {"meta": course_meta, "modules": code_info}


def import_module(module_data: dict, dry_run: bool = False) -> str:
    """Import a single module. Returns 'created', 'updated', or 'skipped'."""
    code = module_data["code"]

    defaults = {
        "name": module_data["name"],
        "description": module_data.get("description", ""),
        "credits": module_data.get("credits", 15),
        "lecturer": module_data.get("lecturer", ""),
        "semester": module_data.get("semester", 1) or 1,
        "department": module_data.get("department", ""),
    }

    if dry_run:
        exists = Module.objects.filter(code=code).exists()
        return "would update" if exists else "would create"

    _, created = Module.objects.update_or_create(code=code, defaults=defaults)
    return "created" if created else "updated"


def link_modules_to_course(course_obj, course_modules: dict, dry_run: bool = False):
    """Create ModuleCourse records linking modules to the course."""
    linked = 0
    skipped = 0

    for code, info in course_modules.items():
        try:
            module = Module.objects.get(code=code)
        except Module.DoesNotExist:
            # module wasn't in our scraped data, skip it
            continue

        if dry_run:
            exists = ModuleCourse.objects.filter(module=module, course=course_obj).exists()
            print(f"    {'would update' if exists else 'would link'}: {code} -> {course_obj.slug}")
            linked += 1
            continue

        ModuleCourse.objects.update_or_create(
            module=module,
            course=course_obj,
            defaults={
                "year": info["year"],
                "is_compulsory": info["compulsory"],
            },
        )
        linked += 1

    return linked


def main():
    parser = argparse.ArgumentParser(description="Import scraped modules into Django DB")
    parser.add_argument("path", help="Path to a module JSON file or directory of module JSONs")
    parser.add_argument("--course", help="Course JSON for year/compulsory info + course creation")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without making changes")
    args = parser.parse_args()

    # Load course data if provided
    course_data = load_course_data(args.course) if args.course else None

    # Collect JSON files to import
    if os.path.isfile(args.path):
        json_files = [args.path]
    elif os.path.isdir(args.path):
        json_files = sorted(
            os.path.join(args.path, f)
            for f in os.listdir(args.path)
            if f.endswith(".json")
        )
    else:
        print(f"ERROR: {args.path} is not a file or directory", file=sys.stderr)
        sys.exit(1)

    if not json_files:
        print("No JSON files found.")
        sys.exit(0)

    if args.dry_run:
        print("=== DRY RUN (no changes will be made) ===\n")

    # Import all modules
    results = {"created": 0, "updated": 0, "would create": 0, "would update": 0, "error": 0}
    for path in json_files:
        with open(path) as f:
            data = json.load(f)
        code = data.get("code", os.path.basename(path).replace(".json", ""))
        try:
            result = import_module(data, args.dry_run)
            results[result] = results.get(result, 0) + 1
            print(f"  {result}: {code} - {data.get('name', '?')}")
        except Exception as e:
            results["error"] += 1
            print(f"  ERROR: {code} - {e}", file=sys.stderr)

    print(f"\nModule summary: {dict((k, v) for k, v in results.items() if v > 0)}")

    # Create course + link modules if --course was given
    if course_data:
        meta = course_data["meta"]
        print(f"\n--- Course: {meta['name']} ({meta['slug']}) ---")

        if args.dry_run:
            print(f"  Would create/update course: {meta['name']}")
        else:
            course_obj, created = Course.objects.update_or_create(
                slug=meta["slug"],
                defaults={
                    "name": meta["name"],
                    "url": meta["url"],
                    "degree_level": meta["degree_level"],
                },
            )
            status = "created" if created else "updated"
            print(f"  Course {status}: {course_obj.name}")

        # Link modules to course
        if args.dry_run:
            linked = link_modules_to_course(None, course_data["modules"], dry_run=True)
        else:
            linked = link_modules_to_course(course_obj, course_data["modules"], dry_run=False)
        print(f"  Linked {linked} modules to course")


if __name__ == "__main__":
    main()
