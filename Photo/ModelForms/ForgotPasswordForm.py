from .imports import *


class ForgotPasswordForm(forms.ModelForm):
    email = forms.CharField(
        label='Email ',
        widget=forms.EmailInput(attrs={
            'class': 'input',
            'autofocus': True,
            'placeholder': 'Email'
        })
    )

    def clean_email(self):
        data = self.cleaned_data
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            raise ValidationError("Invalid email")
        user = User.objects.filter(email=data['email'])
        if len(user) < 1:
            raise ValidationError("Email not found")
        return data

    class Meta:
        model = Photo
        fields = ('email',)
