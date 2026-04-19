# Week 3 — Meeting 3 (Fri 13 Feb)

---

## Agenda

1. **Requirements Analysis** — assign someone to polish and submit on Canvas before deadline
2. **Walk through the repo** — folder structure, how Django works, run the server
3. **Live demo** — build a tiny feature in 2 mins to show how views + templates work
4. **Everyone clones the repo and runs it**
5. **Pick tasks** — each person picks a page or task below

---

## Requirements Analysis

- [ ] Assign someone to proofread and polish the document
- [ ] Check all 7 names are in the document (anyone missing = 0 mark)
- [ ] That person submits on Canvas
- [ ] Deadline: Sun 16 Feb (noon) — 7-day grace period until 23 Feb

---

## What's already set up

The repo has all the infrastructure ready. You don't need to touch any of this:

- **Models** — all database tables are defined (`modules/models.py`, `grades/models.py`, `accounts/models.py`)
- **URLs** — all routes are wired up (`/`, `/modules/<code>/`, `/grades/`, `/accounts/login/`, `/accounts/register/`)
- **Base template** — sidebar + layout (`templates/base.html`, `static/css/style.css`)
- **Sample data** — fixture with modules, assignments, weeks, materials, grades (`fixtures/sample_data.json`)
- **Auth** — login, register, and logout pages already work

The page views and templates are **empty placeholders**. That's your job.

---

## Live Demo (2 mins)

Show the team how a view + template works by making the module list page display real data. Do this live in the meeting.

**Step 1 — Open `modules/views.py` and change `module_list` to:**

```python
from django.shortcuts import render
from .models import Module  # import the Module model so we can query the database

def module_list(request):
    modules = Module.objects.all()  # get every module from the database
    return render(request, 'modules/module_list.html', {
        'modules': modules,  # pass the modules to the template as a variable called 'modules'
    })
```

**Step 2 — Open `templates/modules/module_list.html` and replace the content block:**

```html
{% block content %}                          {# start of the page content area #}
{% for module in modules %}                  {# loop over each module passed from the view #}
    <h3>{{ module.code }}: {{ module.name }}</h3>   {# display the module code and name #}
    <p>{{ module.credits }} credits · {{ module.lecturer }}</p>  {# display credits and lecturer #}
{% endfor %}                                 {# end of the loop #}
{% endblock %}
```

**Step 3 — Refresh `/modules/` in the browser.** Module data appears.

That's it. Every page works the same way: query in the view, loop in the template. Then revert these changes before pushing.

---

## Pages

Each person owns a page. Your job is to:

1. Open the mockup in `/mockups` to see what it should look like
2. Write queries in your view (`views.py`) to get data from the database
3. Build the HTML in your template to display that data
4. Don't worry about CSS — just use basic HTML (tables, lists, headings)

---

### Dashboard (`/`)

**Your files:**
- View: `dashboard/views.py`
- Template: `templates/dashboard/dashboard.html`
- Mockup: `mockups/dashboard.png`

**What to do:**

1. In the view, import `Module` from `modules.models` and `Assignment` from `grades.models`
2. Query all modules and all assignments, pass them to the template
3. In the template, loop through modules and display a card for each one (code, name, credits)
4. Loop through assignments and display a deadline row for each one (module code, title, due date)
5. Order deadlines by due date (closest first)
6. If an assignment is due within 3 days, show a "Due soon" badge or warning icon

**Models you'll use:** `Module` (code, name, credits), `Assignment` (module, title, due_date)

---

### Module Detail (`/modules/COMP202/`)

**Your files:**
- View: `modules/views.py` → `module_detail` function
- Template: `templates/modules/module_detail.html`
- Mockup: `mockups/module-details.png`

**What to do:**

1. In the view, import `Module`, `Week` from `modules.models` and `Assignment` from `grades.models`
2. Get the module by its code (it's passed in as the `code` parameter)
3. Get all assignments for that module, and all weeks with their materials
4. Pass everything to the template
5. In the template, show module info (code, name, lecturer, credits, description)
6. Show assignments in a table (title, weight %, type, due date)
7. Show materials grouped by week — each week has a title and a list of materials

**Models you'll use:** `Module`, `Assignment` (filtered by module), `Week` (filtered by module), `Material` (accessed via `week.materials.all`)

---

### Grades (`/grades/`)

**Your files:**
- View: `grades/views.py`
- Template: `templates/grades/grades.html`
- Mockup: `mockups/grades.png`

**What to do:**

1. In the view, import `Assignment`, `Grade` from `grades.models` and `Module` from `modules.models`
2. Get all assignments and grades, pass them to the template
3. In the template, show an overview section: semester average, year average, degree projection, credits completed
4. Show assignment grades grouped by module — each module's assignments with title, weight %, type, score, status, due date
5. Calculate the weighted average for each module (sum of score * weight / sum of weights for graded assignments)
6. Calculate overall averages across modules

**Models you'll use:** `Assignment` (module, title, weight, type, due_date), `Grade` (student, assignment, score, status), `Module` (code, name, credits)

This is the hardest page because of the averages calculation.

---

### Login / Register (`/accounts/login/`, `/accounts/register/`)

**Your files:**
- Views: `accounts/views.py`
- Templates: `templates/accounts/login.html`, `templates/accounts/register.html`
- URL config: `accounts/urls.py`

**What's already working:** Login, register, and logout pages all work. You can log in with `jb` / `password123` right now.

**What to do:**

1. Add `@login_required` decorator to the dashboard, module detail, and grades views so only logged-in users can access them (import from `django.contrib.auth.decorators`)
2. Update the other views to filter data by `request.user` instead of showing everything (e.g. only show modules the student is enrolled in)
3. Test the full flow: register a new account → log in → see data → log out → get redirected to login

**Docs:** [Django authentication](https://docs.djangoproject.com/en/5.1/topics/auth/default/)

---

### Gather Module Data + Create Fixture

Not a coding task. Go through Canvas and record the real module data.

**Your file:** `fixtures/sample_data.json`

**Which modules:** COMP201 (Semester 1), COMP207 (Semester 1), COMP202 (Semester 2), COMP208 (Semester 2). COMP202 and COMP208 are already partially done — the rest need filling in.

**What to record for each module:**

- Module info: code, name, description, credits, lecturer, semester
- Assignments: title, weight %, type (coursework/exam), due date
- Weeks: number and title (e.g. "Week 1 — Introduction & Module Overview")
- Materials: title and type (slides, worksheet, recording) for each week

**How to add it:** The fixture is a JSON file. Each entry has a model name, a pk (number), and fields. Here's an example:

```json
{
    "model": "modules.module",
    "pk": 6,
    "fields": {
        "code": "COMP201",
        "name": "Software Engineering I",
        "credits": "15.0",
        "lecturer": "Dr Someone",
        "semester": 1,
        "academic_year": "2025/26",
        "students": [1]
    }
}
```

Look at the existing entries in the file for examples of assignments, weeks, and materials. Make sure each new entry has a unique `pk` (just use the next number).

---

## Task Summary

| Task | People |
|------|--------|
| Finalise + submit Requirements Analysis | 1 |
| Dashboard page | 1 |
| Module detail page | 1 |
| Grades page | 1 |
| Login / Register + auth | 1 |
| Gather module data | 1 |
