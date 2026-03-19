from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    """A degree programme like 'Computer Science BSc'."""
    DEGREE_CHOICES = [
        ('BSc', 'BSc'),
        ('MEng', 'MEng'),
        ('MSc', 'MSc'),
        ('BA', 'BA'),
        ('BEng', 'BEng'),
        ('LLB', 'LLB'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)  # e.g. "computer-science-bsc"
    url = models.URLField(blank=True)
    degree_level = models.CharField(max_length=10, choices=DEGREE_CHOICES)

    # Added to get weights for the grades page when needed, defaults should ensure no problems
    year_1_weight = models.IntegerField(default=0)
    year_2_weight = models.IntegerField(default=30)
    year_3_weight = models.IntegerField(default=70)
    
    def __str__(self):
        return self.name


class ModuleCourse(models.Model):
    """Links a module to a course, with year level and compulsory status."""
    module = models.ForeignKey('Module', on_delete=models.CASCADE, related_name='module_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='module_courses')
    year = models.CharField(max_length=10)  # "1", "2", "3", "S1", "S2", "FP" etc.
    is_compulsory = models.BooleanField(default=False)

    class Meta:
        unique_together = ('module', 'course')

    def __str__(self):
        status = "compulsory" if self.is_compulsory else "optional"
        return f"{self.module.code} in {self.course.slug} (year {self.year}, {status})"


class Module(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.DecimalField(max_digits=4, decimal_places=1)
    lecturer = models.CharField(max_length=200, blank=True)
    semester = models.IntegerField(default=1)
    academic_year = models.CharField(max_length=10, default='2025/26')
    department = models.CharField(max_length=200, blank=True)
    year = models.IntegerField(default=2)
    students = models.ManyToManyField(User, related_name='enrolled_modules', blank=True)

    def __str__(self):
        return f"{self.code}: {self.name}"


class Week(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='weeks')
    number = models.IntegerField()
    title = models.CharField(max_length=200)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"{self.module.code} — Week {self.number}: {self.title}"


class Material(models.Model):
    TYPE_CHOICES = [
        ('slides', 'Slides'),
        ('worksheet', 'Worksheet'),
        ('recording', 'Recording'),
        ('other', 'Other'),
    ]

    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    url = models.URLField(blank=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.type})"
