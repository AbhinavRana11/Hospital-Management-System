from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_patient_dob_alter_patient_age_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('age', models.PositiveIntegerField(blank=True, null=True)),
                ('dob', models.DateField()),
                ('address', models.TextField()),
                ('problem', models.TextField()),
                ('admin_reply', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('replied_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
