from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product, name='product'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('order-now/', views.order_now, name='order_now'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<int:pk>/success/', views.order_success, name='order_success'),
    path('orders/<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
]
