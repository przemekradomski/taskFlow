from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('To Do', 'Do zrobienia'), ('In Progress', 'W Trakcie'), ('Done', 'Gotowe')], default='To Do', max_length=20)),
                ('priority', models.CharField(choices=[('Low', 'Niska'), ('Medium', 'Średnia'), ('High', 'Wysoka'), ('Urgent', 'Pilna')], default='Medium', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
