from django.urls import path
from . import views

app_name = 'canteen'

urlpatterns = [
    path('', views.menu, name='menu'),
    path('dish/<int:pk>/', views.dish_detail, name='dish_detail'),
    path('prebook/<int:dish_id>/', views.prebook_dish, name='prebook_dish'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cancel-order/<int:order_id>/', views.cancel_preorder, name='cancel_preorder'),
    
    # Staff/Admin URLs
    path('admin/dishes/', views.manage_dishes, name='manage_dishes'),
    path('admin/preorders/', views.manage_preorders, name='manage_preorders'),
]