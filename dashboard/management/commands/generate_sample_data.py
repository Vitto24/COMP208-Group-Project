"""
Generate sample assignments, grades, and timetable entries for demo purposes.

Reads assessment info (titles, weights, types) from the scraper JSON files,
then creates Assignment records with spaced-out due dates, Grade records with
random scores, and clash-free TimetableEntry records for every enrolled student.

Usage:
    python manage.py generate_sample_data
    python manage.py generate_sample_data --clear   # wipe existing generated data first

See docs/sample-data-logic.md for full details on the generation logic and
how to tweak the parameters below.
"""

import json
import os
import random
import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from modules.models import Module, ModuleCourse
from grades.models import Assignment, Grade
from timetable.models import TimetableEntry


# ── Path to scraper JSONs ──────────────────────────────────────────────
SCRAPER_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scraper', 'data', 'modules')

# ── Timetable parameters ──────────────────────────────────────────────
START_HOUR = 9              # earliest event start
END_HOUR = 17               # latest event end (last slot starts at 16)
LECTURES_PER_MODULE = 2     # how many lecture slots each module gets
LABS_PER_MODULE = 1         # how many lab/tutorial slots each module gets
EVENT_DURATION = 1          # all events are 1 hour
WED_CUTOFF = 12             # no Wednesday events at or after this hour (sport)

# module code prefixes that count as STEM (get labs instead of tutorials)
STEM_PREFIXES = ['COMP', 'MATH', 'PHYS', 'CHEM', 'CIVE', 'ELEC', 'MECH', 'AERO', 'ENG', 'BIOL']

ROOMS = [
    'Ashton Lecture Theatre',
    'Central Teaching Hub - LT1',
    'Central Teaching Hub - LT2',
    'Central Teaching Hub - SR3',
    'Chadwick Building - G05',
    'George Holt Building - Room 101',
    'Rendall Building - LT1',
    'Rendall Building - LT2',
    'Engineering, Lecture Room E3',
    'Sherrington Lecture Theatre 2',
    'South Campus Teaching Hub - LT3',
    'Thompson Yates Building - Room 104',
    'Harold Cohen Library - PC Lab',
    'George Holt Building - Teaching Lab H1.05',
    '502 Building - Flex Room 2',
]

# ── Deadline parameters ───────────────────────────────────────────────
COURSEWORK_DUE_DAY = 4      # 0=Mon ... 4=Fri

# semester 1 dates
SEM1_TEACHING_START = datetime.date(2025, 9, 22)
SEM1_CW_START = datetime.date(2025, 10, 6)       # coursework window opens (week 3)
SEM1_CW_END = datetime.date(2025, 11, 28)         # coursework window closes (week 11)
SEM1_EXAM_START = datetime.date(2026, 1, 12)
SEM1_EXAM_END = datetime.date(2026, 1, 23)

# semester 2 dates
SEM2_TEACHING_START = datetime.date(2026, 1, 26)
SEM2_CW_START = datetime.date(2026, 2, 2)         # coursework window opens (week 2)
SEM2_CW_END = datetime.date(2026, 5, 1)           # coursework window closes (week 11)
SEM2_EXAM_START = datetime.date(2026, 5, 11)
SEM2_EXAM_END = datetime.date(2026, 5, 22)

# ── Grade parameters ──────────────────────────────────────────────────
GRADE_MEAN = 62
GRADE_STD_DEV = 14
GRADE_MIN = 20
GRADE_MAX = 95


