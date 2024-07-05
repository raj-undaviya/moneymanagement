from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.views.generic.base import TemplateView
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import stripe
import json
import logging
from .models import *
import random, string
import re
from .forms import *

from pymongo import MongoClient
client = MongoClient('connection_string')
db = client['db_name']

logger = logging.getLogger(__name__)
# Create your views here.
# Views for payment
@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {
            'publicKey': settings.STRIPE_PUBLISHABLE_KEY,
            'secretKey': settings.STRIPE_SECRET_KEY
        }
        return JsonResponse(stripe_config, safe=False)
    
class startingPage(TemplateView):
    template_name = 'landing-page.html'

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        domain_url = 'http://localhost:8000/'  # Ensure this is correct for your environment
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            data = json.loads(request.body.decode('utf-8'))
            amount_in_rupees = int(data['planPrice'])
            amount_in_paisa = amount_in_rupees * 100
            # Create a new Checkout Session for the order
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success/session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': data["planName"],
                            'description': data["planDesc"],
                        },
                        'unit_amount': amount_in_paisa,  # Amount is in cents
                    },
                    'quantity': 1,
                }]
            )
            logger.info("Checkout session created successfully: %s", checkout_session['id'])
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            logger.error("Error creating checkout session: %s", str(e))
            return JsonResponse({'error': str(e)})


class SuccessView(TemplateView):
    template_name = 'success.html'

class CancelledView(TemplateView):
    template_name = 'cancelled.html'

def register(request):
    if request.method == 'POST':
        randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        user_id = 'USER_' + randomstr

        firstname = request.POST.get('firstname')
        middlename = request.POST.get('middlename')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        gender = request.POST.get('gender')
        profileimg = request.FILES.get('profileimg')
        print(profileimg)
        if Userdata.objects.filter(user_email=email).exists():
            return render(request, 'register.html', {'error': 'User already registered.'})

        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match.'})

        encrypted_password = make_password(password)

        userdata = Userdata(
            user_id=user_id,
            user_firstname=firstname,
            user_middlename=middlename,
            user_lastname=lastname,
            user_email=email,
            user_username=username,
            user_password=encrypted_password,
            user_gender=gender,
            profile_image=profileimg
        )
        userdata.save()
        response = redirect('homePage')

        return response

    return render(request, 'register.html')

def forgotPassword(request):
    if request.method == 'POST':
        recipientdata = request.POST.get('email')
        otp = random.randint(0000, 9999)
        request.session['recipient'] = {'recipient':recipientdata, 'otp':otp}
        subject = 'Update Password'
        message = f'One Time Password is {otp}'
        email_from = 'no-reply@binaries.org.in'
        recipient_list = [recipientdata]
        send_mail(subject, message, email_from, recipient_list)
        return redirect('otpVerificationPage')
    return render(request, 'forgot-password.html')

def otptemplate(request):
    recipientdata = request.session.get('recipient')
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == str(recipientdata['otp']):
            return redirect('passwordUpdationPage')
        else:
            print("OTP is expired or incorrect!!")
    return render(request, 'otp-template.html', {'recipient':recipientdata})

def passwordUpdate(request):
    recipientdata = request.session.get('recipient')
    if not recipientdata:
        print("Recipient data not found in session.")
        return redirect('forgotPasswordPage')

    userdata = Userdata.objects.filter(user_email=recipientdata['recipient']).first()
    if not userdata:
        print("User not found.")
        return redirect('otpVerificationPage')

    if request.method == 'POST':
        password = request.POST.get('password')
        if not password or len(password) < 8:  # Example validation
            print("Invalid password. Password must be at least 8 characters long.")
            return redirect('password_update_page')
        userdata.user_password = make_password(password)
        userdata.save()
        print("Password Updated Successfully")
        return redirect('homePage')

    return render(request, 'password-update.html')

