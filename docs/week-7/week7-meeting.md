# Week 7 — Meeting 7 (Fri 13 Mar)


## Review — Week 6 Tasks


| Task | Owner | Status | Notes |
| ---- | ----- | ------ | ----- |
|      |       |        |       |
|      |       |        |       |
|      |       |        |       |
|      |       |        |       |
|      |       |        |       |
|      |       |        |       |

---

## Online Hosting / Database

We need to get the app online before the demo. Here are the options we looked at:

### Option 1: PythonAnywhere (Recommended)

- **Free**, no credit card needed
- Designed for students hosting Django apps
- Web UI setup — no CLI tools or Docker needed
- Gives us a URL like `ourname.pythonanywhere.com`
- Comes with a free MySQL database
- Can be set up in under an hour
- HTTPS included

### Option 2: Render

- Free tier, no credit card needed
- Free PostgreSQL database (lasts 90 days — covers us through the demo and written deliverables)
- Auto-deploys from GitHub (push to main = site updates automatically)
- Downside: free tier sleeps after 15 min of no activity (takes ~30s to wake up)

### Option 3: Railway

- Auto-deploys from GitHub like Render
- Free PostgreSQL with $5 trial credit
- Needs a credit card to sign up
- Modern and clean dashboard

### What We Need to Change (Any Option)

No matter which platform we pick, we need to update:

- **`settings.py`** — move SECRET_KEY to an environment variable, set DEBUG=False, add ALLOWED_HOSTS, switch database config from SQLite to MySQL/PostgreSQL, add STATIC_ROOT, add whitenoise middleware
- **`requirements.txt`** — add gunicorn, whitenoise, dj-database-url, and the database driver (mysqlclient or psycopg2-binary)

## Tasks — Week 7

| Task | Owner | Status | Notes |
| ---- | ----- | ------ | ----- |
|      |       |        |       |
|      |       |        |       |
|      |       |        |       |
|      |       |        |       |
|      |       |        |       |
|      |       |        |       |

---

## Reminders

- **Use branches and PRs** — Don't push directly to main
- **Demo + Video due 20 Apr** — 5 weeks away
- **Written deliverables due 11 May**

