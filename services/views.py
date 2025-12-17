from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import ServiceCategory, Service, Booking
from .forms import BookingForm


def category_list(request):
    categories = ServiceCategory.objects.all()
    return render(request, 'service_category.html', {'categories': categories})


def service_list(request, category_id=None):
    query = request.GET.get('q')

    if category_id:
        category = get_object_or_404(ServiceCategory, id=category_id)
        services = Service.objects.filter(category=category)
    else:
        category = None
        services = Service.objects.all()

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
            messages.success(request, "Booking created successfully.")
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
        messages.error(request, "You can only review completed services.")
        return redirect('profile')

    if request.method == "POST":
        booking.review = request.POST.get("review")
        booking.save()
        messages.success(request, "Review added successfully.")
        return redirect('profile')

    return render(request, "add_review.html", {"booking": booking})


@login_required
def booking_edit(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # 🔒 BLOCK editing
    if booking.status == "Done" or booking.technician:
        messages.error(request, "This booking cannot be edited.")
        return redirect('profile')

    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, "Booking updated successfully.")
            return redirect('profile')
    else:
        form = BookingForm(instance=booking)

    return render(
        request,
        "booking_form.html",
        {'form': form, 'service': booking.service}
    )


@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # 🔒 BLOCK cancelling
    if booking.status == "Done" or booking.technician:
        messages.error(request, "This booking cannot be cancelled.")
        return redirect('profile')

    if request.method == "POST":
        booking.delete()
        messages.success(request, "Booking cancelled successfully.")
        return redirect('profile')

    return render(request, "booking_cancel.html", {"booking": booking})
