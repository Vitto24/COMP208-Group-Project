# Week 6 — Meeting 6 (Fri 6 Mar)

**Attended:** Tyr, Owen, Jamal

---

## What's Working


| Page             | Status      | Notes                                                                     |
| ---------------- | ----------- | ------------------------------------------------------------------------- |
| Login / Register | Working     | Auth flow, per-user data isolation, `@login_required` on all views        |
| Dashboard        | Working     | Module cards, upcoming deadlines, colour-coded due dates, clickable cards |
| Modules          | Working     | Module list + detail page with assignments table and materials section    |
| Timetable        | Working     | Weekly grid, colour-coded events, today panel, week navigation            |
| Grades           | Working     | Nested by year/semester, expandable modules, weighted overall grade calc  |
| Settings         | Placeholder | Just renders "coming soon" — no actual functionality                      |
| Notifications    | Not built   | Sidebar link goes to `#`                                                  |


### Infrastructure

- Django project with 7 apps (accounts, dashboard, modules, grades, timetable, settings_page, uni_tracker)
- SQLite database with fixture data (`fixtures/sample_data.json`)
- Per-user filtering on all main views
- Sidebar with uni logo, nav icons, active page highlight, user avatar with initials
- Dynamic semester/week info in header
- 2 test users with different module enrolments

---

## Tasks — Week 6

### Dashboard (Jamal)

**Files:** `dashboard/views.py`, `templates/dashboard/dashboard.html`

- Fix dashboard deadline icons — keep emojis for now, switch to proper icons later (week 7).
- Add the timetable that is in the mockup to the dashboard. Use the existing timetable code as a starting base and adapt a simplified version for the dashboard:
  - `timetable/views.py`, `templates/timetable/timetable.html`, `timetable/models.py`, `timetable/utils.py`
- Make headers larger over the entire site for better readability.

### Grades (Owen)

**Files:** `grades/views.py`, `templates/grades/grades.html`

- Add the grade logic to calculate and display grades properly.
- Don't change the overview until the assignment grade is confirmed — if an assignment is upcoming or being marked, the grade shouldn't update.
- Only update the grade when the result is officially released. Use the `status` field on `Assignment` to check this.
- Make sure the status shows "Pending" or "Submitted" for assignments that haven't been graded yet.

**Models:** `Grade` (student, assignment, score), `Assignment` (module, title, due_date, weight, status)

### Database (Tyr)

**Files:** `dashboard/views.py` (for filtering), new scraper script

- Only show modules on the dashboard that the student is currently enrolled in — filter by current semester enrolment so past/future modules don't appear.
- Download different modules data using a Python script scraper — there are roughly 500 undergrad courses to collect.
- Connect the database up to an online server (week 7/8).

### Settings (Vitto)

**Files:** `settings_page/views.py`, `templates/settings_page/settings.html`

- Finish the settings page — currently just a placeholder ("coming soon").
- Connect the student name to the settings page so the user can view and edit their profile details.
- Display fields from `UserProfile`: name, course, year of study, university.

### Modules (Daniel)

**Files:** `modules/views.py`, `templates/modules/module_list.html`

- On the modules page, separate current and past modules with clear headers:
  - Add a **"Current Modules"** header, then show module cards for this semester below it.
  - Add a **"Previous Modules"** header below that, with past module cards underneath.
- Students should see what's relevant first — current modules at the top.

### Login (Sam)

**Files:** `accounts/views.py`, `templates/accounts/`

- Add forgot / reset password feature (password reset email flow).
- Once registered, the user should be automatically logged in — log them in and redirect to dashboard after successful registration.

### Optional

- Hide the sidebar whilst logging in / registering (Login).
- Add a password show/hide toggle (Login).
- Require username, email, and course on registration (Login).
- Update module card design to match dashboard (Modules).
- Move notification bell to header with notification count (Notifications).

### Project Presentation (Week 8+) (Everyone)

- Record the video.
- Make sure we can explain each main function with diagrams (e.g. flow charts).

---

## Reminders

- **Use branches and PRs** — Don't push directly to main
- **Demo + Video due 20 Apr** — 6 weeks away. Aim to be feature-complete by early April so we have time to polish and record
- **Written deliverables due 11 May** — Start drafting the design doc alongside coding, don't leave it all to the end

