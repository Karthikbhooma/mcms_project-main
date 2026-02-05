from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("complaints", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='officer',
            field=models.ForeignKey(
                related_name='assigned_complaints',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name='complaint',
            name='resolution_notes',
            field=models.TextField(blank=True),
        ),
    ]
