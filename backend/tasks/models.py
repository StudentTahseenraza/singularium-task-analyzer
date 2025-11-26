from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)  # Allow null for tasks without due dates
    estimated_hours = models.FloatField(
        validators=[MinValueValidator(0.1)],  # At least 0.1 hours
        help_text="Estimated time to complete in hours"
    )
    importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],  # 1-10 scale
        help_text="Importance on a scale of 1-10"
    )
    dependencies = models.JSONField(
        default=list,
        blank=True,
        help_text="List of task IDs that this task depends on"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']