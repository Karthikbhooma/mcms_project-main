from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("complaints", "0003_remove_complaint_category"),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='resolution_proof',
            field=models.FileField(blank=True, null=True, upload_to='complaints/'),
        ),
    ]
