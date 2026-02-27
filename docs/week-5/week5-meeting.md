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

**Assign in meeting:**


| Task           | Person | Notes                                                                                                                                                                                                                                                                                                                                                       |
| -------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dashboard Page | Jamal  | - Add icons to modules as shown in mockup image- Add due soon and colours - Transport to module assignment page when clicking upcoming deadlines                                                                                                                                                                                                           |
| Module Page    | Dan    | - Connect student account to show current semester modules- Standardised size for module blocks, maybe add image- Top line of module info: Lecturer, credits, semester- Add warning sign for assignments due soon, remove year from date- Clean up hyperlinks, change bullet points to emojis- Make materials one large card rather than separate ones |
| Grades Page    | Owen   | - Hardcode overview section temporarily at top of the page- Dynamic degree weighting depending on course duration                                                                                                                                                                                                                                          |
| Sidebar        | Tyr    | - Remove from sidebar and add as a settings icon next to profile- Add icons to the sidebar- Add the university logo to the sidebar - able to edit as admin- With django, set up individual student accounts within database and the modules/grades according to them - Consider adding a variable assignment due soon time frame (Due 3 days) etc         |
| Extra          | Sam    | - Complete Login page. - Add 3 test users (make sure each user has different modules)                                                                                                                                                                                                                                                                      |
| Settings       | Vitto  | Carry this over to next week.                                                                                                                                                                                                                                                                                                                               |


