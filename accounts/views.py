from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.core.serializers.json import DjangoJSONEncoder
from login_site import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token
import random
import datetime
import json 
# Create your views here.

# View for the home page

def home(request):
    return render(request, "index.html")

def signup(request):
    if request.method == "POST":
        # Retrieve form data from the POST request.
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username=username):
            # Check if the username already exists in the User model.
            # If it exists, display an error message and redirect to the home page.
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('home')
        
        if len(username)>20:
            # Check if the username length is greater than 20 characters.
            # If it is, display an error message and redirect to the home page.
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('home')
        
        if pass1 != pass2:
            # Check if the passwords provided in the form do not match.
            # If they don't match, display an error message and redirect to the home page.
            messages.error(request, "Passwords didn't matched!!")
            return redirect('home')
        
        if not username.isalnum():
            # Check if the username contains only alphanumeric characters.
            # If it doesn't, display an error message and redirect to the home page.
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('home')
        
        # Create a new user using the User model's create_user() method.
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        # myuser.is_active = False
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")
        
        # Welcome Email
        subject = "Welcome to Null- Null Login!!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to Null!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\n Null jobs"        
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ Null - Null Login!!"
        message2 = render_to_string('email_confirmation.html',{
            
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        return redirect('signin')
        
        
    return render(request, "signup.html")


def activate(request,uidb64,token):
    # This function handles the account activation process when a user clicks on the activation link.
    # Using Try block for better practices

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
        # Decode the uidb64 parameter to get the user's ID.
        # If decoding fails, an exception is raised.
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')
    
# OTP 
def otp_verify(request):
    # if request.method == "POST":
    #     entered_otp = request.POST.get('otp')
    #     saved_otp = request.session.get('otp')
    #     expiry_time = request.session.get('expiry_time')

    #     if entered_otp == saved_otp and datetime.datetime.now() < expiry_time:

    #         del request.session['otp']
    #         del request.session['expiry_time']

    #         return redirect('index.html')
    #     else:
    #         return redirect(request,'otp_verify.html' , {'error':'Invalid OTP'})
    
    # otp = str(random.randint(100000, 999999))
    # expiry_time = datetime.datetime.now() + datetime.timedelta(minutes= 5)
    # request.session['otp']  = otp 
    # request.session['expiry_time'] = expiry_time

    # expiry_time_str = expiry_time.strftime('%Y-%m-%d %H:%M:%S')

    # context = {
    #     'otp': otp,
    #     'expiry_time':expiry_time_str,
    # }


    # return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type='application/json')
    return render(request, 'otp_verify.html')


def signin(request):
    # This function handles the signin process when a user submits the signin form.
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        # Authenticate the user using the provided username and password.
        # If the credentials are valid, it returns a User object, otherwise None.
        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "index.html",{"fname":fname})
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('home')
    
    return render(request, "signin.html")


def signout(request):
        # This function handles the signout process when a user clicks on the signout button.
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')

