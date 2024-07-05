from django.db import models

# Create your models here.
class Userdata(models.Model):
    class Meta:
        db_table = 'User_tb'
    
    user_id = models.CharField(max_length=60, primary_key=True, default=True)
    user_firstname = models.CharField(max_length=120, null=True, blank=True, default=None)
    user_middlename = models.CharField(max_length=120, null=True, blank=True, default=None)
    user_lastname = models.CharField(max_length=120, null=True, blank=True, default=None)
    user_email = models.EmailField(max_length=254, null=True, blank=True, default=None)
    user_username = models.CharField(max_length=120, null=True, blank=True, default=None)
    user_gender = models.CharField(max_length=120, null=True, blank=True, default=None)
    user_password = models.CharField(max_length=120, null=True, blank=True, default=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_active = models.BooleanField(default=False)

class AccountdataModel(models.Model):
    class Meta:
        db_table = 'account_data_tb'

    account_id = models.CharField(max_length=120, primary_key=True, default=True)
    user = models.ForeignKey(Userdata, on_delete=models.CASCADE, related_name='accounts')
    account_name = models.CharField(max_length=120, null=True, blank=True, default=None)
    account_email_id = models.EmailField(max_length=120, null=True, blank=True, default=None)
    account_phone_number = models.CharField(max_length=120, null=True, blank=True, default=None)
    # account_address_line_1 = models.CharField(max_length=120, null=True, blank=True, default=None)
    # account_address_line_2 = models.CharField(max_length=120, null=True, blank=True, default=None)
    account_city = models.CharField(max_length=120, null=True, blank=True, default=None)
    account_state = models.CharField(max_length=120, null=True, blank=True, default=None)
    # account_country = models.CharField(max_length=120, null=True, blank=True, default=None)
    account_pincode = models.CharField(max_length=120, null=True, blank=True, default=None)

class TransactionModel(models.Model):
    class Meta:
        db_table = 'transaction_detail_tb'

    transaction_id = models.CharField(max_length=120, primary_key=True, default=True)
    user = models.ForeignKey(Userdata, on_delete=models.CASCADE, related_name='transactions')
    transaction_date = models.DateField(max_length=120)
    account_name = models.CharField(max_length=120, null=True, blank=True, default=None)
    credit_amount = models.CharField(max_length=120, null=True, blank=True, default=None)
    debit_amount = models.CharField(max_length=120, null=True, blank=True, default=None)