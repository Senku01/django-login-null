from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    # One-to-One relationship with the User model
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    # Authentication token for account verification
    auth_token = models.CharField(max_length=100)
    # Verification status of the user's account
    is_verified = models.BooleanField(default=False) 
    # Date and time when the profile is created
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
    # Return the username as the string representation
        return self.user.username
