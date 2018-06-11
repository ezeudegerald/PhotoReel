from .imports import *


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'input',
                'autofocus': True,
                'required': True,
                'placeholder':'Enter new password'
            })
    )
    password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'required': True,
            'placeholder': 'Repeat Password'
        })
    )

    # Validating password
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password2'] != cd['password']:
            raise ValidationError("Password don't match")

        return cd['password2']
