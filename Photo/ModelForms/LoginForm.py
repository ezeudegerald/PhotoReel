from .imports import *

class LoginForm(forms.ModelForm):
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
        }),
        help_text='Must contain Uppercase, lowercase, number and must be up to 8 characters'
    )

    def clean_email(self):
        data = self.cleaned_data
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            raise ValidationError("Invalid email")

        return data

    class Meta:
        model = Photo
        fields = ('email',)