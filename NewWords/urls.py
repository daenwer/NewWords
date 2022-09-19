"""NewWords URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
import re

from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import re_path
from django.views.static import serve


from NewWords import settings
from app.views import TokenVerificationView, ForTestView

# app_name = "app"

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    # path('admin/', ForTestView.as_view(), name='admin'),
    path('login/<str:token>/', TokenVerificationView.as_view(), name='token'),

    # path('admin/', site.urls),
    path('', ForTestView.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
prefix = settings.STATIC_URL

urlpatterns += [
    re_path(
        r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')), serve, kwargs={}
    ),
]
# urlpatterns += staticfiles_urlpatterns()
