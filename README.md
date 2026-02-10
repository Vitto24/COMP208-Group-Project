# Uni Tracker

University learning platform to replace Canvas. Django + SQLite + HTML/CSS.

COMP208 • Team 1 • 2026

---

## Quick Setup

**Mac / Linux:**
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Windows:**
```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

To load sample data: `python manage.py loaddata fixtures/sample_data.json`

Sample accounts (after loading fixture):
- **Student:** `jb` / `password123`
- **Admin panel** (`/admin`): `admin` / `password123`

---

## MVP

| Essential | Extra |
|-----------|-------|
| Login / Register / Logout | Timetable page |
| Dashboard (module cards, deadlines) | Notifications |
| Module detail page | Settings page |
| Grades page with averages | Lecturer / admin roles |
| Sidebar navigation | Assignment submission |
| Sample data (fixtures) | Marking + grade release |

MVP is read-only for students. Data is managed through Django's admin panel (`/admin`).

## Database

`python manage.py migrate` creates all tables. Don't commit `db.sqlite3`.

### UserProfile

| Field | What it stores |
|-------|----------------|
| **user** | Links to Django User (username, email, password) |
| **role** | student, lecturer, or admin |
| **university** | E.g. University of Liverpool |
| **course** | E.g. Computer Science |
| **year_of_study** | 1, 2, or 3 |

### Module

| Field | What it stores |
|-------|----------------|
| **code** | E.g. COMP202 (unique) |
| **name** | E.g. Complexity of Algorithms |
| **description** | Module description |
| **credits** | E.g. 15 or 7.5 |
| **lecturer** | E.g. Dr J. Smith |
| **semester** | 1 or 2 |
| **academic_year** | E.g. 2025/26 |
| **students** | Which students are enrolled (many-to-many) |

### Assignment

| Field | What it stores |
|-------|----------------|
| **module** | Which module this belongs to |
| **title** | E.g. Requirements Analysis |
| **weight** | Percentage, e.g. 12, 15, 30 |
| **type** | Coursework or exam |
| **due_date** | Deadline (blank if TBC) |

### Grade

| Field | What it stores |
|-------|----------------|
| **student** | Which student |
| **assignment** | Which assignment |
| **score** | Percentage mark (blank if not graded) |
| **status** | graded, submitted, or not_submitted |

### Week

| Field | What it stores |
|-------|----------------|
| **module** | Which module |
| **number** | Week number (1, 2, 3...) |
| **title** | E.g. Recurrences |

### Material

| Field | What it stores |
|-------|----------------|
| **week** | Which week this belongs to |
| **title** | E.g. Lecture Slides |
| **type** | slides, worksheet, recording, other |
| **url** | Link to the resource |
| **available** | True or false (false = 'Not yet available') |

### Relationships

```
User ——— UserProfile
  └── enrolled in ——— Module
                        ├── Assignment ——— Grade (per student)
                        └── Week ——— Material
```

---

## Repo Structure

```
uni_tracker/         Project settings
accounts/            Auth — login, register, logout, user profiles
modules/             Module detail, materials, week content
grades/              Grades, assignments, averages
dashboard/           Dashboard — pulls from modules + grades
templates/           Shared templates (base.html = sidebar + layout)
static/              CSS, JS, images
fixtures/            Sample data (JSON)
mockups/             Screenshots of what each page should look like
```

Each app has: `models.py` (database tables), `views.py` (logic), `urls.py` (routing), `templates/` (HTML).

---

## How to Build a Page

Each page has an empty view and an empty template. Your job is to fill them in.

### 1. Check the mockup

Look in `/mockups` for the screenshot of your page. Check the models in `models.py` to see what data is available.

### 2. Write the view

Your view already exists in `views.py` but it's empty. Add queries to get data and pass it to the template:

```python
from django.shortcuts import render
from modules.models import Module

def dashboard(request):
    modules = Module.objects.all()
    return render(request, 'dashboard/dashboard.html', {
        'modules': modules,
    })
```

### 3. Build the template

Your template already extends `base.html`. Replace the placeholder text with HTML + Django template tags:

```html
{% for module in modules %}
    <h3>{{ module.code }}: {{ module.name }}</h3>
    <p>{{ module.credits }} credits</p>
{% endfor %}
```

### 4. Push it

```bash
git checkout -b feature/your-page
git add .
git commit -m "dashboard page showing real data"
git push origin feature/your-page
```

Open a PR on GitHub and message the WhatsApp group.

---

## Git

Use branches. Don't commit to main directly.

```bash
git pull origin main                       # get latest
git checkout -b feature/your-task          # e.g. feature/grades-page
# ... work + commit ...
git push origin feature/your-task
```

Open a PR → message WhatsApp → someone merges it.
