# Test Accounts

Use these to log in and test the app without registering.

| Name           | University Email       | Password       | Course              | Year |
|----------------|------------------------|----------------|---------------------|------|
| Test Student   | test@liverpool.ac.uk   | testpass123    | Computer Science BSc | 1    |
| Jane Smith     | jane@liverpool.ac.uk   | testpass123    | Computer Science MEng| 2    |

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
