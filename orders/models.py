from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_choices = [('water', 'Water'), ('oil', 'Cooking Oil')]
    product = models.CharField(max_length=10, choices=product_choices)
    quantity = models.IntegerField()
    location = models.CharField(max_length=255)
    status_choices = [('pending', 'Pending'), ('delivered', 'Delivered')]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product} ({self.quantity}L)"

