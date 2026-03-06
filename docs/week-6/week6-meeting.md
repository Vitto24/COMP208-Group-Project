# Week 6 — Meeting 6 (Fri 6 Mar)

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

## What We're Waiting On


| Item                    | Person | Details                                                                                                                                            |
| ----------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Settings page           | Vitto  | Carried over from week 4. Needs to actually let users view/edit their profile (name, course, year, university). `UserProfile` model already exists |
| Sam's login/register PR | Sam    | Was marked as "done, just needs pushing" in week 5. Needs to be merged so we can confirm multi-user flow works end-to-end                          |
| Owen's grades overview  | Owen   | Week 5 task was to add overview section (semester avg, year avg, classification, credits). Check if this made it into the merged PR                |


---

## What to Work On — Next 1-2 Weeks

### Ideas

- **Scrape Module data. There is roughly 500 Undergrad Courses. Can we download the module data using a python script scraper?**
- Have student choose the modules to do.
- In future could set up so 'Uni Tracker' works for other UK universities.
- Add some JavaScript animations
- Connect the database up to online server. Also host the website online. 
  -   - PythonAnywhere — Easiest for Django. Free tier gives you one web app at
      [yourusername.pythonanywhere.com](http://yourusername.pythonanywhere.com), 512MB storage, SQLite works out of the box. Probably your best bet for
      a uni project demo.
      - Railway — Free trial with $5 credit (no card needed). Supports Django + Postgres. Gives you a public
      URL. Credit runs out eventually but should last through your demo.
      - Render — Free tier for web services. Spins down after inactivity (cold starts take ~30s), but fine for
       a demo. Supports Django + Postgres.
      - [Fly.io](http://Fly.io) — Free tier with small VMs. Slightly more setup but very capable.

---

## Reminders

- **Use branches and PRs** — Don't push directly to main
- **Demo + Video due 20 Apr** — 6 weeks away. Aim to be feature-complete by early April so we have time to polish and record
- **Written deliverables due 11 May** — Start drafting the design doc alongside coding, don't leave it all to the end

