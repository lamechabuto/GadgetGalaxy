from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleorder',
            name='payment_method',
            field=models.CharField(choices=[('lipa_pole_pole', 'Lipa Pole Pole'), ('cash', 'Cash')], default='cash', max_length=30),
        ),
    ]
