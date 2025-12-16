from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ServiceCategory, Service, Booking
from .forms import BookingForm
from django.db.models import Q

def category_list(request):
    categories = ServiceCategory.objects.all()
    return render(request, 'service_category.html', {'categories': categories})

def service_list(request, category_id=None):
    query = request.GET.get('q')

    if category_id:
        # If category ID is provided, show services of that category
        category = get_object_or_404(ServiceCategory, id=category_id)
        services = Service.objects.filter(category=category)
    else:
        # If no category, show all services
        category = None
        services = Service.objects.all()

    # Apply search if query exists
    if query:
        services = services.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    return render(request, 'service_list.html', {
        'services': services,
        'category': category,
        'query': query,
    })

@login_required
def booking_create(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.service = service
            booking.save()
            return redirect('profile')
    else:
        form = BookingForm()

    return render(request, 'booking_form.html', {
        'form': form,
        'service': service
    })

@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status != "Done":
        return redirect('profile')
    if request.method == "POST":
        booking.review = request.POST.get("review")
        booking.save()
        return redirect('profile')
    return render(request, "add_review.html", {"booking": booking})

@login_required
def booking_edit(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.technician:
        return redirect('profile')
    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = BookingForm(instance=booking)
    return render(request, "booking_form.html", {'form': form, 'service': booking.service})

@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.technician:
        return redirect('profile')
    if request.method == "POST":
        booking.delete()
        return redirect('profile')
    return render(request, "booking_cancel.html", {"booking": booking})
