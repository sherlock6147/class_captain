from django.shortcuts import render, redirect
from django.contrib.auth.decorators import(
    login_required,
)
from base.models import(
    Professor,
    Student,
    SecretToken,
    Department,
)
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
import pendulum, datetime

# Create your views here.
input_format = "DD/MM/YYYY, hh:mm A"

def prepare_context(request):
    context = {}
    context['is_admin'] = False
    context['is_professor'] = False
    context['is_student'] = False
    if Professor.objects.filter(user=request.user).count() > 0:
        context['is_professor'] = True
    if Student.objects.filter(user=request.user).count() > 0:
        context['is_student'] = True
    if request.user.is_superuser or request.user.is_staff:
        context['is_admin'] = True
    # print(context,request.user.is_superuser, request.user.is_staff)
    return context

def home(request):
    context  = {}
    return render(request, 'pages/home.html', context)

@login_required
def profile(request):
    context = {}
    context = prepare_context(request)
    user = request.user
    social_account = SocialAccount.objects.filter(user=user).first()
    profile_img = None
    if social_account:
        profile_img = social_account.extra_data.get('picture')
    context['profile_img'] = profile_img
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    context['needs_profile'] = False
    if (not is_professor) and (not is_student) and (not is_admin):
        context['needs_profile'] = True
        messages.info(request, 'Please complete account creation for furthur usage.')
    else:
        if is_student:
            context['student'] = Student.objects.get(user=request.user)
        if is_professor:
            context['prof'] = Professor.objects.get(user=request.user)
    return render(request, 'pages/profile.html', context)

def view_secret_tokens(request):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    context['tokens'] = None
    if is_professor or is_admin:
        if not is_admin:
            messages.info(request, 'Can only create Student-level access tokens.')
            context['tokens'] = SecretToken.objects.filter(token_type=SecretToken.TOKEN_TYPES['Student']).order_by('-created_on')
        else:
            context['tokens'] = SecretToken.objects.all().order_by('-created_on')
    else:
        return redirect('base:home')
    return render(request, 'pages/tokens.html', context)

@login_required
def delete_secret(request, secret_id):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if is_admin or is_professor:
        secret = SecretToken.objects.get(id=int(secret_id))
        if secret:
            messages.info("Successfully deleted token.")
            secret.delete()
    return redirect('base:view_secret_tokens')

def add_secret(request):
    context = {}
    context = prepare_context(request)
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not (is_admin or is_professor):
        return redirect('base:profile')
    # print('EXPIRY_______________________\n',request.POST.get('expiry'))
    if request.method == 'POST':
        if 'add_token' in request.POST:
            allowed_roles = []
            if is_admin:
                allowed_roles.append('PROF')
            if is_professor or is_admin:
                allowed_roles.append('STUD')
            token_type = request.POST.get('token_type')
            if token_type:
                if token_type in allowed_roles:
                    new_token = SecretToken()
                    if token_type == 'PROF':
                        new_token.token_type = 'Professor'
                    if token_type == 'STUD':
                        new_token.token_type = 'Student'
                    parsed_datetime = pendulum.from_format(request.POST.get('expiry'), input_format)
                    new_token.expiry = parsed_datetime
                    new_token.save()
                    messages.success(request, 'Succesfully created token')
                    return redirect('base:view_secret_tokens')
    return render(request, 'pages/add_token.html', context)

@login_required
def register_professor(request):
    context = {}
    context = prepare_context(request)
    context['departments'] = Department.objects.all().order_by('-name')
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if is_admin or is_professor or is_student:
        return redirect('base:profile')
    if request.method == 'POST':
        if 'save' in request.POST:
            mobile = request.POST.get('mobile')
            dept_id = request.POST.get('dept_id')
            department = Department.objects.get(id= dept_id)
            secret = request.POST.get('secret')
            is_secret_valid = False
            if secret:
                token = SecretToken.objects.filter(code=secret).first()
                if not token:
                    messages.error(request,'Secret code enterred is wrong.')
                else:
                    if token.expiry > pendulum.now():
                        if token.token_type == 'Professor':
                            is_secret_valid = True
                        else:
                            messages.info(request,'Your token is for student level access. Please use a professor level access token.')
                    else:
                        messages.info(request,'Your token has expired')
            if is_secret_valid and department:
                new_prof = Professor()
                new_prof.user = request.user
                new_prof.department = department
                new_prof.mobile = mobile
                new_prof.save()
                messages.success(request, 'Successfully registered as a Professor')
                return redirect('base:profile')
    return render(request, 'pages/register_prof.html', context)


