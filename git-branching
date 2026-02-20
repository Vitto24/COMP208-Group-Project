# Git Workflow Guide

Step-by-step guide for working on features using branches and pull requests.

---

## Branch Naming

Always create a branch for your work. Never commit directly to `main`.

Format: `your-name/feature-name`

Examples:
- `tyr/module-data`
- `alex/dashboard-page`
- `sam/grades-styling`
- `jordan/timetable`

---

## Step-by-Step: Working on a Feature

### 1. Make sure you're on main and up to date

```bash
git checkout main
git pull
```

### 2. Create your branch

```bash
git checkout -b your-name/feature-name
```

This creates a new branch AND switches to it. You're now on your own branch.

### 3. Check you're on the right branch

```bash
git status
```

You should see: `On branch your-name/feature-name`

### 4. Do your work

Edit files, add code, test it locally. Work as normal.

### 5. Stage your changes

```bash
git add file1.py file2.html
```

Or to stage everything you changed:

```bash
git add .
```

### 6. Commit

```bash
git commit -m "Short description of what you did"
```

Good commit messages:
- `Add dashboard page with module cards and deadlines`
- `Style grades page to match mockup`
- `Fix login redirect after registration`

Bad commit messages:
- `update`
- `stuff`
- `fixed it`

### 7. Push your branch

First time pushing this branch:

```bash
git push -u origin your-name/feature-name
```

After that, just:

```bash
git push
```

### 8. Create a Pull Request on GitHub

1. Go to the repo on GitHub
2. You'll see a yellow banner saying "your-name/feature-name had recent pushes" — click **Compare & pull request**
3. Or go to the **Pull requests** tab → **New pull request**
4. Set base: `main` ← compare: `your-name/feature-name`
5. Write a short title and description of what you did
6. Click **Create pull request**
7. Let someone know in the group chat so they can review it

### 9. After the PR is merged

Switch back to main and pull the latest:

```bash
git checkout main
git pull
```

Then create a new branch for your next task.

---

## Common Situations

### "I need someone else's changes"

If someone merged a PR and you need their changes on your branch:

```bash
git checkout main
git pull
git checkout your-name/feature-name
git merge main
```

This brings main's latest changes into your branch.

### "I'm on the wrong branch"

Check which branch you're on:

```bash
git branch
```

The one with `*` is your current branch. Switch with:

```bash
git checkout branch-name
```

### "I made changes on main by accident"

If you haven't committed yet:

```bash
git stash
git checkout -b your-name/feature-name
git stash pop
```

This saves your changes, creates a branch, then puts them back.

### "I get a merge conflict"

This happens when two people edited the same lines. Git will show something like:

```
<<<<<<< HEAD
your version of the code
=======
their version of the code
>>>>>>> main
```

Pick which version to keep (or combine them), delete the `<<<<<<<`, `=======`, `>>>>>>>` markers, then:

```bash
git add the-file-you-fixed
git commit -m "Resolve merge conflict in the-file"
```

If you're stuck, ask in the group chat.

---

## Quick Reference

| What | Command |
| ---- | ------- |
| Check current branch | `git status` or `git branch` |
| Switch to main | `git checkout main` |
| Pull latest | `git pull` |
| Create new branch | `git checkout -b your-name/feature` |
| Stage files | `git add file1 file2` or `git add .` |
| Commit | `git commit -m "message"` |
| Push (first time) | `git push -u origin your-name/feature` |
| Push (after first time) | `git push` |
| See what you changed | `git diff` |
| See commit history | `git log --oneline` |
