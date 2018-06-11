from .imports import *


class PhotosForm(forms.ModelForm):
    image = forms.FileField(
        label='Image',
        widget=forms.FileInput(attrs={
            'class': 'input',
            'required': True,
            'accepts': 'image/*'
        })
    )

    title = forms.CharField(
        label='Title ',
        # initial= ' ',
        widget=forms.TextInput(attrs={
            'class': 'input',
            'autofocus': True,
            'placeholder': 'Photo title'
        })
    )

    description = forms.CharField(
        label='Description ',
        # initial=' ',
        widget=forms.Textarea(attrs={
            'class': 'input',
            'placeholder': 'Photo Description',
            'cols': 40,
            'rows': 3,
            'style': 'font-size: small;padding: 12px 20px;'
        })

    )
    location = forms.CharField(
        label='Location ',
        initial='unknown',
        widget=forms.TextInput(attrs={
            'class': 'input',
            'autofocus': True,
            'placeholder': 'Where was this photo taken'
        }))

    class Meta:
        model = Photo
        fields = ('image', 'title', 'description', 'location',)
