from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_userprofile_course'),
    ]

    operations = [
        # Change university field: shorter max_length + choices
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
        # Add study_level field
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
        # Add student_id field
        migrations.AddField(
            model_name='userprofile',
            name='student_id',
            field=models.CharField(max_length=10, unique=True, blank=True, default=''),
            preserve_default=False,
        ),
    ]