@login_required
def register_student(request):
    context = {}
    context = prepare_context(request)
    context['departments'] = Department.objects.all().order_by('-name')
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if is_admin or is_professor or is_student:
        return redirect('base:profile')
    if request.method == 'POST':
        if 'save' in request.POST:
            mobile = request.POST.get('mobile')
            dept_id = request.POST.get('dept_id')
            roll = request.POST.get('roll')
            reg = request.POST.get('reg')
            department = Department.objects.get(id= dept_id)
            secret = request.POST.get('secret')
            is_secret_valid = False
            if secret:
                token = SecretToken.objects.filter(code=secret).first()
                if not token:
                    messages.error(request,'Secret code enterred is wrong.')
                else:
                    if token.expiry > pendulum.now():
                        if token.token_type == 'Student':
                            is_secret_valid = True
                        else:
                            messages.info(request,'Your token is for Professor level access. Please use a student level access token.')
                    else:
                        messages.info(request,'Your token has expired')
            if is_secret_valid and department:
                new_student = Student()
                new_student.user = request.user
                new_student.department = department
                new_student.roll = roll
                new_student.reg = reg
                new_student.mobile = mobile
                new_student.save()
                messages.success(request, 'Successfully registered as a Student')
                return redirect('base:profile')
    return render(request, 'pages/register_student.html', context)

@login_required
def edit_view(request):
    context = {}
    context = prepare_context(request)
    context['departments'] = Department.objects.all().order_by('-name')
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if (not is_professor) and (not is_student) and (not is_admin):
        return redirect('base:profile')
    if is_admin:
        messages.info(request, 'Edit info from django admin.')
    if is_professor:
        return redirect('base:edit_prof')
    if is_student:
        return redirect('base:edit_student')
    return redirect('base:profile')

@login_required
def edit_professor(request):
    context = {}
    context = prepare_context(request)
    context['departments'] = Department.objects.all().order_by('-name')
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not is_professor:
        return redirect('base:profile')
    prof = Professor.objects.get(user=request.user)
    if not prof:
        return redirect('base:profile')
    context['prof'] = prof
    if request.method == 'POST':
        if 'save' in request.POST:
            mobile = request.POST.get('mobile')
            dept_id = request.POST.get('dept_id')
            department = Department.objects.get(id= dept_id)
            if department:
                prof.department = department
                prof.mobile = mobile
                prof.save()
                messages.success(request, 'Edit Successfull')
                return redirect('base:profile')
    return render(request, 'pages/edit_prof.html', context)

@login_required
def edit_student(request):
    context = {}
    context = prepare_context(request)
    context['departments'] = Department.objects.all().order_by('-name')
    is_professor = context.get("is_professor", False)
    is_student = context.get("is_student", False)
    is_admin = context.get("is_admin", False)
    if not is_student:
        return redirect('base:profile')
    student = Student.objects.get(user=request.user)
    if not student:
        return redirect('base:profile')
    context['student'] = student
    if request.method == 'POST':
        if 'save' in request.POST:
            mobile = request.POST.get('mobile')
            dept_id = request.POST.get('dept_id')
            roll = request.POST.get('roll')
            reg = request.POST.get('reg')
            department = Department.objects.get(id= dept_id)
            if department:
                student.department = department
                student.mobile = mobile
                student.roll = roll
                student.reg = reg
                student.save()
                messages.success(request, 'Edit Successfull')
                return redirect('base:profile')
    return render(request, 'pages/edit_student.html', context)
