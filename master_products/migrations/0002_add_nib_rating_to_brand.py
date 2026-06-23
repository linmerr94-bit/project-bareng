# Generated migration for adding nib_or_ktp and rating fields to Brand model
# and updating STATUS_CHOICES to include 'suspended'

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('master_products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='nib_or_ktp',
            field=models.CharField(
                blank=True,
                db_column='nib_or_ktp',
                help_text='Nomor Induk Berusaha (NIB) atau Nomor KTP',
                max_length=50,
                null=True,
                unique=True
            ),
        ),
        migrations.AddField(
            model_name='brand',
            name='rating',
            field=models.FloatField(
                db_column='rating',
                default=0.0,
                help_text='Rating brand dari customer (0.0-5.0)',
                validators=[
                    django.core.validators.MinValueValidator(0.0),
                    django.core.validators.MaxValueValidator(5.0)
                ]
            ),
        ),
        migrations.AlterField(
            model_name='brand',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending Approval'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                    ('suspended', 'Suspended')
                ],
                default='pending',
                help_text='Status persetujuan brand (pending, approved, rejected, suspended)',
                max_length=20
            ),
        ),
    ]
