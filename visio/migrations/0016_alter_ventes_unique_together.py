# Generated by Django 3.2.5 on 2021-07-21 07:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('visio', '0015_ventes'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ventes',
            unique_together={('pdv', 'industry', 'product')},
        ),
    ]
