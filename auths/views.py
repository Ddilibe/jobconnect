import uuid
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from auths.models import CompanyProfile, User, StudentProfile

def student_login(request):
    if request.method == 'POST':
        data = request.POST
        user = authenticate(request, username=data['email'], password=data['password'])
        if user and user.is_student:
            login(request, user)
            return redirect("studentdashboard")
    return render(request, "auth/student_login.html")

def student_signup(request):
    try:
        if request.method=='POST':
            full_name = request.POST.get("full_name")
            email = request.POST.get("email")
            phone_number = request.POST.get("phone_number")
            student_id = request.POST.get("student_id")
            gender = request.POST.get("gender")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            if password == confirm_password:
                user = User(public_id=uuid.uuid4(),email=email,is_active=True,is_company=False,is_student=True)
                user.set_password(password)
                user.save()
                profile = StudentProfile(user=user,gender=gender,phone_number=phone_number,student_id=student_id,full_name=full_name)
                profile.save()
                messages.success(request, "This is working")
                return redirect("studentlogin")
    except Exception as e:
        messages.error(request, str(e))
    return render(request, "auth/student_signup.html")

def admin_login(request):
    if request.method=='POST':
        data = request.POST
        user = authenticate(request, username=data['email'], password=data['password'])
        if user and user.is_company:
            login(request, user)
            return redirect("companydashboard")
    return render(request, "auth/company_login.html")

def admin_signup(request):
    try:
        if request.method=='POST':
            full_name = request.POST.get("full_name")
            email = request.POST.get("email")
            company_phone_number = request.POST.get("company_phone_number")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            company_name = request.POST.get("company_name")
            company_url = request.POST.get("company_url")
            company_address = request.POST.get("company_address")
            if password == confirm_password:
                user = User(public_id=uuid.uuid4(),email=email,is_active=True,is_company=True,is_student=False, username=full_name)
                user.set_password(password)
                user.save()
                profile = CompanyProfile(
                    user=user, address=company_address, company_name=company_name, company_phone_number=company_phone_number, company_url=company_url
                )
                profile.save()
                messages.success(request, "This is working")
                return redirect("adminlogin")
    except Exception as e:
        print(str(e))
        messages.error(request, str(e))
    return render(request, 'auth/company_signup.html')

def reset_password(request):
    return render(request, "auth/reset_password.html")

def change_password(request):
    return render(request, "auth/change_password.html")

def company_profile(request):
    return render(request, "job/company_profile.html")

def student_profile(request):
    return render(request, "job/student_profile.html",response.json())

def admin_profile(request):
    return render(request, "job/admin_profile.html")

def logout_view(request):
    logout(request)
    return redirect('index')