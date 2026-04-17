# Week 9 — Meeting 9 (Fri 17 Apr)

**Location:** Harold Cohen Library
**Time:** 1:00 pm
**Present:** Tyr, Sam, Owen, Jamal, Dan, Vitto
**Absent:**

First meeting back post-Easter.

**Hard deadlines this week:**
- Mon 20 Apr — all 4 demo items submitted on Canvas
- ASAP — **email project assessor to book the Q&A / presentation slot** (window 20–24 Apr, all team must attend)

---

## Demo — 4 things to submit (uploaded separately)

1. **Video** (≤10 min, pre-recorded)
2. **Slides** used in the video
3. **One-page access doc** — dev-focused, tells markers how to run the code locally + the live URL. Basically a trimmed README; mostly written already.
4. **User manuals** — end-user focused, task-oriented ("Click Register", screenshots). One combined Google Doc with two sections: **Student** (register, dashboard, modules, grades, timetable) + **Admin** (using `/admin` to add modules, set grades). Whoever built a page writes the section for it.

> Items 3 and 4 are different: item 3 is for developers/markers running the code, item 4 is for end users. Can't merge them.

---

## Open Work

- **PR #15** (Owen, grades page) — open since 6 Apr, needs merge or close.
- **Sam** — `sam/account-updates` pushed (Student ID, uni select, password change, notifications removed). Needs PR.
- Modules page revamp, grades follow-ups, admin/lecturer view — decide what to cut.
- Live hosting on `student.csc.liv.ac.uk/~sgtbujac/` (Tyr) — blocker for item 3.

---

## Live hosting — options

Original plan was `student.csc.liv.ac.uk/~sgtbujac/`. Might not support Django out of box. Options if we need a fallback:

| Option | Free? | DB | Sleeps? | Setup |
|--------|-------|-----|---------|-------|
| **PythonAnywhere** (recommended) | yes, no card | keeps SQLite | no | <1hr, web UI |
| UoL student server | yes, on-domain | SQLite if supported | no | unknown — test first |
| Render | yes | forces Postgres migration | **yes, 30s cold start** | medium |
| Railway | needs card | Postgres | no | medium |

**Recommendation:** PythonAnywhere as primary (`tyrbujac.pythonanywhere.com`). Try UoL server for 15 min tomorrow; if it works, use both. Deploy by Sunday evening.

---

## Proposals (Tyr)

- **Slides:** Google Slides — shared link, everyone can edit, no file-passing.
- **Submission:** I'll handle all 4 Canvas uploads myself so we don't depend on who turns up Monday.
- **Recording tool:** Canvas Studio is what the brief recommends. QuickTime/OBS + upload to Canvas Studio also works. Pick one upfront so nobody records in a format that won't import.

## Agenda

1. Attendance + apologies
2. Demo plan — video storyboard, who talks about what, slides (Google Slides?), recording tool pick, recording slot (before Sun)
3. Live hosting — is it up? If not, fallback plan
4. What to cut — merge #15? drop modules revamp / admin view?
5. Email the project assessor to book the Q&A slot — agree who sends it, when, and collect everyone's availability 20–24 Apr
6. Who's doing what before Monday

---

## Backlog — bite-size tasks (1–2 hrs each)

Pick any of these over the weekend / next week. No owners yet — claim in the meeting.

**Demo video prep**
- Write 1–2 slides for a single section (intro, dashboard, modules, grades, timetable, scraper, closing)
- Record a screen capture of one feature (e.g. register → dashboard walkthrough)
- Draft voiceover notes for one section of the video
- Time a practice run-through and flag anything over 10 min

**User manuals (Google Doc)**
- Write the Student manual section for one page (dashboard / modules / grades / timetable / register)
- Write the Admin manual section (using `/admin` to add a module + mark an assignment)
- Take 3–5 annotated screenshots for one manual section

**One-page access doc**
- Trim `README.md` down to one page covering: live URL, test login, how to run locally, sample data commands

**Code — small fixes still open from week 8**
- Grades: fix modules showing "Avg: 0%" when no assignments seeded
- Grades: fix assignment dropdowns outside CS Year 2
- Grades: reverse-chronology order in Previous Years dropdowns
- Grades: smoke-test overview boxes (Semester Avg, Degree Projection %, Credits Completed)
- Modules: match dashboard card style on the modules list
- Modules: "Current Modules" vs "Previous Modules" split with per-semester dropdowns
- Module detail: add Year X label next to semester info
- Module detail: inline assignment table (name, type, weight, student grade)
- Settings: add Undergrad/Postgrad toggle
- Clone the repo from scratch on a different machine and walk through the README — fix anything that breaks

**Reviews / housekeeping**
- Review + merge or close PR #15 (grades)
- Open a PR for `sam/account-updates` and review it
- Commit `docs/diagrams/` so the team can see them

**Portfolio groundwork (can start, due ~11 May)**
- Compile all `docs/week-*/weekN-meeting.md` into a single Team Activity Record doc
- Start personal contribution notes (for the individual 20% submission) — what you built, what you learned
- Capture 1–2 design decisions from memory with the *why* written down

---

## Action Items

| Who | What | By when |
|-----|------|---------|
|     |      |         |
|     |      |         |

---

## Next Meeting

Date/time:
