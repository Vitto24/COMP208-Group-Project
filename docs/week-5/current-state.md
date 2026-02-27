# Uni Tracker — Current State (Week 5)

Overview of how the website works as of 27 Feb 2026.

---

## Layout

Every page uses `base.html` which has a sidebar + main content area:

```
┌──────────────┬──────────────────────────────────────────────┐
│              │  Page Title            Week 3 · Semester 2   │
│  Uni Tracker │──────────────────────────────────────────────│
│  University  │                                              │
│  of Liverpool│                                              │
│              │                                              │
│  Dashboard   │              Page Content                    │
│  Modules     │                                              │
│  Timetable   │                                              │
│  Grades      │                                              │
│  Notifs      │                                              │
│  Settings    │                                              │
│              │                                              │
│              │                                              │
│  ┌──┐        │                                              │
│  │TS│ Test   │                                              │
│  └──┘ Student│                                              │
│       Logout │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

- Sidebar highlights the active page
- User avatar shows initials (e.g. TS for Test Student)
- Logout link at bottom

---

## Pages

### 1. Login (`/accounts/login/`)

Simple login form. Test credentials: `student` / `password`

```
┌──────────────────────────┐
│         Login             │
│                           │
│  Username: [___________]  │
│  Password: [___________]  │
│                           │
│  [ Login ]                │
│                           │
│  Don't have an account?   │
│  Register                 │
└──────────────────────────-┘
```

**Status:** Working. Has register link too.

---

### 2. Dashboard (`/`)

Shows module cards and upcoming deadlines.

```
┌─────────────────────────────────────────────────────────┐
│  My Modules                                             │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ COMP202  │ │ COMP208  │ │ COMP284  │ │ COMP285  │   │
│  │ 15 creds │ │ 15 creds │ │ 15 creds │ │ 15 creds │   │
│  │ Complex. │ │ Group SW │ │ Scripting│ │ CASD     │   │
│  │ of Alg.  │ │ Dev Proj │ │ Langs    │ │          │   │
│  │ Due soon │ │          │ │          │ │          │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│                                                         │
│  Upcoming Deadlines                                     │
│  ┌─────────────────────────────────────────────────┐    │
│  │ ⚠ COMP202  Class Test              Tue 10 Mar  │    │
│  │   COMP208  Software Demo           Mon 20 Apr  │    │
│  │   COMP202  Programming Assg.       Fri 24 Apr  │    │
│  │   COMP208  Design                  Mon 11 May  │    │
│  │   COMP208  Portfolio (Team)        Mon 11 May  │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**Status:** Working. Uses inline styles (needs moving to style.css).
**Note:** Shows all modules/deadlines — not filtered by logged-in user. No `@login_required`.

---

### 3. Modules (`/modules/`)

List of all modules as clickable cards.

```
┌─────────────────────────────────────────────────┐
│  ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │ COMP202    │ │ COMP208    │ │ COMP284    │   │
│  │ 15 credits │ │ 15 credits │ │ 15 credits │   │
│  │ Complexity │ │ Group SW   │ │ Scripting  │   │
│  │ of Alg.    │ │ Dev Project│ │ Languages  │   │
│  └────────────┘ └────────────┘ └────────────┘   │
│  ┌────────────┐ ┌────────────┐                   │
│  │ COMP285    │ │ ULMS254    │                   │
│  │ 15 credits │ │ 15 credits │                   │
│  │ CASD       │ │ Becoming   │                   │
│  │            │ │ Entrepr.   │                   │
│  └────────────┘ └────────────┘                   │
└─────────────────────────────────────────────────┘
```

### Module Detail (`/modules/COMP208/`)

Shows module info, assignments table, and materials.

```
┌─────────────────────────────────────────────────┐
│  COMP208 — Group Software Development Project   │
│  Semester 2 · 2025/26                           │
│  Lecturer: TBC · Credits: 15                    │
│  Description: ...                               │
│                                                 │
│  Assignments                                    │
│  ┌──────────────┬────────┬──────┬──────────┐    │
│  │ Title        │ Weight │ Type │ Due Date  │    │
│  ├──────────────┼────────┼──────┼──────────┤    │
│  │ Software Demo│ 20%    │ ...  │ 20 Apr   │    │
│  │ Design       │ 30%    │ ...  │ 11 May   │    │
│  │ Portfolio    │ 50%    │ ...  │ 11 May   │    │
│  └──────────────┴────────┴──────┴──────────┘    │
│                                                 │
│  Materials                                      │
│  ▸ Week 1 — Introduction                        │
│  ▸ Week 2 — Requirements                        │
└─────────────────────────────────────────────────┘
```

