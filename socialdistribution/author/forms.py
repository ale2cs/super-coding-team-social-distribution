from django import forms 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, SiteConfiguration

# contains different forms that the user interacts with
# e.g the registration form/screen, update user, etc.
class RegisterUser(UserCreationForm):
    first_name = forms.CharField(max_length=100,
                                 required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name',
                                                                'class': 'form-control',
                                                                }))
    
    last_name = forms.CharField(max_length=100,
                                 required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'Last Name',
                                                                'class': 'form-control',
                                                                }))
    
    username = forms.CharField(max_length=100,
                                 required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                                'class': 'form-control',
                                                                }))
    
    email = forms.EmailField(max_length=100,
                                 required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'Email',
                                                                'class': 'form-control',
                                                                }))
    github = forms.URLField(required=False,
                            widget=forms.URLInput(attrs={'placeholder': 'Github Link',
                                                        'class': 'form-control'}),
                            label='',
                            )
    
    password1 = forms.CharField(max_length=100,
                                 required=True,
                                 widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                'class': 'form-control',
                                                                'data-toggle': 'password',
                                                                'id': 'password',
                                                                }))
    
    password2 = forms.CharField(max_length=100,  # <--  this one can be removed if we don't want the functionality
                                 required=True,
                                 widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
                                                                'class': 'form-control',
                                                                'data-toggle': 'password',
                                                                'id': 'password',
                                                                })) 
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class LoginUser(AuthenticationForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control',
                                                             }))
    password = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'form-control',
                                                                 'data-toggle': 'password',
                                                                 'id': 'password',
                                                                 'name': 'password',
                                                                 }))
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me']

class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']


class UpdateProfileForm(forms.ModelForm):
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    github = forms.URLField(required=False,
                            widget=forms.URLInput(attrs={'placeholder': 'Github Link',
                                                        'class': 'form-control'}),
                            label='',
                            )
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

    class Meta:
        model = Profile
        fields = ['avatar', 'github', 'bio']

class SiteConfigurationForm(forms.ModelForm):
    class Meta: 
        model = SiteConfiguration
        fields = ['user_approval_required']
        widgets = {'user_approval_required':forms.CheckboxInput(attrs={'class':'switch'})}