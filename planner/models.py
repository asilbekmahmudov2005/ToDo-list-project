from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = 'low', 'Past'
        MEDIUM = 'medium', 'O‘rta'
        HIGH = 'high', 'Yuqori'

    class Category(models.TextChoices):
        STUDY = 'study', 'O‘qish'
        WORK = 'work', 'Ish'
        PERSONAL = 'personal', 'Shaxsiy'
        HEALTH = 'health', 'Sog‘liq'
        OTHER = 'other', 'Boshqa'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Foydalanuvchi"
    )
    title = models.CharField(max_length=255, verbose_name="Vazifa nomi")
    description = models.TextField(blank=True, verbose_name="Vazifa tavsifi")
    date = models.DateField(default=timezone.now, verbose_name="Sana")
    start_time = models.TimeField(null=True, blank=True, verbose_name="Boshlanish vaqti")
    end_time = models.TimeField(null=True, blank=True, verbose_name="Tugash vaqti")
    duration = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Davomiyligi (daqiqalarda)", 
        verbose_name="Davomiyligi (daqiqa)"
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Muhimlik darajasi"
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.PERSONAL,
        verbose_name="Kategoriya"
    )
    is_completed = models.BooleanField(default=False, verbose_name="Bajarilgan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")

    class Meta:
        ordering = ['date', 'start_time', '-priority', '-created_at']
        verbose_name = "Vazifa"
        verbose_name_plural = "Vazifalar"

    def __str__(self):
        return self.title

    @property
    def status_label(self):
        return "Bajarilgan" if self.is_completed else "Bajarilmagan"