class Command(BaseCommand):
    help = 'Generate sample assignments, grades, and timetable data from scraper JSONs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing assignments, grades, and timetable entries before generating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            TimetableEntry.objects.all().delete()
            Grade.objects.all().delete()
            Assignment.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared.'))

        # load scraper data into a dict keyed by module code
        scraper_data = self._load_scraper_data()
        self.stdout.write(f'Loaded assessment data for {len(scraper_data)} modules from scraper JSONs')

        # get all modules that have at least one enrolled student
        modules_with_students = Module.objects.filter(students__isnull=False).distinct()
        self.stdout.write(f'Found {modules_with_students.count()} modules with enrolled students')

        # ── Generate assignments + grades ──────────────────────────────
        assignment_count = 0
        grade_count = 0

        for module in modules_with_students:
            students = list(module.students.all())
            a, g = self._create_assignments_and_grades(module, students, scraper_data)
            assignment_count += a
            grade_count += g

        # ── Generate timetable (clash-free by course/year/sem group) ───
        timetable_count = self._generate_all_timetables(modules_with_students)

        self.stdout.write(self.style.SUCCESS(
            f'Done! Created {assignment_count} assignments, '
            f'{grade_count} grades, {timetable_count} timetable entries.'
        ))

    # ──────────────────────────────────────────────────────────────────
    # SCRAPER DATA
    # ──────────────────────────────────────────────────────────────────

    def _load_scraper_data(self):
        """Load all scraper module JSONs into a dict keyed by module code."""
        data = {}
        scraper_dir = os.path.normpath(SCRAPER_DIR)

        if not os.path.isdir(scraper_dir):
            self.stdout.write(self.style.WARNING(f'Scraper directory not found: {scraper_dir}'))
            return data

        for filename in os.listdir(scraper_dir):
            if not filename.endswith('.json'):
                continue
            filepath = os.path.join(scraper_dir, filename)
            try:
                with open(filepath) as f:
                    module_data = json.load(f)
                code = module_data.get('code', filename.replace('.json', ''))
                data[code] = module_data
            except (json.JSONDecodeError, IOError):
                continue

        return data

    # ──────────────────────────────────────────────────────────────────
    # ASSIGNMENTS + GRADES
    # ──────────────────────────────────────────────────────────────────

    def _create_assignments_and_grades(self, module, students, scraper_data):
        """Create assignment and grade records for a single module."""
        assignment_count = 0
        grade_count = 0

        # get assessment data from scraper or use fallback
        assessments = scraper_data.get(module.code, {}).get('assessment', [])
        if not assessments:
            assessments = self._generate_generic_assessments()

        # split into coursework and exams, then generate due dates
        coursework = [a for a in assessments if a.get('type', 'coursework') == 'coursework']
        exams = [a for a in assessments if a.get('type') == 'exam']

        # calculate spaced due dates for coursework
        cw_dates = self._space_coursework_dates(module.semester, len(coursework))
        exam_dates = self._pick_exam_dates(module.semester, len(exams))

        # create coursework assignments
        for i, assessment in enumerate(coursework):
            title = assessment.get('title', assessment['title']) if isinstance(assessment, dict) else assessment[0]
            weight = assessment.get('weight', assessment['weight']) if isinstance(assessment, dict) else assessment[1]
            atype = 'coursework'

            due_date = cw_dates[i] if i < len(cw_dates) else cw_dates[-1]

            assignment, created = Assignment.objects.get_or_create(
                module=module,
                title=title,
                defaults={
                    'weight': weight,
                    'type': atype,
                    'due_date': due_date,
                },
            )
            if created:
                assignment_count += 1

            for student in students:
                score, status = self._random_grade(assignment)
                _, created = Grade.objects.get_or_create(
                    student=student,
                    assignment=assignment,
                    defaults={'score': score, 'status': status},
                )
                if created:
                    grade_count += 1

        # create exam assignments
        for i, assessment in enumerate(exams):
            title = assessment.get('title', assessment['title']) if isinstance(assessment, dict) else assessment[0]
            weight = assessment.get('weight', assessment['weight']) if isinstance(assessment, dict) else assessment[1]
            atype = 'exam'

            due_date = exam_dates[i] if i < len(exam_dates) else exam_dates[-1]

            assignment, created = Assignment.objects.get_or_create(
                module=module,
                title=title,
                defaults={
                    'weight': weight,
                    'type': atype,
                    'due_date': due_date,
                },
            )
            if created:
                assignment_count += 1

            for student in students:
                score, status = self._random_grade(assignment)
                _, created = Grade.objects.get_or_create(
                    student=student,
                    assignment=assignment,
                    defaults={'score': score, 'status': status},
                )
                if created:
                    grade_count += 1

        return assignment_count, grade_count

    def _space_coursework_dates(self, semester, count):
        """Space coursework due dates evenly across the semester, all on Fridays."""
        if count == 0:
            return []

        if semester == 1:
            window_start = SEM1_CW_START
            window_end = SEM1_CW_END
        else:
            window_start = SEM2_CW_START
            window_end = SEM2_CW_END

        total_days = (window_end - window_start).days
        dates = []

        for i in range(count):
            # place each item in the middle of its chunk
            chunk_mid = window_start + datetime.timedelta(
                days=int(total_days * (i + 0.5) / count)
            )
            # round to nearest Friday
            days_until_friday = (COURSEWORK_DUE_DAY - chunk_mid.weekday()) % 7
            friday = chunk_mid + datetime.timedelta(days=days_until_friday)

            # if this Friday is the same as the previous one, bump forward a week
            if dates and friday <= dates[-1]:
                friday = dates[-1] + datetime.timedelta(weeks=1)

            dates.append(friday)

        return dates

    def _pick_exam_dates(self, semester, count):
        """Pick random weekday dates within the exam period."""
        if count == 0:
            return []

        if semester == 1:
            exam_start = SEM1_EXAM_START
            exam_end = SEM1_EXAM_END
        else:
            exam_start = SEM2_EXAM_START
            exam_end = SEM2_EXAM_END

        exam_days = (exam_end - exam_start).days
        dates = []

        for _ in range(count):
            # pick a random date in the exam window, ensure it's a weekday
            for _attempt in range(20):
                offset = random.randint(0, exam_days)
                date = exam_start + datetime.timedelta(days=offset)
                if date.weekday() < 5:  # Mon-Fri
                    # make sure it's at least 2 days from other exams
                    too_close = any(abs((date - d).days) < 2 for d in dates)
                    if not too_close:
                        dates.append(date)
                        break
            else:
                # couldn't find a non-clashing date, just pick one
                dates.append(exam_start + datetime.timedelta(days=random.randint(0, exam_days)))

        return dates

    def _random_grade(self, assignment):
        """Generate a consistent (score, status) pair for a student grade."""
        is_future = assignment.due_date and assignment.due_date > datetime.date.today()

        if is_future:
            # future assignment - most students haven't done it yet
            roll = random.random()
            if roll < 0.5:
                return None, 'not_submitted'
            elif roll < 0.7:
                return None, 'submitted'
            else:
                # some keen students already graded
                score = round(max(GRADE_MIN, min(GRADE_MAX, random.gauss(GRADE_MEAN, GRADE_STD_DEV))), 1)
                return score, 'graded'
        else:
            # past due date - mostly graded by now
            roll = random.random()
            if roll < 0.7:
                score = round(max(GRADE_MIN, min(GRADE_MAX, random.gauss(GRADE_MEAN, GRADE_STD_DEV))), 1)
                return score, 'graded'
            elif roll < 0.9:
                return None, 'submitted'
            else:
                return None, 'not_submitted'

    def _generate_generic_assessments(self):
        """Fallback assessments for modules without scraper data.

        Returns list of dicts matching the scraper JSON format.
        """
        templates = [
            [
                {'title': 'Coursework 1', 'weight': 30, 'type': 'coursework'},
                {'title': 'Coursework 2', 'weight': 30, 'type': 'coursework'},
                {'title': 'Final Exam', 'weight': 40, 'type': 'exam'},
            ],
            [
                {'title': 'Assignment 1', 'weight': 20, 'type': 'coursework'},
                {'title': 'Assignment 2', 'weight': 20, 'type': 'coursework'},
                {'title': 'Exam', 'weight': 60, 'type': 'exam'},
            ],
            [
                {'title': 'Project', 'weight': 40, 'type': 'coursework'},
                {'title': 'Written Exam', 'weight': 60, 'type': 'exam'},
            ],
            [
                {'title': 'Lab Report', 'weight': 25, 'type': 'coursework'},
                {'title': 'Midterm', 'weight': 25, 'type': 'exam'},
                {'title': 'Final Exam', 'weight': 50, 'type': 'exam'},
            ],
        ]
        return random.choice(templates)

    # ──────────────────────────────────────────────────────────────────
    # TIMETABLE GENERATION (clash-free)
    # ──────────────────────────────────────────────────────────────────

    def _build_available_slots(self):
        """Build the list of all available (day, hour) slots."""
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
        slots = []
        for day in days:
            for hour in range(START_HOUR, END_HOUR):
                # skip Wednesday afternoon (sport)
                if day == 'WED' and hour >= WED_CUTOFF:
                    continue
                slots.append((day, hour))
        return slots

    def _is_stem_module(self, module):
        """Check if a module is STEM based on its code prefix."""
        for prefix in STEM_PREFIXES:
            if module.code.startswith(prefix):
                return True
        return False

    def _schedule_group(self, modules):
        """Schedule all modules in a group into a clash-free grid.

        Returns a dict: {module_code: [(day, hour, event_type), ...]}
        """
        all_slots = self._build_available_slots()
        free_slots = set(all_slots)
        schedule = {}

        # shuffle so the order is random each time
        module_list = list(modules)
        random.shuffle(module_list)

        for module in module_list:
            events = []

            # figure out whether this module gets a lab or tutorial
            extra_type = 'PC Teaching Centre' if self._is_stem_module(module) else 'Tutorial'

            # pick slots for 2 lectures, trying to spread across different days
            used_days = set()

            for _ in range(LECTURES_PER_MODULE):
                slot = self._pick_free_slot(free_slots, avoid_days=used_days)
                if slot is None:
                    # no free slots on other days, try any free slot
                    slot = self._pick_free_slot(free_slots, avoid_days=set())
                if slot is None:
                    # grid is completely full - shouldn't happen with normal module counts
                    self.stdout.write(self.style.WARNING(
                        f'  No free slots left for {module.code} lecture, skipping'
                    ))
                    break
                day, hour = slot
                free_slots.discard(slot)
                used_days.add(day)
                events.append((day, hour, 'Lecture'))

            # pick slot for lab/tutorial on a different day from lectures
            for _ in range(LABS_PER_MODULE):
                slot = self._pick_free_slot(free_slots, avoid_days=used_days)
                if slot is None:
                    slot = self._pick_free_slot(free_slots, avoid_days=set())
                if slot is None:
                    self.stdout.write(self.style.WARNING(
                        f'  No free slots left for {module.code} {extra_type}, skipping'
                    ))
                    break
                day, hour = slot
                free_slots.discard(slot)
                used_days.add(day)
                events.append((day, hour, extra_type))

            schedule[module.code] = events

        return schedule

    def _pick_free_slot(self, free_slots, avoid_days=None):
        """Pick a random free slot, preferring days not in avoid_days.

        Returns (day, hour) or None if no free slots.
        """
        if not free_slots:
            return None

        if avoid_days:
            # try to find slots on days we haven't used yet
            preferred = [(d, h) for d, h in free_slots if d not in avoid_days]
            if preferred:
                return random.choice(preferred)

        # fall back to any free slot
        return random.choice(list(free_slots))

    def _generate_all_timetables(self, modules_with_students):
        """Generate clash-free timetables grouped by year/semester.

        We group by (year, semester) rather than (course, year, semester) because
        modules are shared across courses (e.g. BSc and MEng both take COMP202).
        Grouping by year+sem means each module is scheduled exactly once, and all
        students taking it get the same time slot.
        """
        timetable_count = 0

        # skip if timetable entries already exist
        if TimetableEntry.objects.exists():
            self.stdout.write('Timetable entries already exist, skipping generation.')
            return 0

        # group enrolled modules by (year, semester)
        groups = {}
        for module in modules_with_students:
            key = (module.year, module.semester)
            if key not in groups:
                groups[key] = set()
            groups[key].add(module)

        self.stdout.write(f'Scheduling timetable for {len(groups)} year/semester groups...')

        # for each group, schedule modules clash-free and create entries
        for (year, semester), group_modules in groups.items():
            self.stdout.write(f'  Year {year} Sem {semester}: {len(group_modules)} modules ({len(group_modules) * 3} slots needed, 35 available)')
            schedule = self._schedule_group(group_modules)

            # create timetable entries for each student enrolled in each module
            for module in group_modules:
                students = list(module.students.all())
                module_events = schedule.get(module.code, [])

                for day, hour, event_type in module_events:
                    # pick a room for this event (same room for all students)
                    room = random.choice(ROOMS)
                    start_time = datetime.time(hour, 0)
                    end_time = datetime.time(hour + EVENT_DURATION, 0)

                    for student in students:
                        TimetableEntry.objects.create(
                            student=student,
                            module=module,
                            day=day,
                            start_time=start_time,
                            end_time=end_time,
                            room=room,
                            event_type=event_type,
                            semester=semester,
                            weeks='1-12',
                        )
                        timetable_count += 1

        return timetable_count
