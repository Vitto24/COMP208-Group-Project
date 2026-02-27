# Week 5 — Meeting 5 (Fri 27 Feb)

---

## Agenda

1. **Week 4 review** — each person shows what they've done
2. **Bug fixes** — modules page was broken, now fixed
3. **Pick week 5 tasks** — continue building out pages, styling, testing

---

## Week 4 Review


| Task                    | Person | Status                                                                                                          |
| ----------------------- | ------ | --------------------------------------------------------------------------------------------------------------- |
| Dashboard page          | Jamal  | ✅ Merged via jamal/dashboard-clean (#4). Shows modules and upcoming deadlines. Old branch had conflicts — fixed |
| Module detail page      | Dan    | Pushed directly to main. Added comments to views.py. Module list had a bug (title fallback) — now fixed ✅       |
| Grades page             | Owen   | Grades page works in main ✅                                                                                     |
| Login / Register + auth | Sam    | Will do this over the next week. Already done just needs to be pushed to main.                                  |
| Timetable page          | Tyr    | ✅ Merged via tyr/timetable-page (#5). Weekly grid, event cards, today panel, upcoming deadlines                 |
| Settings page           | Vitto  | Will be updated from him next week                                                                              |


---

## Notes

- **Use branches and PRs** — Dan pushed directly to main which caused a bug. Everyone should create a branch and do a Pull Request so changes get reviewed before merging.
- **Modules bug** — `module.title` doesn't exist on the Module model. Was causing a 500 error. Fixed by using `module.name` instead.

---

## Week 5 Tasks

---

### Jamal - Dashboard

**Your files:**

- View: `dashboard/views.py`
- Template: `templates/dashboard/dashboard.html`
- CSS: `static/css/style.css`

**What to do:**

1. Move any inline styles out of dashboard.html and into CSS classes in style.css
2. Add icons to the module cards so they match the mockup
3. Colour-code upcoming deadlines — red if due within 3 days, amber within 7
4. When you click on an upcoming deadline it should take you to that module's page

**Models you'll use:** `Module` (code, name, credits, students), `Assignment` (module, title, due_date)

---

### Dan - Modules

**Your files:**

- View: `modules/views.py`
- Templates: `templates/modules/module_list.html`, `templates/modules/module_detail.html`

**What to do:**

1. Make the module cards all the same size
2. On the detail page, show lecturer, credits, and semester at the top
3. Add a warning icon next to assignments that are due within 7 days, and remove the year from dates
4. Change the material bullet points to emojis (📄 slides, 🎥 recording, 📝 worksheet)
5. Make the materials section one big card instead of lots of small ones
6. **Use a branch and PR** — don't push directly to main

**Models you'll use:** `Module` (code, name, lecturer, credits, semester, students), `Assignment` (due_date), `Week`, `Material`

---

### Owen - Grades

**Your files:**

- View: `grades/views.py`
- Template: `templates/grades/grades.html`

**What to do:**

1. Add a hardcoded overview section at the top of the page showing: semester average, year average, degree classification, credits completed
2. Add dynamic degree weighting depending on course duration. Maybe add switch button in grades page? (e.g. 3-year course: years weighted 0/120/240, 4-year course - Masters: 0/120/240/240)

**Models you'll use:** `Grade` (student, assignment, score), `Assignment` (module, weight), `Module` (credits)

---

### Tyr - Sidebar + Database

**Your files:**

- Sidebar: `templates/base.html`, `static/css/style.css`
- Models / views / fixture: various — see below

**What to do:**

1. Make the views filter data by the logged-in user so each student only sees their own modules, grades, and timetable
2. Update the fixture with at least one working student account to test this
3. In the sidebar — remove the Settings text link and put a gear icon next to profile instead
4. Add icons to each sidebar nav item (Dashboard, Modules, Timetable, Grades, Notifications)
5. Add the university logo at the top of the sidebar

Sam builds on top of this — once the per-user filtering works, Sam adds login/register and the 3 test users.

---

### Sam - Login + Test Users

**Your files:**

- Views: `accounts/views.py`
- Templates: `templates/accounts/login.html`, `templates/accounts/register.html`
- Fixture: `fixtures/sample_data.json`

**What to do:**

1. Push the login/register code to a branch and create a PR
2. Build on Tyr's DB work — make sure the login/register flow creates a profile and works with per-user filtering
3. Add 3 test users to the fixture, each enrolled in different modules
4. Each user should also have timetable and grade data so every page shows something for them
5. Test the full flow: register → log in → see only your data → log out → redirected to login

**Models you'll use:** `User`, `UserProfile` (role, university, course, year_of_study), `Module` (students)

---

### Vitto - Settings

Carried over from last week. Refer to the detailed guide in `docs/week-4/week4-meeting.md` — Settings section. Same files and steps apply.