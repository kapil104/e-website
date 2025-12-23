from django.urls import path
from customerapp import views 


urlpatterns = [
path('', views.home),
# path('customerapp/', include('customerapp.urls')),
path('addtocart/', views.addtocart, name='addtocart'), 
path('addtocart/increment',views.increment),
path('addtocart/decrement',views.decrement),
path('changepassword/',views.changepassword),
path('editprofile/',views.editprofile),
path('payment/',views.payment),
path('paymentstatus/',views.paymentstatus),
path('viewprofile/',views.viewprofile),
path('addtocart/delete/', views.deleteproduct, name='deleteproduct'),
path('logout/',views.Logout),
path('productdetail/', views.productdetail, name='productdetail'),

] 


