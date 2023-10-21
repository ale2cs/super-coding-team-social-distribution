"""socialdistribution URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from social.views import CustomLoginView
from social.forms import LoginUser
from django.conf import settings
from django.conf.urls.static import static
from social.views import ChangePasswordView

urlpatterns = [
    #path('social/', include('social.urls')),
    path('admin/', admin.site.urls),
    path('', include('social.urls')),
    path('login/', CustomLoginView.as_view(redirect_authenticated_user=True, template_name='login.html', authentication_form=LoginUser), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('password-change/', ChangePasswordView.as_view(), name='password_change'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
