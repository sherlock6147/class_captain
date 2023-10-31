from django.shortcuts import render, redirect
from base.views import prepare_context
from access_management.models import (
    PAG,
    SAG,
    Professor,
    Student,
    Classroom,
)
from django.contrib import messages

# Create your views here.
def list_PAG(request):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not is_admin:
        return redirect('base:profile')
    context['pags'] = PAG.objects.filter()
    return render(request,'pages/list_PAG.html',context)

def list_SAG(request):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not (is_admin or is_professor):
        return redirect('base:profile')
    context['sags'] = SAG.objects.filter()
    return render(request,'pages/list_SAG.html',context)

def add_PAG(request):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not is_admin:
        return redirect('base:profile')
    context['professors'] = Professor.objects.all().order_by('user__name')
    context['classrooms'] = Classroom.objects.all().order_by('name')
    if request.method == "POST":
        if 'save' in request.POST:
            classroom_ids = request.POST.getlist('classrooms')
            prof_ids = request.POST.getlist('professors')
            name = request.POST.get('name')
            new_group = PAG()
            new_group.name = name
            new_group.save_base()
            for cl_id in classroom_ids:
                cl_obj = Classroom.objects.get(id=cl_id)
                new_group.classrooms.add(cl_obj)
            for prof in prof_ids:
                prof_obj = Professor.objects.get(id=prof)
                new_group.professors.add(prof_obj)
            new_group.save()
            messages.success(request, 'Create group '+name)
            return redirect('access:list_PAG')
    return render(request, 'pages/add_pag.html', context)

def add_SAG(request):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not (is_admin or is_professor):
        return redirect('base:profile')
    context['students'] = Student.objects.all().order_by('user__name')
    context['classrooms'] = Classroom.objects.all().order_by('name')
    if request.method == "POST":
        if 'save' in request.POST:
            classroom_ids = request.POST.getlist('classrooms')
            student_ids = request.POST.getlist('students')
            name = request.POST.get('name')
            new_group = SAG()
            new_group.name = name
            new_group.save_base()
            
            for cl_id in classroom_ids:
                cl_obj = Classroom.objects.get(id=cl_id)
                new_group.classrooms.add(cl_obj)
            for st_id in student_ids:
                student_obj = Student.objects.get(id=st_id)
                new_group.students.add(student_obj)
            new_group.save()
            messages.success(request, 'Successfully created student group '+name)
            return redirect('access:list_SAG')
    return render(request, 'pages/add_sag.html', context)

def edit_SAG(request,sag_id):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not (is_admin or is_professor):
        return redirect('base:profile')
    context['students'] = Student.objects.all().order_by('user__name')
    context['classrooms'] = Classroom.objects.all().order_by('name')
    sag = SAG.objects.get(id=sag_id)
    context['sag'] = sag
    if request.method == "POST":
        if 'save' in request.POST:
            classroom_ids = request.POST.getlist('classrooms')
            student_ids = request.POST.getlist('students')
            name = request.POST.get('name')
            new_group = sag
            new_group.name = name
            new_group.save_base()
            new_group.classrooms.clear()
            for cl_id in classroom_ids:
                cl_obj = Classroom.objects.get(id=cl_id)
                new_group.classrooms.add(cl_obj)
            new_group.students.clear()
            for st_id in student_ids:
                student_obj = Student.objects.get(id=st_id)
                new_group.students.add(student_obj)
            new_group.save()
            messages.success(request, 'Saved changes to  group '+name)
            return redirect('access:list_SAG')
    return render(request, 'pages/edit_sag.html', context)

def edit_PAG(request,pag_id):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not is_admin:
        return redirect('base:profile')
    context['professors'] = Professor.objects.all().order_by('user__name')
    context['classrooms'] = Classroom.objects.all().order_by('name')
    pag = PAG.objects.get(id=pag_id)
    context['pag'] = pag
    if request.method == "POST":
        if 'save' in request.POST:
            classroom_ids = request.POST.getlist('classrooms')
            prof_ids = request.POST.getlist('professors')
            name = request.POST.get('name')
            new_group = pag
            new_group.name = name
            new_group.save_base()
            new_group.classrooms.clear()
            for cl_id in classroom_ids:
                cl_obj = Classroom.objects.get(id=cl_id)
                new_group.classrooms.add(cl_obj)
            new_group.professors.clear()
            for prof in prof_ids:
                prof_obj = Professor.objects.get(id=prof)
                new_group.professors.add(prof_obj)
            new_group.save()
            messages.success(request, 'Saved changes to  group '+name)
            return redirect('access:list_PAG')
    return render(request, 'pages/edit_pag.html', context)


def delete_SAG(request,sag_id):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not (is_admin or is_professor):
        return redirect('base:profile')
    sag = SAG.objects.get(id=sag_id)
    sag.delete()
    return redirect('access:list_SAG')

def delete_PAG(request,pag_id):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not is_admin:
        return redirect('base:profile')
    pag = PAG.objects.get(id=pag_id)
    pag.delete()
    return redirect('access:list_PAG')

def view_SAG(request,sag_id):
    return None

def view_PAG(request,pag_id):
    return None
