"""PhotoReel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from Photo.views import *
from PhotoReel import settings


admin.autodiscover()



# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'snippets', SnipperViewSet)
router.register(r'photos', PhotoViewSet)

# router.register(r'api/class/photo', PhotoList)


urlpatterns = [
    url(r'^$', index, name='home'),
    url(r'^profile/$', profile, name='profile'),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout_user, name='logout'),
    url(r'^signup/$', signup, name='signup'),
    url(r'^save_photo/$', save_photo, name='save_photo'),
    url(r'^forgot_password/$', forgot_password, name='forgot_password'),
    url(r'^reset_password/$', reset_password, name='reset_password'),
    url(r'^reset_password/(?P<reset_hash>[\w|\W]+)/$', reset_password_page, name='serve_reset_page'),
    url(r'^photos/([0-9]+)/$', photo_detail, name='get_single_photo'),

    url(r'^api/', include(router.urls)),
    url(r'^api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^api/snippet/$', snippet_list),
    url(r'^api/snippet/(?P<pk>[0-9]+)/$', snippet_detail),

    url(r'^api/photo/$', photo_list),
    url(r'^api/photo/(?P<pk>[0-9]+)/$', photo_detail),

    url(r'^api/class/photo/$', PhotoList.as_view()),
    url(r'^api/class/photo/(?P<pk>[0-9]+)/$', PhotoDetail.as_view()),

    url(r'^users/$', UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', UserDetail.as_view()),

    url(r'^apis/$', api_root),
    url(r'^snippetsapis/(?P<pk>[0-9]+)/highlight/$', SnippetHighlight.as_view()),
    url(r'^photosapis/(?P<pk>[0-9]+)/highlight/$', PhototHighlight.as_view()),

    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns = format_suffix_patterns(urlpatterns)

