from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.admin.views.decorators import staff_member_required
from services.models import Booking, Technician, ServiceCategory
from django.db.models import Sum
from django.contrib import messages

def admin_login(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate by username
        user = authenticate(request, username=username_or_email, password=password)

        # If username fails, try email
        if not user:
            from django.contrib.auth.models import User
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or not an admin.")

    return render(request, 'admin_login.html')


@staff_member_required
def admin_dashboard(request):
    bookings = Booking.objects.all().order_by('-created_at')
    technicians = Technician.objects.all()
    categories = ServiceCategory.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        # ADD TECHNICIAN
        if action == 'add_tech':
            Technician.objects.create(
                name=request.POST['name'],
                role_id=request.POST['role'],
                phone=request.POST['phone']
            )
            messages.success(request, "Technician added successfully.")

        # ASSIGN / CHANGE TECHNICIAN
        elif action == 'assign_tech':
            booking_id = request.POST.get('booking_id')
            tech_id = request.POST.get('tech')

            if not tech_id:
                messages.error(request, "Please select a technician before assigning.")
                return redirect('admin_dashboard')

            booking = Booking.objects.get(id=booking_id)
            tech = Technician.objects.get(id=tech_id)

            booking.technician = tech
            booking.status = 'Assigned'
            booking.save()

            messages.success(request, f"{tech.name} assigned to booking.")

        # MARK DONE
        elif action == 'mark_done':
            booking_id = request.POST.get('booking_id')
            booking = Booking.objects.get(id=booking_id)
            booking.status = 'Done'
            booking.save()

            messages.success(request, "Booking marked as Done.")

        return redirect('admin_dashboard')

    # Technician stats
    tech_stats = []
    for t in technicians:
        completed = Booking.objects.filter(technician=t, status='Done')
        tech_stats.append({
            'technician': t,
            'total_tasks': completed.count(),
            'total_earned': completed.aggregate(Sum('service__price'))['service__price__sum'] or 0
        })

    return render(request, 'admin_dashboard.html', {
        'bookings': bookings,
        'categories': categories,
        'tech_stats': tech_stats
    })
