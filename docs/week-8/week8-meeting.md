# Week 8 — Meeting 8 (Fri 20 Mar)

**Location:** Harold Cohen Library, Lower Ground Floor — Group Study Table 1
**Time:** 1:00 pm – 2:30 pm
**Chair:** Samuel Garwood | **Secretary:** Owen Wells
**Present:** Tyr Bujac, Samuel Garwood, Owen Wells
**Absent:** Connor Holdcroft, Vittorio Gastaldi (ill), Daniel Greslow (holiday), Jamal Ahmed

---

## Demo Documentation Deadline

The next meeting is provisionally set for **2:00 pm, 14th April** to plan and prepare the presentation.

**Demo Documentation (15%) — Due 20th April**

One submission per team. All documents must list contributing team members. Four separate submissions (no zips):

1. Video demonstration
2. Copy of slides used in the video presentation
3. One-page document with details on how to access and run the code (code and deployed system must remain permanently available to markers). Web apps should be live and accessible.
4. User manuals for all user types — install, setup, and usage instructions

---

## Tasks — Week 8

### Dashboard (Tyr)

- ✅ Only show modules the student has chosen (not all modules for the semester/year)
- ✅ Fix empty Upcoming Deadlines for some courses
- ✅ Create random timetable data
- ✅ Create random deadline data
- ✅ Create random assignment grades (scrape assessment names and weightings from TULIP)
- ✅ Add timetable section at the bottom of the Dashboard page

### Modules

- Use the same card style as Dashboard module cards
- Current modules at the top under "Current Modules" header
- Under "Previous Modules", add dropdowns per semester/year in reverse chronology
- In /modules/Course_Code/ add assignment details (name, type, weighting, student grade)
- Add "Year X" label to the left of the semester info at the top of Course_Code page
- Possibly add randomised material data under Materials header
- ✅ Only show modules the student has chosen

### Timetable

- ✅ Fix timetable events not showing
- ✅ Create random timetable data for every module/course
- ✅ Fix empty Upcoming Deadlines (same issue as Dashboard)
- Optional: dropdown to switch between Semester 1 and 2 timetable

### Grades (Owen)

- Fix assignment grade dropdowns not appearing outside of CS Year 2
- Previous Years section should show semesters in reverse chronology
- Test that Grades Overview logic boxes work properly (Semester Avg, Degree Projection %, Credits Completed)
- Fix modules showing "Avg: 0%" — need randomised assignment data in student DB

### Notifications (Sam)

- Remove notifications from the sidebar entirely (feature cut due to time)

### Settings (Sam + Vitto)

- Add Student ID field (auto-generated on account creation, not editable by student)
- Add change password option (Sam)
- Add other universities in signup (e.g. John Moores) and update sidebar logo/link accordingly
- Add Undergraduate/Postgraduate option in student profile

### Admin Pages

- Admin view for teachers/lecturers/staff to add/edit modules and grade assignments (after Easter)

### Live Hosting (Tyr)

- Host the GitHub main branch on [https://student.csc.liv.ac.uk/~sgtbujac/](https://student.csc.liv.ac.uk/~sgtbujac/)

