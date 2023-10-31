from django.shortcuts import render, redirect
from base.views import prepare_context
from django.contrib.auth.decorators import login_required
from classroom.models import(
    Building,
    Classroom,
)
from base.models import(
    Professor,
    Student,
)
from access_management.utils import(
    get_classrooms_for_professor,
    get_classrooms_for_student,
)
from django.contrib import messages
# Create your views here.
@login_required
def list_all(request):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    context['classrooms'] = []
    if is_admin:
        context['classrooms'] = Classroom.objects.filter(ready=True)
    if is_professor:
        professor = Professor.objects.get(user=request.user)
        context['classrooms'] = get_classrooms_for_professor(professor)
    if is_student:
        student = Student.objects.get(user= request.user)
        context['classrooms'] = get_classrooms_for_student(student)
    return render(request,'pages/classrooms.html',context)

@login_required
def add_classroom(request):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not is_admin:
        return redirect('base:profile')
    context['buildings'] = Building.objects.all().order_by('name')
    if request.method == 'POST':
        if 'save' in request.POST:
            building_id = request.POST.get('building_id')
            building = Building.objects.get(id=building_id)
            if building:
                name = request.POST.get('name')
                floor = request.POST.get('floor')
                seating_capacity = int(request.POST.get('seating_capacity'))
                whiteboard_available = False
                projector_available = False
                blackboard_available = False
                selected_options = request.POST.getlist('options')
                whiteboard_available = 'whiteboard' in selected_options
                projector_available = 'projector' in selected_options
                blackboard_available = 'blackboard' in selected_options
                new_classroom = Classroom()
                new_classroom.name = name
                new_classroom.building = building
                new_classroom.floor = floor
                new_classroom.seating_capacity = seating_capacity
                new_classroom.whiteboard_available = whiteboard_available
                new_classroom.projector_available = projector_available
                new_classroom.blackboard_available = blackboard_available
                new_classroom.save()
                messages.success(request, 'Added classroom '+name+'successfully')
                return redirect('classroom:list_all')
    return render(request,'pages/add_classroom.html',context)

def edit_classroom(request, classroom_id):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not is_admin:
        return redirect('base:profile')
    classroom = Classroom.objects.get(id=classroom_id)
    if not classroom:
        return redirect('base:profile')
    context['classroom'] = classroom
    context['buildings'] = Building.objects.all().order_by('name')
    if request.method == 'POST':
        if 'save' in request.POST:
            building_id = request.POST.get('building_id')
            building = Building.objects.get(id=building_id)
            if building:
                name = request.POST.get('name')
                floor = request.POST.get('floor')
                seating_capacity = int(request.POST.get('seating_capacity'))
                whiteboard_available = False
                projector_available = False
                blackboard_available = False
                selected_options = request.POST.getlist('options')
                whiteboard_available = 'whiteboard' in selected_options
                projector_available = 'projector' in selected_options
                blackboard_available = 'blackboard' in selected_options
                new_classroom = classroom
                new_classroom.name = name
                new_classroom.building = building
                new_classroom.floor = floor
                new_classroom.seating_capacity = seating_capacity
                new_classroom.whiteboard_available = whiteboard_available
                new_classroom.projector_available = projector_available
                new_classroom.blackboard_available = blackboard_available
                new_classroom.save()
                messages.success(request, 'Changes to  classroom '+name+' saved successfully')
                return redirect('classroom:list_all')
    return render(request,'pages/edit_classroom.html',context)

def delete_classroom(request, classroom_id):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not is_admin:
        return redirect('base:profile')
    classroom = Classroom.objects.get(id=classroom_id)
    if not classroom:
        return redirect('base:profile')
    classroom_name = classroom.name
    classroom.delete()
    messages.info(request, 'succesfully removed classroom '+ classroom_name)
    return redirect('classroom:list_all')

def detail_view(request, classroom_id):
    pass