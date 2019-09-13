"""oncall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf import settings
from django.urls import path, include
from django.conf.urls import url
from django.views.generic.base import RedirectView, TemplateView

from roster import views
from roster.models import Roster, Toil


urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('add_user/', views.users, name='add_user'),
    path('contact_info/', views.contact, name='contact_info'),
    path('update_roster/',views.update, name='update'),
    path('search/',views.search, name='search'),
    path('add_new_date/',views.add_roster_date, name='add_roster_date'),
    path('ajax_return_oncall/',views.ajax_return_oncall),
    path('ajax_return_changelog/',views.ajax_return_changelog),
    path('toilbalance/',views.toilbalance, name='toilbalance'),
    path('toilsummary/',views.toilsummary, name='toilsummary'),
    path('update_toil/', views.toilupdate, name='update_toil'),
    path('accounts/', include('django.contrib.auth.urls')),
]
