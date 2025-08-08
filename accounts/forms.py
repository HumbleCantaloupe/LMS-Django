from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import User, UserProfile

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'date_of_birth', 'address', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        user.address = self.cleaned_data['address']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 
                 'date_of_birth', 'address', 'emergency_contact_name', 
                 'emergency_contact_phone', 'profile_picture']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class UserProfileExtendedForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'preferred_branch', 'reading_preferences', 
                 'notification_preferences', 'privacy_settings']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'reading_preferences': forms.CheckboxSelectMultiple(),
            'notification_preferences': forms.Textarea(attrs={'rows': 3}),
            'privacy_settings': forms.Textarea(attrs={'rows': 3}),
        }

class MemberSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name, username, email, or library card...',
            'class': 'form-control'
        })
    )
    status = forms.ChoiceField(
        choices=[
            ('all', 'All Members'),
            ('active', 'Active Members'),
            ('inactive', 'Inactive Members'),
        ],
        required=False,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    user_type = forms.ChoiceField(
        choices=[
            ('all', 'All Types'),
            ('member', 'Members'),
            ('librarian', 'Librarians'),
            ('admin', 'Administrators'),
        ],
        required=False,
        initial='member',
        widget=forms.Select(attrs={'class': 'form-control'})
    )