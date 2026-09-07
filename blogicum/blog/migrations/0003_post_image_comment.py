import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_category_options_alter_location_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={
                'default_related_name': 'posts',
                'ordering': ('-pub_date',),
                'verbose_name': 'публикация',
                'verbose_name_plural': 'Публикации',
            },
        ),
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='post_images/',
            ),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('text', models.TextField(verbose_name='Текст')),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Добавлено',
                )),
                ('author', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='comments',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('post', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='comments',
                    to='blog.post',
                )),
            ],
            options={'ordering': ('created_at',)},
        ),
    ]
