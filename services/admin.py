


from django.contrib import admin
from .models import ServiceCategory, Service, Technician, Booking

admin.site.register(ServiceCategory)
admin.site.register(Service)
admin.site.register(Technician)
admin.site.register(Booking)
