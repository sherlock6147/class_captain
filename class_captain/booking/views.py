from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from base.views import prepare_context
from classroom.models import Classroom
from booking.models import Booking,generate_unsaved_booked_dates
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
    'weekly':'Weekly',
}

def check_conflicts(unsaved_booking:Booking):
    conflicts = []
    bookings_for_classroom = Booking.objects.filter(classroom=unsaved_booking.classroom, expiry__gte=pendulum.now()).exclude(approved_by=None)
    bookings_within_timeperiod:Booking = []
    for booking in bookings_for_classroom:
        if booking.start_time >= unsaved_booking.start_time and booking.start_time < unsaved_booking.end_time:
            bookings_within_timeperiod.append(booking)
        elif booking.end_time > unsaved_booking.start_time and booking.end_time <= unsaved_booking.end_time:
            bookings_within_timeperiod.append(booking)
    # print(bookings_within_timeperiod)
    bookings_within_timeperiod_and_dates = []
    booked_dates_for_unsaved_booking = generate_unsaved_booked_dates(unsaved_booking)
    unsaved_booking_set = set(booked_dates_for_unsaved_booking)
    # print("Booked Dates:\n")
    # print(unsaved_booking_set)
    for booking in bookings_within_timeperiod:
        booked_dates = [booking.date for booking in booking.booked_dates.all()]
        booked_dates_set = set(booked_dates)
        # print(booking)
        # print(booked_dates_set)
        intersection_set = booked_dates_set & unsaved_booking_set
        if intersection_set:
            new_conflict = {
                'booking':booking,
                'conflicting_dates':list(intersection_set)
            }
            conflicts.append(new_conflict)
            # print(intersection_set)
    print(conflicts)
    return conflicts

@login_required
def detail_view(request, classroom_id):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    classroom = Classroom.objects.get(id=classroom_id)
    context['classroom'] = classroom
    bookings = []
    if is_admin:
        bookings = Booking.objects.all()
    if is_professor or is_student:
        valid_classrooms = get_classrooms_for_user(request)
        for room in valid_classrooms:
            room_bookings = Booking.objects.filter(classroom=room,expiry__gte=pendulum.now(tz="Asia/Kolkata"))
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
                    unsaved_booking.generate_booked_dates()
                    messages.success(request,'Succesfully booked classroom '+classroom.name)
                    return redirect(f'/booking/view/classroom/{classroom_id}')
                else:
                    messages.error(request, 'Conflicts with existing bookings')
                    for conflict in conflicts:
                        date_str = ""
                        for d in conflict.get('conflicting_dates'):
                            date_str = str(d)+','
                        messages.info(request,
                                      "Conflicts with Booking "+conflict['booking'].name+" on the following dates or more:\n"+date_str
                                      )
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
            messages.success(request,'Deleted booking suggested by student')
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
        booking.generate_booked_dates()
        booking.save()
        messages.success(request, 'Booking Approved!')
    else:
        messages.error(request, 'The booking conflicts with the timings')
        for conflict in conflicts:
                    date_str = ""
                    for d in conflict.get('conflicting_dates'):
                        date_str = str(d)+','
                    messages.info(request,
                                    "Conflicts with Booking "+conflict['booking'].name+" on the following dates or more:\n"+date_str
                                    )
    return redirect('base:profile')

@csrf_exempt
def device_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            token = data.get('token', None)
            classroom = Classroom.objects.get(code=token)
            status = "AVAILABLE"
            current = pendulum.now(tz="Asia/Kolkata")
            all_approved_bookings_for_classroom = Booking.objects.filter(classroom=classroom, expiry__gte=current,start_time__lte=current.time(),end_time__gte=current.time(),booked_dates__date=current.date()).exclude(approved_by=None)
            all_approved_bookings_for_classroom_after = Booking.objects.filter(classroom=classroom, expiry__gte=current,start_time__gte=current.time(),booked_dates__date=current.date()).exclude(approved_by=None).order_by("start_time")
            current_booking = None
            for booking in all_approved_bookings_for_classroom:
                if booking.booked_dates.filter(date=current.date()).exists():
                    status = "BOOKED"
                    current_booking = booking
                    break
            row1 = ""
            row2 = ""
            if status == "BOOKED":
                row1 = f"Booked By Prof. {current_booking.booked_for.user.name}"
                row2 = f"{current_booking.name} From {current_booking.start_time.strftime('%H:%M')} till {current_booking.end_time.strftime('%H:%M')}"
            else:
                start_time = "19:00"
                if all_approved_bookings_for_classroom_after.exists():
                    for booking in all_approved_bookings_for_classroom_after:
                        start_time = booking.start_time.strftime("%H:%M")
                        break
                row1 = f"{classroom.name}"
                row2 = f"Available Till {start_time}"
            len1 = len(row1)
            len2 = len(row2)
            if len2 > len1:
                spaces = " "
                while(len2 > len1):
                    len2 -= 1
                    spaces += " "
                row1 = row1 + spaces
            elif len1 > len2:
                spaces = " "
                while(len1 > len2):
                    len1 -= 1
                    spaces += " "
                row2 = row2 + spaces
            response_data = {
                'row1': row1,
                'row2': row2
            }

            # Convert the response data to JSON
            response_json = json.dumps(response_data)

            # Send the JSON response with the appropriate content type
            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)