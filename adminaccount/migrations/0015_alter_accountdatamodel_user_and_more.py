# Generated by Django 5.0.4 on 2024-06-26 07:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminaccount', '0014_accountdatamodel_user_transactionmodel_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountdatamodel',
            name='user',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='adminaccount.userdata'),
        ),
        migrations.AlterField(
            model_name='transactionmodel',
            name='user',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='adminaccount.userdata'),
        ),
    ]
