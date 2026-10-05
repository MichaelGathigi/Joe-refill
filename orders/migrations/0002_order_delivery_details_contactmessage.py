import datetime

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_address',
            field=models.CharField(default='', help_text='Building, house number or landmark', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='phone',
            field=models.CharField(default='', help_text='Number the rider can call on delivery', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(default=datetime.date(2025, 1, 1)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='location',
            field=models.CharField(help_text='Town or estate, e.g. Voi Town', max_length=255),
        ),
        migrations.AlterField(
            model_name='order',
            name='quantity',
            field=models.PositiveIntegerField(help_text='Litres', validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
