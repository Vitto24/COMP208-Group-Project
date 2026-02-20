# Week 4 — Meeting 4 (Fri 20 Feb)

---

## Agenda

1. **Week 3 review** — each person shows what they've done
2. **Set up git branches** — everyone creates their branch following the workflow guide
3. **Pick week 4 tasks** — timetable, styling, module page, fixture data, bug fixes

---

## Week 3 Review

Go around the table. Each person shows their page running in the browser.


| Task                             | Person | Status                                                                                                             |
| -------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------ |
| Dashboard page                   | Jamal  | Got the project on your laptop. Need to put the dashboard code onto jamal/dashboard-page branch.                   |
| Module detail page               | Dan    | Dan isn't here so we will wait to next meeting                                                                     |
| Grades page                      | Owen   | Have grade logic for all modules. Need to connect the code to the owen/grades-page branch. Then do a Pull Request. |
| Login / Register + auth          | Sam    | Need to link branch sam/login-register to github. Go through docs/week3-meeting.md for the Login/Register Section  |
| Gather module data               | Tyr    | ✅ Created a branch. Submitted a Pull Request                                                                       |
| Requirements Analysis submission | Vitto  | ✅ Submitted the requirements on canvas                                                                             |


If a task isn't finished, it carries over to this week. Note any blockers.

---

## Set Up Your Git Branch

Everyone creates their own branch in the meeting. Follow the guide: `docs/week-4/git-workflow.md`

1. Make sure you're on main and up to date:
  ```bash
   git checkout main
   git pull
  ```
2. Create your branch:
  ```bash
   git checkout -b your-name/your-task
  ```
   For example: `alex/dashboard-page`, `sam/grades-styling`, `jordan/timetable`
3. Confirm you're on the right branch:
  ```bash
   git status
  ```

Once everyone has their branch, pick a task from the list below and start working.

---

## Week 4


| Task                             | Person | Status                                        |
| -------------------------------- | ------ | --------------------------------------------- |
| Dashboard page                   | Jamal  | Continue Week 3                               |
| Module detail page               | Dan    | Continue Week 3                               |
| Grades page                      | Owen   | Continue Week 3                               |
| Login / Register + auth          | Sam    | Continue Week 3                               |
| Gather module data               | Tyr    | Complete Timetables                           |
| Requirements Analysis submission | Vitto  | Complete Settings. Can refer to week3-meeting |


## Timetables

Copy the timetable in the dashboard UI Mockup

## Settings

- Need to make a new settings template. Refer to week3-meeting.md

- Profile Information
  - Course Name (Computer Science)
  - University (Liverpool)
  - Year (Year 2)
  - Name
  - Student Email
  - Profile Picture
- Light/Dark Mode
- Change nickname
- Font size
- Notifications - On/Off (button)

