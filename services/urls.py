from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.category_list, name='categories'),
    path('services/', views.service_list, name='all_services'),  # Global search across all services
    path('services/<int:category_id>/', views.service_list, name='service_list'),  # Category-specific
    path('booking/<int:service_id>/', views.booking_create, name='booking_create'),
    path('add-review/<int:booking_id>/', views.add_review, name='add_review'),
    path('booking/edit/<int:booking_id>/', views.booking_edit, name='booking_edit'),
    path('booking/cancel/<int:booking_id>/', views.booking_cancel, name='booking_cancel'),
]
