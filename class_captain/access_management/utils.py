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