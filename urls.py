"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
https://docs.djangoproject.com/en/5.1/topics/http/urls/    

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
from django.urls import path,include
from ecommerce import views
from django.conf import settings
from django.conf.urls.static import static
# from django.urls import include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('contact/', views.contact),
    # path('home/', views.home),
    path('about/', views.about),
    # path('help/', views.help),
    path('login/', views.login),
    # path('email/',views.email),
    path('register/', views.register),
    path('forgotPassword/', views.forgotPassword),
    path('productdetails/', views.productdetails),
    path('resetpassword/<token>',views.resetpassword),
    # path('send-email/', views.send_email),
    path('', views.product_list, name='product_list'),
    path('search/', views.search_products, name='search_products'),  
    path("adminapp/",include("adminapp.urls")),
    path("customerapp/",include("customerapp.urls")), 
    path('logout/',views.Logout),  

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





