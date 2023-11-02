from base.models import (
    Student,
    Professor,
)
from classroom.models import(
    Classroom
)
from access_management.models import(
    PAG,
    SAG,
)
from base.views import prepare_context

def get_classrooms_for_professor(professor):
    pags = PAG.objects.filter(professors=professor)
    classrooms = []
    if pags.exists():
        for pag in pags:
            for room in pag.classrooms.all():
                classrooms.append(room)
    classrooms_final = list(set(classrooms))
    return classrooms_final

def get_classrooms_for_student(student):
    sags = SAG.objects.filter(students=student)
    classrooms = []
    if sags.exists():
        for sag in sags:
            for room in sag.classrooms.all():
                classrooms.append(room)
    classrooms_final = list(set(classrooms))
    return classrooms_final

def get_classrooms_for_user(request):
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    classrooms = []
    if is_admin:
        classrooms = Classroom.objects.filter(ready=True)
    if is_professor:
        professor = Professor.objects.get(user=request.user)
        classrooms = get_classrooms_for_professor(professor)
    if is_student:
        student = Student.objects.get(user= request.user)
        classrooms = get_classrooms_for_student(student)
    return classrooms

def get_professors_for_classroom(classroom):
    professors = []
    pags = PAG.objects.filter(classrooms=classroom)
    if pags.exists():
        for pag in pags:
            for prof in pag.professors.all():
                professors.append(prof)
    professors = list(set(professors))
    return professors