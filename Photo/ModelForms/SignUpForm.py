from .imports import *

class SignUpForm(forms.ModelForm):
    email = forms.CharField(
        label='Email ',
        widget=forms.EmailInput(attrs={
            'class': 'input',
            'autofocus': True,
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': 'password'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': 'confirm password'
        })
    )

    def clean_email(self):
        data = self.cleaned_data
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            raise ValidationError("Invalid email")

        return data

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password2'] != cd['password']:
            raise ValidationError("Password don't match")

        return cd['password2']

    class Meta:
        model = Photo
        fields = ('email',)