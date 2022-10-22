# Generated by Django 4.1.1 on 2022-10-09 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0012_threadmodel_messagemodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='media/uploads/post_picture')),
            ],
        ),
        migrations.RemoveField(
            model_name='threadmodel',
            name='receiver',
        ),
        migrations.RemoveField(
            model_name='threadmodel',
            name='user',
        ),
        migrations.RemoveField(
            model_name='post',
            name='image',
        ),
        migrations.DeleteModel(
            name='MessageModel',
        ),
        migrations.DeleteModel(
            name='ThreadModel',
        ),
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ManyToManyField(blank=True, to='social.image'),
        ),
    ]