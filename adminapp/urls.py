from django.urls import path
from adminapp import views


urlpatterns = [
path('', views.home),
path('addproduct/', views.addproduct),
path('addproductimage/',views.addproductimage),
path('managecustomer/',views.managecustomer),
path('managecustomerstatus/',views.managecustomerstatus),
path('viewproduct/',views.viewproduct),
path('deleteproduct/', views.deleteproduct),
path('managecustomer/delete/',views.deletecustomer),
path('vieworders/',views.vieworders),
path('logout/',views.Logout),
path('deleteimage/', views.deleteimage, name='deleteimage'),
path('changeproductdetail/',views.changeproductdetail),

]