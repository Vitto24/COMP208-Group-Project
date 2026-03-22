# Sample Data Generation — Logic & Parameters

How the `generate_sample_data` management command works, and how to tweak it.

```bash
python manage.py generate_sample_data          # generate data
python manage.py generate_sample_data --clear   # wipe + regenerate
```

---

## Timetable

### How it works

1. Modules are grouped by **(course, year, semester)** using `ModuleCourse` records.
   Example group: CS BSc, Year 2, Semester 2 → COMP202, COMP208, COMP284, etc.

2. For each group, a shared weekly grid of time slots is built.
   Events are placed into free slots so that **no two modules in the same group clash**.

3. Each module gets **3 events** per week:
   - 2 Lectures
   - 1 Lab (STEM modules) or 1 Tutorial (non-STEM modules)

4. The algorithm tries to spread a module's events across **different days**.
   If all other days are full, it falls back to placing on any free day.

5. Every enrolled student gets the same timetable for each module.

### Available time slots

| Day | Slots | Count |
|-----|-------|-------|
| MON | 09–16 | 8 |
| TUE | 09–16 | 8 |
| WED | 09–11 | 3 (sport after 12) |
| THU | 09–16 | 8 |
| FRI | 09–16 | 8 |
| **Total** | | **35** |

A typical group of 5–6 modules needs 15–18 slots, so 35 is more than enough.

### STEM vs non-STEM

Module code prefixes that count as STEM (and get Labs instead of Tutorials):

`COMP`, `MATH`, `PHYS`, `CHEM`, `CIVE`, `ELEC`, `MECH`, `AERO`, `ENG`, `BIOL`

Everything else gets a Tutorial.

### Parameters to tweak

All at the top of `dashboard/management/commands/generate_sample_data.py`:

| Parameter | Default | What it does |
|-----------|---------|-------------|
| `START_HOUR` | 9 | Earliest event start time |
| `END_HOUR` | 17 | Latest event end (last slot at 16:00) |
| `LECTURES_PER_MODULE` | 2 | Number of lecture slots per module |
| `LABS_PER_MODULE` | 1 | Number of lab/tutorial slots per module |
| `EVENT_DURATION` | 1 | All events are 1 hour |
| `WED_CUTOFF` | 12 | No Wednesday events at or after this hour |
| `STEM_PREFIXES` | list | Module code prefixes that get Labs |
| `ROOMS` | list | Room names to randomly pick from |

---

## Deadlines (Assignment Due Dates)

### How it works

1. Assessment data (title, weight, type) is pulled from the scraper JSONs in `scraper/data/modules/`.
   If a module has no scraper data, a random fallback template is used.

2. Assessments are split into **coursework** and **exams**.

3. **Coursework** due dates are spaced evenly across the semester's coursework window,
   then rounded to the nearest **Friday**. If two land on the same Friday, the second
   gets bumped forward a week.

4. **Exam** dates are placed randomly within the exam period (weekdays only),
   with at least 2 days between exams for the same module.

### Semester dates

| | Sem 1 | Sem 2 |
|---|---|---|
| Teaching | 22 Sep – 12 Dec | 26 Jan – 20 Mar + 13 Apr – 8 May |
| Coursework window | 6 Oct – 28 Nov | 2 Feb – 1 May |
| Exam period | 12 Jan – 23 Jan | 11 May – 22 May |

### Fallback assessments

If a module has no scraper data, one of these templates is randomly picked:

- Coursework 1 (30%) + Coursework 2 (30%) + Final Exam (40%)
- Assignment 1 (20%) + Assignment 2 (20%) + Exam (60%)
- Project (40%) + Written Exam (60%)
- Lab Report (25%) + Midterm (25%) + Final Exam (50%)

### Parameters to tweak

| Parameter | Default | What it does |
|-----------|---------|-------------|
| `COURSEWORK_DUE_DAY` | 4 (Friday) | Day of week for coursework deadlines (0=Mon) |
| `SEM1_CW_START` / `SEM1_CW_END` | 6 Oct / 28 Nov | Sem 1 coursework date range |
| `SEM2_CW_START` / `SEM2_CW_END` | 2 Feb / 1 May | Sem 2 coursework date range |
| `SEM1_EXAM_START` / `SEM1_EXAM_END` | 12 Jan / 23 Jan | Sem 1 exam period |
| `SEM2_EXAM_START` / `SEM2_EXAM_END` | 11 May / 22 May | Sem 2 exam period |

---

## Grades

### How it works

For each student + assignment pair, a **(score, status)** pair is generated.
The status and score are always consistent:
- `graded` → has a numeric score
- `submitted` / `not_submitted` → score is `None`

### Past due date assignments

| Probability | Status | Score |
|-------------|--------|-------|
| 70% | graded | Random (mean 62, std dev 14, clamped 20–95) |
| 20% | submitted | None |
| 10% | not_submitted | None |

### Future due date assignments

| Probability | Status | Score |
|-------------|--------|-------|
| 50% | not_submitted | None |
| 20% | submitted | None |
| 30% | graded | Random (same distribution) |

### Parameters to tweak

| Parameter | Default | What it does |
|-----------|---------|-------------|
| `GRADE_MEAN` | 62 | Average score |
| `GRADE_STD_DEV` | 14 | Score spread |
| `GRADE_MIN` | 20 | Lowest possible score |
| `GRADE_MAX` | 95 | Highest possible score |
