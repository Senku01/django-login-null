from accounts.models import Profile
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import * 
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.urls import reverse

# Create your views here.

# View for the home page

@login_required
def home(request):
    return render(request , 'home.html')


# View for the login attempt page
def login_attempt(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username = username).first()
        if user_obj is None:
            messages.success(request, 'User not found')
            return redirect('/accounts/login')
        
        profile_obj = Profile.objects.filter(user = user_obj).first()

        if not profile_obj.is_verified:
            messages.success(request,'Profile is not verified check your Mail ')
            return redirect('/accounts/login')
        
        user = authenticate(username = username , password =password)
        if user in None:
            messages.success(request, 'Wrong password')
            return redirect('/accounts/login')
        
        login(request,user)
        return redirect('/')

    return render(request , 'login.html')


# View for the registration attempt page
def register_attempt(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Using Try catch block for best practices
        try:
            # Check if the username is already taken
            if User.objects.filter(username = username).first():
                messages.success(request , 'Username is taken')
                return redirect('/register')
            
            # Check if the email is already taken
            if User.objects.filter(email = email).first():
                messages.success(request,'Email is Taken ')
                return redirect('/register')
            

            # Create a new User object and save it
            user_obj = User(username = username ,email = email)
            user_obj.set_password(password)
            user_obj.save()

            # Generate an authentication token and create a new Profile object
            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user = user_obj , auth_token = auth_token)
            profile_obj.save()

            # Send a verification email to the user
            send_mail_register(email, auth_token)
            
            return redirect('/token_auth')


        except Exception as e:
            print(e)


    return render(request , 'register.html')

# View for the success page after successful registration

def success(request):
    return render(request , 'success.html')

# View for the token authentication page

def token_auth(request):
    return render(request , 'token_auth.html')



# View for verifying the user's account using the authentication token

def verify(request , auth_token):
    try:
        profile_obj =  Profile.objects.filter(auth_token = auth_token).first()

        if profile_obj:
            # Set the account as verified
            if profile_obj.is_verified:
                messages.success(request , 'Your Account is already verified')
                return redirect('/accounts/login')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request , 'Your account has been verified')
            return redirect('/login')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)
        return redirect('/')

# View for the error page
def error_page(request):
    return render(request,'error.html')


# Helper function to send a registration verification email
def send_mail_register(email, token):
    subject = 'Your account needs to be verified'
    message = f'Hi, to verify your account, please click on the following link: http://127.0.0.1:8000/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject , message , email_from, recipient_list)

