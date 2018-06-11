import datetime
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight

# Create your models here.

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(default="")
    image = models.ImageField(upload_to="photo/%Y/%m/%d", null=True, blank=True, default='No.jpg')
    created_on = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=150, default='unknown')
    is_deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    @classmethod
    def get_by_title(cls, title):
        return cls.objects.get(title=title)

    @classmethod
    def get_by_id(cls, photo_id):
        return cls.objects.get(id=photo_id)

    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'

    def __unicode__(self):
        return self.title


class PasswordReset(models.Model):
    email = models.CharField(max_length=250)
    reset_hash = models.CharField(max_length=250)
    created_on = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=0)
    used_on = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=0)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def get_by_hash(self, reset_hash):
        reset = PasswordReset.objects.filter(reset_hash=reset_hash)
        if len(reset) < 1:
            return {'result': False, 'error': 'Invalid hash'}
        reset = reset[0]
        if reset.is_used is True:
            return {'result': False, 'error': 'Link has been used'}
        if reset.is_deleted is True:
            return {'result': False, 'error': 'Link has been cancelled'}
        if reset.expires_on <= timezone.now():
            return {'result': False, 'error': 'Link has expired'}
        return {'result': True, 'email': reset.email}

    def forgot_password(self, email, reset_hash):
        PasswordReset.objects.filter(email=email, is_deleted=False) \
            .update(is_deleted=True, deleted_on=datetime.datetime.now())

        reset = PasswordReset(reset_hash=reset_hash, email=email,
                              expires_on=datetime.datetime.now() + datetime.timedelta(hours=24))
        reset.save()

    def reset_user_password(self, password, email):
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        PasswordReset.objects.filter(email=email, is_deleted=False) \
            .update(is_deleted=True, deleted_on=datetime.datetime.now(), is_used=True, used_on=datetime.datetime.now())

    class Meta:
        verbose_name = 'PasswordReset'
        verbose_name_plural = 'PasswordResets'

    def __unicode__(self):
        return self.email


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)
    owner = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE)
    highlighted = models.TextField()

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language)
        linenos = 'table' if self.linenos else False
        options = {'title': self.title} if self.title else {}
        formatter = HtmlFormatter(style=self.style, linenos=linenos,
                                  full=True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super(Snippet, self).save(*args, **kwargs)