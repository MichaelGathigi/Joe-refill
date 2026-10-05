from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Order(models.Model):
    PRODUCT_CHOICES = [('water', 'Water'), ('oil', 'Cooking Oil')]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.CharField(max_length=10, choices=PRODUCT_CHOICES)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text='Litres')
    location = models.CharField(max_length=255, help_text='Town or estate, e.g. Voi Town')
    delivery_address = models.CharField(max_length=255, help_text='Building, house number or landmark')
    phone = models.CharField(max_length=20, help_text='Number the rider can call on delivery')
    delivery_date = models.DateField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_product_display()} ({self.quantity}L)"

    @property
    def can_cancel(self):
        return self.status == 'pending'


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} <{self.email}>"
