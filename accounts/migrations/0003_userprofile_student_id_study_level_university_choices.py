import uuid

from django.db import migrations, models


def generate_student_ids(apps, schema_editor):
    UserProfile = apps.get_model('accounts', 'UserProfile')
    used = set(
        UserProfile.objects.exclude(student_id='').values_list('student_id', flat=True)
    )
    for profile in UserProfile.objects.filter(student_id=''):
        while True:
            candidate = '2' + str(uuid.uuid4().int)[:7]
            if candidate not in used:
                used.add(candidate)
                break
        profile.student_id = candidate
        profile.save(update_fields=['student_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_userprofile_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='university',
            field=models.CharField(
                max_length=50,
                choices=[
                    ('uol', 'University of Liverpool'),
                    ('ljmu', 'Liverpool John Moores University'),
                    ('chester', 'University of Chester'),
                    ('edge_hill', 'Edge Hill University'),
                ],
                default='uol',
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='study_level',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('undergraduate', 'Undergraduate'),
                    ('postgraduate', 'Postgraduate'),
                ],
                default='undergraduate',
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='student_id',
            field=models.CharField(max_length=10, blank=True, default=''),
        ),
        migrations.RunPython(generate_student_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='userprofile',
            name='student_id',
            field=models.CharField(max_length=10, unique=True, blank=True),
        ),
    ]
