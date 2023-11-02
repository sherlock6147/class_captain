from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from base.views import prepare_context
from classroom.models import Classroom
from booking.models import Booking
from base.models import(
    Professor,
    Student,
)
from access_management.utils import get_classrooms_for_user,get_professors_for_classroom
import pendulum
from django.contrib import messages

# Create your views here.

repeat_choices = {
    'no_repeat':'No Repeat',
    'weekday_repeat':'Repeat only on Weekdays',
    'weekend_repeat':'Repeat only on Weekends',
    'daily_repeat':'Repeat Daily',
}

def check_conflicts(unsaved_booking):
    return []

@login_required
def detail_view(request, classroom_id):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    classroom = Classroom.objects.get(id=classroom_id)
    context['classroom'] = classroom
    context['bookings'] = Booking.objects.filter(classroom = classroom, expiry__gte=pendulum.now(tz="Asia/Kolkata"))
    return render(request, 'pages/view_classroom.html',context)

def list_all(request):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not(is_admin or is_professor or is_student):
        return redirect('base:profile')
    bookings = []
    if is_admin:
        bookings = Booking.objects.all()
    if is_professor or is_student:
        valid_classrooms = get_classrooms_for_user(request)
        for room in valid_classrooms:
            room_bookings = Booking.objects.filter(classroom=room)
            if room_bookings.exists():
                for bk in room_bookings:
                    bookings.append(bk)
    new_bookings = []
    if is_student:
        student = Student.objects.get(user=request.user)
        for bk in bookings:
            new_booking = bk
            if bk.suggested_by == student:
                new_booking.can_delete = True
            else:
                new_booking.can_delete = False
            new_bookings.append(new_booking)
    else:
        new_bookings = bookings
    context['bookings'] = new_bookings
    print(context)
    return render(request,'pages/bookings.html',context)

@login_required
def add_booking(request, classroom_id):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not (is_admin or is_professor or is_student):
        return redirect('base:profile')
    context['classrooms'] = get_classrooms_for_user(request)
    if classroom_id is not None:
        classroom = Classroom.objects.get(id=classroom_id)
        context['selected_classroom'] = classroom
    context['professors'] = get_professors_for_classroom(classroom)
    if request.method == 'POST':
        if 'save' in request.POST:
            classroom_id = request.POST.get('classroom_id')
            classroom = Classroom.objects.get(id=classroom_id)
            date = request.POST.get('date')
            expiry = request.POST.get('expiry')
            end_time = request.POST.get('end_time')
            start_time = request.POST.get('start_time')
            name = request.POST.get('name')
            repeat = request.POST.get('repeat')
            unsaved_booking = Booking()
            unsaved_booking.name = name
            unsaved_booking.classroom = classroom
            unsaved_booking.date = pendulum.from_format(date,"DD/MM/YYYY",tz='Asia/Kolkata').date()
            unsaved_booking.expiry = pendulum.from_format(expiry,"DD/MM/YYYY, hh:mm A",tz='Asia/Kolkata')
            unsaved_booking.repeatable = repeat_choices[repeat]
            unsaved_booking.start_time = pendulum.parse(start_time, strict=False,tz='Asia/Kolkata').time()
            unsaved_booking.end_time = pendulum.parse(end_time, strict=False,tz='Asia/Kolkata').time()
            if (unsaved_booking.end_time > unsaved_booking.start_time) and (unsaved_booking.expiry.date() >= unsaved_booking.date):
                conflicts = check_conflicts(unsaved_booking)
                if not conflicts:
                    if is_professor:
                        prof = Professor.objects.get(user=request.user)
                        unsaved_booking.approved_by = prof
                        unsaved_booking.booked_for = prof
                        unsaved_booking.booked_by = prof
                    if is_student:
                        booked_for_prof_id = request.POST.get('booked_for_prof_id')
                        approval_prof_id = request.POST.get('approval_prof_id')
                        student = Student.objects.get(user=request.user)
                        b_prof = Professor.objects.get(id=booked_for_prof_id)
                        a_prof = Professor.objects.get(id=approval_prof_id)
                        unsaved_booking.suggested_by = student
                        unsaved_booking.booked_for = b_prof
                        unsaved_booking.approval_for = a_prof
                    unsaved_booking.save()
                    messages.success(request,'Succesfully booked classroom '+classroom.name)
                    return redirect(f'/booking/view/classroom/{classroom_id}')
                else:
                    messages.error(request, 'Conflicts with existing bookings')
    return render(request, 'pages/add_booking.html',context)

def delete_booking(request, booking_id):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    booking = Booking.objects.get(id=booking_id)
    classroom = booking.classroom
    if is_student:
        student = Student.objects.get(user=request.user)
        if booking.suggested_by == student:
            booking.delete()
            messages.success(request,'Deleted booking by student')
    if is_professor:
        # prof = Professor.objects.get(user=request.user)
        classrooms = get_classrooms_for_user(request)
        if classroom in classrooms:
            booking.delete()
            messages.success(request,'Deleted Booking by Professor')
    if is_admin:
        booking.delete()
        messages.success(request,'Deleted Booking by Admin')
    return redirect('booking:list_all')

@login_required
def approve_booking(request, booking_id):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    booking = Booking.objects.get(id=booking_id)
    if not (booking.approved_by == None):
        return redirect('base:profile')
    if not is_professor:
        return redirect('base:profile')
    prof = Professor.objects.get(user=request.user)
    conflicts = check_conflicts(booking)
    print(conflicts)
    if not conflicts:
        booking.approved_by = prof
        booking.save()
        messages.success(request, 'Booking Approved!')
    else:
        messages.error(request, 'THe booking conflicts with the timings')
    return redirect('base:profile')