def home(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        if "@" in email:
            userdata = Userdata.objects.filter(user_email=email).first()
        else:
            userdata = Userdata.objects.filter(user_username=email).first()

        if userdata:
            if userdata.user_email == email or userdata.user_username == email:
                if check_password(password, userdata.user_password):
                    # Create session data dictionary
                    session_data = {
                        'id': userdata.user_id,
                        'email': userdata.user_email,
                        'username': userdata.user_username,
                        'firstname': userdata.user_firstname,
                        'middlename':userdata.user_middlename,
                        'lastname': userdata.user_lastname,
                        'gender':userdata.user_gender
                    }
                    if userdata.profile_image:
                        session_data['profile_image'] = userdata.profile_image.url
                    else:
                        session_data['profile_image'] = None  # Or set a default image URL

                    # Store user data in session
                    request.session['userdata'] = session_data

                    return redirect('dashboardPage')
                else:
                    messages.error(request, "Incorrect Password")
            else:
                messages.error(request, "Invalid Email/Username")
        else:
            messages.error(request, "User Not Found. Register first.")

    return render(request, 'home-page.html')

def dashboard(request):
    userdata = request.session.get('userdata')
    id = userdata['id']
    useraccountdata = AccountdataModel.objects.filter(user=id)
    transactionsdata = TransactionModel.objects.filter(user=id)
    creditAmountReport = transactionsdata.exclude(credit_amount=None).values('credit_amount')
    debitAmountReport = transactionsdata.exclude(debit_amount=None).values('debit_amount')
    
    total_credit = sum(int(item['credit_amount']) for item in creditAmountReport)
    total_debit = sum(int(item['debit_amount']) for item in debitAmountReport)

    if not userdata:
        return redirect('homePage')
    return render(request, 'dashboard.html', {'userdata': userdata,
                                              'useraccountdata':useraccountdata,
                                              'transactionsdata':transactionsdata,
                                              'total_credit': total_credit,
                                              'total_debit': total_debit})

def addaccount(request):
    accountdata = request.session.get('userdata')
    id = accountdata['id']
    useraccountdata = AccountdataModel.objects.filter(user=id)
    if not accountdata:
        return redirect('homePage')
    if not useraccountdata.exists():
        empty_message = "You Don't Have accounts. Please add some accounts to do transactions!!"
    else:
        empty_message = None
    if request.method == 'POST':
        randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        uniqueID = 'Acc_' + randomstr
        account_id = uniqueID
        account_name = request.POST.get("account_name")
        account_email_id  = request.POST.get("account_email_id")
        account_phone_number = request.POST.get("account_phone_number")
        # account_address_line_1 = request.POST.get("account_address_1")
        # account_address_line_2 = request.POST.get("account_address_2")
        account_city = request.POST.get("account_city")
        account_state = request.POST.get("account_state")
        # account_country = request.POST.get("account_country")
        account_pincode = request.POST.get("account_pincode")
        userdata = AccountdataModel.objects.filter(account_email_id=account_email_id).values().first()
        user = Userdata.objects.get(user_id=id)
        print('----------------->', user)
        if userdata is None:
            userdata = AccountdataModel(account_id=account_id,
                                        user=user,
                                        account_name=account_name,
                                        account_email_id=account_email_id,
                                        account_phone_number=account_phone_number,
                                        # account_address_line_1=account_address_line_1,
                                        # account_address_line_2=account_address_line_2,
                                        account_city=account_city,
                                        account_state=account_state,
                                        # account_country=account_country,
                                        account_pincode=account_pincode)
            userdata.save()
            return redirect('addaccountPage')
        else:
            print("Account Already Exsist.........")
    return render(request, 'addaccount.html',{'userdata':useraccountdata,
                                              'empty_message':empty_message,
                                              'accountdata':accountdata })

def updateaccountdata(request, account_id):
    accountdata = request.session.get('userdata')
    if not accountdata:
        return redirect('homePage')
    userdata = get_object_or_404(AccountdataModel, account_id=account_id)
    if request.method == 'POST':
        userdata.account_name = request.POST.get("account_name")
        userdata.account_email_id = request.POST.get("account_email_id")
        userdata.account_phone_number = request.POST.get("account_phone_number")
        userdata.account_address_line_1 = request.POST.get("account_address_1")
        userdata.account_address_line_2 = request.POST.get("account_address_2")
        userdata.account_city = request.POST.get("account_city")
        userdata.account_state = request.POST.get("account_state")
        userdata.account_country = request.POST.get("account_country")
        userdata.account_pincode = request.POST.get("account_pincode")
        userdata.save()
        return redirect('addaccountPage')
    return render(request, 'updateaccount.html', {'userdata': userdata,
                                                  'accountdata':accountdata })

def deleteaccountdata(request, account_id):
    userdata = get_object_or_404(AccountdataModel, account_id=account_id)
    userdata.delete()
    return redirect('addaccountPage')

def transaction(request):
    accountdata = request.session.get('userdata')
    id = accountdata['id']
    transactionsdata = TransactionModel.objects.filter(user=id)
    userdata = AccountdataModel.objects.filter(user=id)
    if not accountdata:
        return redirect('homePage')
    if not transactionsdata.exists():
        empty_message = "You Don't Have Any Transaction !!"
    else:
        empty_message = None
    transactiondata = TransactionModel.objects.filter(user=id).values()
    if request.method == 'POST':
        randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        uniqueID = 'TRN_' + randomstr
        transaction_id = uniqueID
        transaction_date = request.POST.get("transaction_date")
        account_name = request.POST.get("account_name")
        credit_amount = request.POST.get("credit_amount")
        debit_amount = request.POST.get("debit_amount")
        user = Userdata.objects.get(user_id=id)
        print(user)
        transactiondata = TransactionModel(transaction_id=transaction_id,
                                           user=user,
                                           transaction_date=transaction_date,
                                           account_name=account_name,
                                           credit_amount=credit_amount,
                                           debit_amount=debit_amount)
        transactiondata.save()
        return redirect('transactionPage')
    return render(request, 'transaction.html', {'userdata':userdata,
                                                'accountdata':accountdata,
                                                'transactiondata':transactiondata,
                                                'empty_message':empty_message })

def updaterecorddata(request, transaction_id):
    accountdata = request.session.get('userdata')
    if not accountdata:
        return redirect('homePage')
    userdata = AccountdataModel.objects.all()
    transactiondata = get_object_or_404(TransactionModel, transaction_id=transaction_id)
    if request.method == 'POST':
        transactiondata.account_name = request.POST.get("account_name")
        transactiondata.credit_amount = request.POST.get("credit_amount")
        transactiondata.debit_amount = request.POST.get("debit_amount")
        transactiondata.save()
        return redirect('transactionPage')
    return render(request, 'updatetransaction.html', {'transactiondata': transactiondata,
                                                      'accountdata':accountdata,
                                                      'userdata':userdata})

def deleterecorddata(request, transaction_id):
    transactiondata = get_object_or_404(TransactionModel, transaction_id=transaction_id)
    transactiondata.delete()
    return redirect('transactionPage')

def reports(request):
    accountdata = request.session.get('userdata')
    id = accountdata['id']
    if not accountdata:
        return redirect('homePage')
    useraccountdata = AccountdataModel.objects.filter(user=id)
    transactiondata = TransactionModel.objects.filter(user=id).values()

    creditAmountReport = transactiondata.exclude(credit_amount=None).values()
    debitAmountReport = transactiondata.exclude(debit_amount=None).values()

    total_credit = sum(int(item['credit_amount']) for item in creditAmountReport)
    total_debit = sum(int(item['debit_amount']) for item in debitAmountReport)

    return render(request, 'reports.html', {'accountdata':accountdata,
                                            'userdata':useraccountdata,
                                            'transactiondata':transactiondata,
                                            'creditdata':creditAmountReport,
                                            'debitdata': debitAmountReport,
                                            'total_credit': total_credit,
                                            'total_debit': total_debit})

def helpline(request):
    accountdata = request.session.get('userdata')
    if not accountdata:
        return redirect('homePage')
    
    return render(request, 'helpline.html', {'accountdata':accountdata, })

def userprofile(request):
    accountdata = request.session.get('userdata')
    email = accountdata['email']
    if request.method == 'POST':
        profileimg = request.FILES.get('profile_image')
        print(profileimg)
        firstname=request.POST.get('firstname')
        middlename=request.POST.get('middlename')
        lastname=request.POST.get('lastname')
        gender=request.POST.get('gender')
        current_password=request.POST.get('current_password')
        password=request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')
        userdata = Userdata.objects.filter(user_email=email).first()
        if userdata:
            if current_password and password and confirm_password:
                if check_password(current_password, userdata.user_password):
                    if password == confirm_password:
                        encrypted_password = make_password(password)
                        userdata.user_firstname = firstname
                        userdata.user_middlename = middlename
                        userdata.user_lastname = lastname
                        userdata.user_gender = gender
                        userdata.user_password = encrypted_password
                        userdata.profile_image = profileimg
                        userdata.save()
                        accountdata['firstname'] = userdata.user_firstname
                        accountdata['middlename'] = userdata.user_middlename
                        accountdata['lastname'] = userdata.user_lastname
                        accountdata['gender'] = userdata.user_gender
                        accountdata['profile_image'] = userdata.profile_image.url
                        request.session['userdata'] = accountdata
                        return redirect('userprofilePage')
                    else:
                        print('Password and confirm password not matched....')
                else:
                    print('Password does not match....')
            else:
                userdata.user_firstname = firstname
                userdata.user_middlename = middlename
                userdata.user_lastname = lastname
                userdata.user_gender = gender
                userdata.profile_image = profileimg
                userdata.save()
                accountdata['firstname'] = userdata.user_firstname
                accountdata['middlename'] = userdata.user_middlename
                accountdata['lastname'] = userdata.user_lastname
                accountdata['gender'] = userdata.user_gender
                accountdata['profile_image'] = userdata.profile_image.url
                request.session['userdata'] = accountdata
                return redirect('userprofilePage')
        else:
            print('Userdata Not Found....')
    return render(request, 'userprofile.html', {'accountdata':accountdata})

def logout(request):
    request.session.flush()
    response = redirect('homePage')
    for cookie in request.COOKIES:
        response.delete_cookie(cookie)
    return response