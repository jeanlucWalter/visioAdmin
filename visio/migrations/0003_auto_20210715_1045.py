# Generated by Django 3.2.5 on 2021-07-15 08:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('visio', '0002_auto_20210715_1023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enseigne',
            name='name',
            field=models.CharField(max_length=64, unique=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='pdv',
            name='code',
            field=models.CharField(default='Inconnu', max_length=10, unique=True, verbose_name='code'),
        ),
        migrations.AlterField(
            model_name='pdv',
            name='name',
            field=models.CharField(default='Inconnu', max_length=64, unique=True, verbose_name='name'),
        ),
        migrations.CreateModel(
            name='Ensemble',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Inconnu', max_length=64, unique=True, verbose_name='name')),
                ('enseigne', models.ForeignKey(default=7, on_delete=django.db.models.deletion.PROTECT, to='visio.enseigne')),
            ],
            options={
                'verbose_name': 'Ensemble',
            },
        ),
    ]