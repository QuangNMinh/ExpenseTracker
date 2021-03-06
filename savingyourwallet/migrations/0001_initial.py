# Generated by Django 3.1.7 on 2021-04-21 05:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='categories',
            fields=[
                ('CategoryID', models.TextField(primary_key=True, serialize=False)),
                ('CategoryName', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='sub_categories',
            fields=[
                ('S_categoryID', models.TextField(primary_key=True, serialize=False)),
                ('S_categoryName', models.CharField(max_length=100)),
                ('CategoryID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='savingyourwallet.categories')),
            ],
        ),
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(blank=True, max_length=50, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='transaction',
            fields=[
                ('TransactionID', models.TextField(primary_key=True, serialize=False)),
                ('Budget', models.DecimalField(decimal_places=2, max_digits=19)),
                ('Date', models.DateTimeField(default=django.utils.timezone.now)),
                ('CategoryID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='savingyourwallet.categories')),
                ('S_categoryID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='savingyourwallet.sub_categories')),
                ('UserID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
