from django.contrib import auth, messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, mixins, generics, renderers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.reverse import reverse

from Photo.decorators import *
from .forms import *
from .helpers import *
from .serializers import *
from .permissions import *


# Create your views here.

def index(request):
    photos = Photo.objects.filter(is_deleted=0).order_by('-id')[:16]
    return render(request, 'index.html', context_args(request, {'photos': photos}))


@login_required
def profile(request):
    user_photos = Photo.objects.filter(user=request.user, is_deleted=0).order_by('-id')[:16]
    return render(request, 'profile.html', context_args(request, {'photos': user_photos, 'form': PhotosForm()}))


@login_forbidden()
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return authenticate_user(request, request.POST.get('email'), request.POST.get('password'), form)
    else:
        form = LoginForm()
    return render(request, 'login.html', context_args(request, {'form': form}))


def authenticate_user(request, username, password, form, template='login'):
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        messages.success(request, 'Welcome ' + request.user.username)

        if request.POST.get('next'):
            return redirect(request.POST.get('next'))

        photos = Photo.objects.filter(is_deleted=0).order_by('-id')[:16]
        return render(request, 'profile.html',
                      context_args(request, {'photos': photos, 'form': PhotosForm}))
    messages.error(request, 'Authentication Failed.')
    return render(request, template + '.html', context_args(request, {'form': form}))


@login_forbidden
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = email = request.POST.get('email')
            password = request.POST.get('password')
            user = User.objects.create_user(username, email, password)
            user.save()
            return authenticate_user(request, email, password, form, 'signup')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', context_args(request, {'form': form}))


# @login_required()
def logout_user(request):
    logout(request)
    messages.success(request, 'See You !')
    return render(request, 'index.html', context_args(request))


@login_required()
def save_photo(request):
    form = PhotosForm(request.POST, request.FILES)
    if form.is_valid():
        photo = form.save(commit=False)
        photo.user = request.user
        photo.save()
        messages.success(request, 'Photo successfully added !')
        return profile(request)
    user_photos = Photo.objects.filter(user=request.user, is_deleted=0).order_by('-id')[:16]
    return render(request, 'profile.html', context_args(request, {'photos': user_photos, 'form': form}))


@login_forbidden()
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            reset_hash = get_random_string(75) + '--' + get_random_string(75)
            email = request.POST.get('email')

            PasswordReset.forgot_password(request, email, reset_hash)

            # reset_url = "{0}://{1}{2}{3}/{4}".format(request.scheme, request.get_host(), request.path,
            # 'reset_password',reset_hash)
            reset_url = "{0}://{1}/{2}/{3}".format(request.scheme, request.get_host(), 'reset_password', reset_hash)

            message = render_to_string('reset_password_email.html', {'reset_url': reset_url})
            send_mail('Reset Password', message, 'casper', [email], html_message=message, fail_silently=True)
            messages.success(request, 'An email has been sent')
            return index(request)
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', context_args(request, {'form': form}))


@login_forbidden()
def reset_password(request):
    form = ResetPasswordForm(request.POST)
    reset_hash = request.POST.get('reset_hash')
    if form.is_valid():
        reset = PasswordReset.get_by_hash(request, reset_hash)
        if reset['result'] is False:
            messages.error(request, reset['error'])
        else:
            PasswordReset.reset_user_password(request, request.POST.get('password'), reset['email'])
            messages.success(request, 'Password Changed')

        return render(request, 'index.html', context_args(request))
    return render(request, 'resetPassword.html', context_args(request, {'form': form, 'reset_hash': reset_hash}))


@login_forbidden()
def reset_password_page(request, reset_hash):
    form = ResetPasswordForm()
    return render(request, 'resetPassword.html', context_args(request, {'form': form, 'reset_hash': reset_hash}))


@login_required
def photo_detail(request, photo_id):
    photo = Photo.objects.filter(id=photo_id, is_deleted=0)
    if len(photo) < 1:
        messages.error(request, 'Not found')
        return index(request)
    return render(request, 'photo.html', context_args(request, {'photo': photo[0]}))


@csrf_exempt
def snippet_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def snippet_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        snippet = Snippet.objects.get(pk=pk)
    except Snippet.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = SnippetSerializer(snippet)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(snippet, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        snippet.delete()
        return HttpResponse(status=204)


@csrf_exempt
@api_view(['GET', 'POST'])
def photo_list(request, format=None):
    """
    List all or create a photo.
    """
    if request.method == 'GET':
        photos = Photo.objects.all()
        serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def photo_detail(request, pk, format=None):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        photo = Photo.objects.get(pk=pk)
    except Snippet.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        serializer = PhotoSerializer(photo)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PhotoSerializer(photo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        photo.delete()
        return Response(status=204)


class PhotoList(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)


    def get(self, request, format=None):
        photos = Photo.objects.all()
        serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PhotoDetail(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def get_object(self, pk):
        try:
            return Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        photo = self.get_object(pk)
        serializer = PhotoSerializer(photo)
        return HttpResponse(serializer.data)

    def put(self, request, pk, format=None):
        photo = self.get_object(pk)
        serializer = PhotoSerializer(photo, data=request.data)
        if serializer.is_valid():
            return HttpResponse(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        photo = self.get_object(pk)
        photo.delete()
        return Response(status=204)


class PhotoListMixin(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     generics.GenericAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PhotoDetailMixin(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       generics.GenericAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class PhotoListRestMixin(generics.ListCreateAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer


class PhotoDetailRestMixin(generics.RetrieveUpdateDestroyAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'usersapi': reverse('user-list', request=request, format=format),
        'snippetsapi': reverse('snippet-list', request=request, format=format),
        'photosapi': reverse('photo-list', request=request, format=format)
    })


class SnippetHighlight(generics.GenericAPIView):
    queryset = Snippet.objects.all()
    renderer_classes = (renderers.StaticHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)


class PhototHighlight(generics.GenericAPIView):
    queryset = Photo.objects.all()
    renderer_classes = (renderers.StaticHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        photo = self.get_object()
        return Response(photo.title)

