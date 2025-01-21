#!/usr/bin/env python3
from django.urls import path, include
import auths.views as job

urlpatterns = [
    path("admin-login", job.admin_login, name="adminlogin"),
    path("admin-signup", job.admin_signup, name="adminsignup"),
    path("admin-profile", job.admin_profile, name="adminprofile"),
    path('student-login', job.student_login, name="studentlogin"),
    path('student-signup', job.student_signup, name="studentsignup"),
    path("reset-password", job.reset_password, name="resetpassword"),
    path("change-password", job.change_password, name="changepassword"),
    path("student-profile", job.student_profile, name="studentprofile"),
    path("company-profile", job.company_profile, name="companyprofile"),
    path("logout", job.logout_view, name="logout")
]

