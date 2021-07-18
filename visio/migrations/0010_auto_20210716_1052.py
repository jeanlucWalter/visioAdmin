# Generated by Django 3.2.5 on 2021-07-16 08:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('visio', '0009_remove_sousensemble_ensemble'),
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Inconnu', max_length=64, unique=True, verbose_name='name')),
            ],
            options={
                'verbose_name': 'Site',
            },
        ),
        migrations.AddField(
            model_name='pdv',
            name='site',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='visio.site'),
        ),
    ]