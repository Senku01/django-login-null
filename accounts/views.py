from accounts.models import Profile
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import * 
import uuid
from django.conf import settings
from django.core.mail import send_mail


# Create your views here.

# View for the home page
def home(request):
    return render(request , 'home.html')


# View for the login attempt page
def login_attempt(request):
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
            send_mail_register(email,auth_token)
            
            return redirect('/token')


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
        profile_obj =  Profile.objects.filter(auth_token).first()
        if profile_obj:
            # Set the account as verified
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request , 'Your account has been verified')
            return redirect('/login')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)

# View for the error page
def error_page(request):
    return render(request,'error.html')


# Helper function to send a registration verification email
def send_mail_register(email, token):
    subject = 'Your account need to be verified'
    message = f'Hi To verify your account http://127.0.0.1:8000/verify/{token}'
    email_from  = settings.EMAIL_HOST_USER
    reciptant_list = [email]

    send_mail(subject,message,email_from, reciptant_list)

