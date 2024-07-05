from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.startingPage.as_view(), name="landingPage"),
    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('paymwnt-declined/', views.CancelledView.as_view()),
    path('success/<str:session_id>', views.SuccessView.as_view()),
    path('login/', views.home, name='homePage'),
    path('register/', views.register, name='registerPage'),
    path('forgot-password/', views.forgotPassword, name='forgotPasswordPage'),
    path('otp-verification/', views.otptemplate, name='otpVerificationPage'),
    path('password-update/', views.passwordUpdate, name='passwordUpdationPage'),
    path('dashboard/', views.dashboard, name='dashboardPage'),
    path('addaccount/', views.addaccount, name='addaccountPage'),
    path('update_user/<account_id>', views.updateaccountdata, name='update_user'),
    path('delete_user/<account_id>', views.deleteaccountdata, name='delete_user'),
    path('transaction/', views.transaction, name='transactionPage'),
    path('update_record/<transaction_id>', views.updaterecorddata, name='update_record'),
    path('delete_record/<transaction_id>', views.deleterecorddata, name='delete_record'),
    path('reports/', views.reports, name='reportsPage'),
    path('userprofile/', views.userprofile, name='userprofilePage'),
    path('logout/', views.logout, name='logout')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)