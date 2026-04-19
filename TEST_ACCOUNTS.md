# Test Accounts

Live demo: https://unitracker.pythonanywhere.com/

Use these to log in and test the app without registering.

| Name           | University Email         | Password         | Course                | Year | Role              |
|----------------|--------------------------|------------------|-----------------------|------|-------------------|
| Demo (passing) | demo.pass@liverpool.ac.uk| uol-demo-2026    | Computer Science BSc  | 2    | Student           |
| Demo (late)    | demo.late@liverpool.ac.uk| uol-demo-2026    | Computer Science BSc  | 2    | Student           |
| Test Student   | test@liverpool.ac.uk     | testpass123      | Computer Science BSc  | 1    | Student           |
| Jane Smith     | jane@liverpool.ac.uk     | testpass123      | Computer Science MEng | 2    | Student           |
| Admin          | admin@liverpool.ac.uk    | adminpass123     | —                     | —    | Staff (superuser) |

The two **Demo** accounts are seeded automatically by `python manage.py generate_sample_data`:
- `demo.pass` — all caught up, ~70% average — good state for the happy-path walk-through.
- `demo.late` — several Missing assignments, ~50% average — shows the warning pills and lower degree projection.

## How to create them

Run the app, go to `/accounts/register/`, and register with the details above.
Or load them via the Django shell:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from accounts.models import UserProfile
from modules.models import Course

user = User.objects.create_user(
    username='test',
    email='test@liverpool.ac.uk',
    password='testpass123',
    first_name='Test',
    last_name='Student',
)
profile = UserProfile.objects.get(user=user)
profile.course = Course.objects.get(name__icontains='Computer Science BSc')
profile.year_of_study = 1
profile.save()
```
