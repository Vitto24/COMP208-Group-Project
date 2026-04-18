# Algorithms

Notes on the non-obvious bits of logic behind the app, for portfolio + Q&A.

---

## Degree classification & projection

Final degree % is a weighted combination of yearly averages. Weights are stored on the `Course` model (`modules/models.py:22-26`) so a BSc (0/30/70) and an MEng (0/20/30/50) can use the same grades code.

```python
year_1_weight = models.IntegerField(default=0)
year_2_weight = models.IntegerField(default=30)
year_3_weight = models.IntegerField(default=70)
year_4_weight = models.IntegerField(default=0)
year_5_weight = models.IntegerField(default=0)
```

The grades view (`grades/views.py`) maps the projection to the UK classification bands:

- ≥ 70 → First (1st)
- ≥ 60 → Upper Second (2:1)
- ≥ 50 → Lower Second (2:2)
- ≥ 40 → Third (3rd)
- else → Pass/Fail

The projection itself is the student's current-year average — not a full weighted sum — because students only have partial grades until the year is over, so the weighted version would underestimate badly.

---

## 60-credit semester validation

UoL rules say every semester must total exactly 60 credits. The validation lives in `accounts/utils.py:224` (`update_module_selection`):

1. Remove the user from all current-year modules.
2. Re-add all compulsory modules (can't be deselected).
3. Add whichever optional modules the student ticked.
4. Sum credits per semester. If any semester has ≠ 60 credits, reject the selection and return an error string.

Previous years are left alone so historical grades stay intact if a student changes course or year.

The same file has `_fill_semester` (line 8) which handles auto-enrolment during registration. Picks largest-credit modules first to avoid leaving unfillable gaps (e.g. 15 remaining credits with only 7.5cr modules left).

---

## Timetable clash detection

Generated once per `(course, year, semester)` group by the sample-data command (`dashboard/management/commands/generate_sample_data.py:411`).

Grid is 35 slots (5 days × 7 hours, minus Wed afternoon for sport). Each module gets 3 events (2 lectures + 1 lab/tutorial). The scheduler:

1. Shuffles the module list so each run produces a different timetable.
2. For each module, tries to pick slots on days it hasn't used yet — spreads the module across the week.
3. Removes the slot from the pool once picked, so no other module in the same group can land on it.

STEM modules (COMP, MATH, ELEC, etc.) get a lab. Non-STEM get a tutorial. Prefix list is in the same file.

All students in the same group share the schedule — realistic, and means the clash check only needs to run once per group instead of per student.

---

## Student ID generation

8-digit numeric, starting with `2` to look like a real UoL ID (20xxxxxx). Lives in `accounts/models.py:56`:

```python
def _generate_student_id(self):
    while True:
        candidate = '2' + str(uuid.uuid4().int)[:7]
        if not UserProfile.objects.filter(student_id=candidate).exists():
            return candidate
```

UUID gives a large enough pool that the uniqueness loop effectively never retries in practice. The `startswith('2')` check in the tests (`accounts/tests.py`) enforces the UoL-style prefix.
