# Generated by Django 5.1.3 on 2024-12-05 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Library', '0003_isbn_language_remove_book_book_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='isbn',
            name='book_content',
            field=models.TextField(blank=True, null=True),
        ),
    ]
