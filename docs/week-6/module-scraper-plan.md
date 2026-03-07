# Module Scraper

## Overview

A two-stage scraping pipeline that collects University of Liverpool module data:

1. **Course scraper** (`scraper/scrape_course.py`) — Scrapes a UoL course page to extract module codes organized by year/semester.
2. **TULIP scraper** (`scraper/scrape_tulip.py`) — Scrapes TULIP detail pages for each module code to get full metadata (name, credits, assessment, etc.).

Output is stored as JSON files in `scraper/data/` (course structures) and `scraper/data/modules/` (individual module details).

## `scraper/scrape_course.py`

Scrapes a University of Liverpool course page to extract module codes organized by year/semester.

### Supported course types

- **UG courses** — Parses "Year one", "Year two", etc. Output keys: `"1"`, `"2"`, `"3"`, `"4"`
- **PGT semester-based courses** — Parses "Semester one", "Semester two". Output keys: `"S1"`, `"S2"`
- **Final project sections** — Output key: `"FP"`

### Usage

```bash
python scraper/scrape_course.py "<course-url>"
```

### Output

JSON file in `scraper/data/<slug>.json` with this structure:

```json
{
  "course_name": "Computer Science BSc (Hons)",
  "course_url": "https://www.liverpool.ac.uk/courses/computer-science-bsc-hons",
  "years": {
    "1": {
      "compulsory": ["COMP101", "COMP105", ...],
      "optional": []
    },
    "2": {
      "compulsory": ["COMP202", ...],
      "optional": ["COMP282", ...]
    }
  }
}
```

## `scraper/scrape_tulip.py`

Scrapes TULIP detail pages for each module code to get full metadata. Skips modules that already have a JSON file in the output directory.

### Fields extracted

`code`, `name`, `department`, `semester`, `level`, `credits`, `lecturer`, `description`, `prerequisites`, `assessment`, `course_url`, `tulip_url`

### Usage

```bash
# Scrape all modules for a course (skips existing files)
python scraper/scrape_tulip.py --course scraper/data/<course>.json

# Scrape a single module
python scraper/scrape_tulip.py --code COMP208
```

Options:
- `--delay <seconds>` — Delay between requests (default: 1.0)
- `-o <dir>` — Output directory (default: `scraper/data/modules/`)

### Output

Individual JSON files in `scraper/data/modules/<CODE>.json`:

```json
{
  "code": "COMP208",
  "name": "Group Software Development Project",
  "department": "Computer Science",
  "semester": 2,
  "level": 5,
  "credits": 15.0,
  "lecturer": "...",
  "description": "...",
  "prerequisites": ["COMP122"],
  "assessment": [
    {"type": "coursework", "title": "Group Project", "weight": 100}
  ],
  "course_url": "https://...",
  "tulip_url": "https://tulip.liv.ac.uk/mods/student/cm_COMP208_202526.htm"
}
```

## Current data

| Course | File | Modules |
|--------|------|---------|
| Computer Science BSc | `computer-science-bsc.json` | 56 |
| Computer Science MEng | `computer-science-meng.json` | 70 |
| Computer Science MSc | `computer-science-msc.json` | 15 |
| Accounting and Finance BSc | `accounting-and-finance-bsc.json` | 36 |
| History BA | `history-ba.json` | — |

**113 unique module detail files** in `scraper/data/modules/`.

Note: COMP525 is listed on the MSc course page but returns 404 on TULIP (likely a new or renamed module for 2025/26).

## How to add a new course

1. Find the course page URL on `liverpool.ac.uk/courses/` (e.g. `https://www.liverpool.ac.uk/courses/mathematics-bsc-hons`)
2. Run the course scraper:
   ```bash
   python scraper/scrape_course.py "https://www.liverpool.ac.uk/courses/mathematics-bsc-hons"
   ```
3. Check the output in `scraper/data/<slug>.json` — verify module codes look correct
4. Run the TULIP scraper to fetch module details:
   ```bash
   python scraper/scrape_tulip.py --course scraper/data/mathematics-bsc.json
   ```
5. New module detail JSONs appear in `scraper/data/modules/`. Existing modules are skipped automatically.
