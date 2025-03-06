from django.db import models


class WorkDay(models.Model):
    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
    ]
    
    day = models.CharField(max_length=3, choices=DAY_CHOICES, unique=True)

    def __str__(self):
        return self.get_day_display()

class TrailerSelection(models.Model):
    day = models.OneToOneField(WorkDay, on_delete=models.CASCADE)  # Ensure one record per WorkDay
    coffee_percentage = models.FloatField(default=0.0)
    milkshake_percentage = models.FloatField(default=0.0)
    trailers_count = models.IntegerField(default=0)
    trailers_with_coffee = models.IntegerField(default=0)
    is_bank_holiday = models.BooleanField(default=False)
    has_coffee_machine = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.day}: {self.coffee_percentage}% coffee, {self.milkshake_percentage}% milkshake"
