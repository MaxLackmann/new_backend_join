from django.db import migrations

def create_guest_user(apps, schema_editor):
    User = apps.get_model('join_api', 'User')
    if not User.objects.filter(id=0).exists():
        # Erstellt den Guest User mit einer festen ID
        guest_user = User(
            id=0,
            name="Guest",
            email="guest@example.com",
            password="",  # Sicherstellen, dass kein echtes Passwort verwendet wird
            emblem="G",  # Standardemblem für Guest
            color="#CCCCCC"  # Standardfarbe für Guest
        )
        # Benutze force_insert=True um sicherzustellen, dass keine Konflikte mit der ID entstehen
        guest_user.save(force_insert=True)

class Migration(migrations.Migration):

    dependencies = [
        ('join_api', '0003_alter_subtask_task_alter_task_priority'),  # Ersetze '0003_alter_subtask_task_alter_task_priority' durch den tatsächlichen Namen der vorherigen Migrationsdatei
    ]

    operations = [
        migrations.RunPython(create_guest_user),
    ]