**Status:** Working (after title bug fix). No `@login_required`.

---

### 4. Timetable (`/timetable/`)

Weekly grid with colour-coded event cards. Week navigation. Today panel + deadlines.

```
┌──────────────────────────────────────────────────────────────┐
│         MON        TUE        WED        THU        FRI     │
│          23        (24)        25         26         27      │
│       ─────────  ════════  ─────────  ─────────  ─────────  │
│ 09:00 │COMP208 │ │COMP208│                      │ULMS254 │  │
│       │COMP284 │ │       │                      │        │  │
│ 10:00 │        │ │       │ │COMP285│            │        │  │
│ 11:00 │        │ │       │ │COMP202│            │COMP202 │  │
│ 12:00 │COMP285 │ │       │ │       │            │        │  │
│ 13:00 │        │ │       │                                  │
│ 14:00 │        │                                            │
│ 15:00 │COMP284 │ │COMP285│            │COMP285│             │
│ 16:00 │        │ │COMP202│                                  │
│ 17:00 │        │                                │ULMS254 │  │
│                                                             │
│ Semester 2 · 26 Jan – 20 Mar  < Week 5 of 8 >  ● Lec etc  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────┐ ┌──────────────────────────┐
│ Today (Tue 24th)     │ │ Upcoming Deadlines       │
│                      │ │                          │
│ → 09:00 COMP208  NOW│ │ COMP202 Class Test 10Mar │
│ ○ 15:00 COMP285     │ │ COMP208 SW Demo    20Apr │
│ ○ 16:00 COMP202     │ │ COMP202 Prog Assg  24Apr │
│                      │ │ COMP208 Design     11May │
│                      │ │ COMP208 Portfolio  11May │
└──────────────────────┘ └──────────────────────────┘
```

**Features:**
- Colour-coded cards: blue=Lecture, purple=Drop-in, green=Lab/Tutorial, orange=Seminar
- Multi-hour events show correct duration (rowspan)
- Today's date gets a dark circle badge
- Week navigation: < Week 5 of 8 >
- Today panel shows done/now/upcoming status
- Next 5 upcoming deadlines

**Status:** Working. Has `@login_required`. Filters by logged-in user.

---

### 5. Grades (`/grades/`)

Expandable sections per module with assignment grades.

```
┌──────────────────────────────────────────────────┐
│  My Grades                                       │
│                                                  │
│  ▸ COMP202: Complexity of Alg. — Overall: 68%   │
│  ▾ COMP208: Group SW Dev — Overall: 72%         │
│    ┌──────────────┬────────┬──────┐              │
│    │ Assignment   │ Weight │ Mark │              │
│    ├──────────────┼────────┼──────┤              │
│    │ Software Demo│ 20%    │ 65%  │              │
│    │ Design       │ 30%    │ 75%  │              │
│    │ Portfolio    │ 50%    │ 72%  │              │
│    └──────────────┴────────┴──────┘              │
│  ▸ COMP284: Scripting Languages — Overall: 70%   │
└──────────────────────────────────────────────────┘
```

**Status:** Working. No `@login_required`.

---

### 6. Notifications

**Status:** Not built. Sidebar link goes to `#`.

---

### 7. Settings (`/settings/`)

**Status:** Placeholder only. Shows "Settings page — coming soon."

---

## Tech Stack

- **Backend:** Django 4.2, Python 3.10, SQLite
- **Frontend:** Django templates, vanilla CSS (`static/css/style.css`)
- **Auth:** Django built-in auth (login/register/logout)
- **Data:** Fixture file `fixtures/sample_data.json` — load with `python manage.py loaddata fixtures/sample_data.json`

---

## Key Models

| Model           | App       | Fields                                                        |
| --------------- | --------- | ------------------------------------------------------------- |
| Module          | modules   | code, name, description, credits, lecturer, semester, year    |
| Week            | modules   | module, number, title                                         |
| Material        | modules   | week, title, type, url, available                             |
| Assignment      | grades    | module, title, weight, type, due_date                         |
| Grade           | grades    | student, assignment, score, status                            |
| TimetableEntry  | timetable | student, module, day, start_time, end_time, room, event_type  |

---

## Known Issues / TODOs

- Dashboard and modules have no `@login_required` — anyone can access without logging in
- Dashboard and modules show all data, not filtered by logged-in user
- Dashboard uses inline styles instead of style.css
- Notifications page not built
- Settings page not built
- base.html header has hardcoded "Week 3 · Semester 2" — should be dynamic
