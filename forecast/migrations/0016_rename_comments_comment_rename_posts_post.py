# Generated by Django 4.0 on 2022-04-29 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('forecast', '0015_alter_comments_options_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Comments',
            new_name='Comment',
        ),
        migrations.RenameModel(
            old_name='Posts',
            new_name='Post',
        ),
    ]
