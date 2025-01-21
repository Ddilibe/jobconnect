from auths.models import CompanyProfile, User, StudentProfile
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, FileResponse
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from job.models import Job, ApplicationForm
from django.core.paginator import Paginator
from django.conf import settings
import os


def landing_page(request):
    return render(request, "landing_page.html")

def about_us(request):
    return render(request, "about_us.html")

def contact_us(request):
    return render(request, "contact_us.html")

def job_list_post(request):
    jobs = Job.objects.all()
    length = 10 
    query = request.GET.get("query")  

    if query:
        filtered_jobs = [job for job in jobs if query.lower() in job['title'].lower()]
    else:
        filtered_jobs = jobs 

    # Set up pagination
    pages = Paginator(filtered_jobs, length)
    page_number = request.GET.get("page", 1)
    page_obj = pages.get_page(page_number)

    context = {
        'jobs': filtered_jobs[(int(page_number) * length) - length: (int(page_number) * length)], 
        'page_obj': page_obj,
    }

    if query:
        context['query'] = query

    return render(request, "job/job_list.html", context)

def job_single(request, primary_key):
    single=Job.objects.filter(pk=primary_key).first()
    if not single:
        return redirect("joblistpost")
    return render(request, 'dashboard/student/detailed_saved_job.html', context={'job':single})

"""
    START OF THE STUDENT PART
"""

def student_dashboard(request):
    if request.user.is_anonymous:
        return redirect('studentlogin') 
    if not request.user.is_anonymous and request.user.is_company:
        return redirect("companydashboard")
    student = StudentProfile.objects.get(user=request.user)
    active_jobs=ApplicationForm.objects.all().filter(student=student)

    list_of_jobs = [
        {
            "full_name":job_applied.full_name,
            "email":job_applied.email,
            "phone_number":job_applied.phone_number,
            "cover_letter":job_applied.cover_letter,
            'pk': job_applied.pk,
        } for job_applied in active_jobs
    ]
    context= {
        "name":student.full_name,
        "applied_jobs": list_of_jobs,
        "recommended_jobs": list_of_jobs,
        "saved_jobs": list_of_jobs
    }
    return render(request, "dashboard/student_dashboard.html", context)


def applied_job(request, job_id):
    if request.user.is_anonymous:
        return redirect('studentlogin') 
    if not request.user.is_anonymous and request.user.is_company:
        return redirect("companydashboard")
    print(job_id)
    appl = ApplicationForm.objects.get(pk=job_id)
    single = appl.job
    content = {'job': single, "leav": "this is it", "apply": appl}
    return render(request, "dashboard/student/applied_job.html", content)

def detailed_saved_job(request, job_id):
    if request.user.is_anonymous:
        return redirect('studentlogin') 
    if not request.user.is_anonymous and request.user.is_company:
        return redirect("companydashboard")
    company=CompanyProfile.objects.get(user=request.user)
    global jobs  # Remove this if jobs is fetched within the function

    # Check the HTTP method
    if request.method == 'POST':
        if 'title' in request.POST:
            print(f"POST Title: {request.POST['title']}")
        else:
            print("POST request made but no 'title' found in the request data.")
        return redirect('index')  # Redirect to index or handle POST differently if needed
    
    # Handle GET request
    single = next((job for job in jobs if job.get('pk') == job_id), None)
    
    if not single:
        print(f"No job found with ID: {job_id}")
        return redirect('index')  # Redirect if job not found

    # Log the job details for debugging
    print(f"Job found: {single}")

    # Save job details in the session for use across views
    request.session['job_title'] = single.get('title', 'Unknown Title')
    request.session['job_description'] = single.get('description', 'No Description Available')

    # Make job details available in the view directly (for debugging or further logic)
    job_title = single.get('title', 'Unknown Title')
    job_description = single.get('description', 'No Description Available')

    # Log session data
    print(f"Session data saved - Title: {job_title}, Description: {job_description}")
    return render(request, 'dashboard/student/detailed_saved_job.html', {"job": single})

"""
    Section for job application
"""

def apply_job(request, job_id):
    if request.user.is_anonymous:
        return redirect('studentlogin') 
    if not request.user.is_anonymous and request.user.is_company:
        return redirect("companydashboard")
    job=Job.objects.get(pk=job_id)
    return render(request, "job/applied_job.html", {'job':job})


def successful_submission(request, job_id):
    if request.user.is_anonymous:
        return redirect('studentlogin') 
    if not request.user.is_anonymous and request.user.is_company:
        return redirect("companydashboard")
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        cover_letter = request.POST['cover_letter']
        
        resume = request.FILES['resume']
        job = Job.objects.get(pk=job_id)
        student=StudentProfile.objects.get(user=request.user)
        if ApplicationForm.objects.filter(job=job, student=student).exists():
            return redirect("studentdashboard")
        application_data = ApplicationForm(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            cover_letter=cover_letter,
            resume=resume,
            job=job,
            student=student,
        )
        application_data.save()
        return render(request, "job/successful_submission.html", dict(full_name=full_name,
            email=email,
            phone_number=phone_number,
            cover_letter=cover_letter,))
    return redirect("apply-job", job_id)

def withdraw_application(request, job_id):
    if request.user.is_anonymous:
        return redirect('studentlogin') 
    if not request.user.is_anonymous and request.user.is_company:
        return redirect("companydashboard")
    
    if request.method == 'POST':
        return redirect('studentdashboard')
    elif request.method == "GET":
        if not (single := [i for i in jobs if i['pk'] == job_id]):
            return redirect('index')
        single = single[0]
        content = {'job': single}
        return render(request, "job/withdraw_application.html", content)
    else:
        return redirect('studentdashboard')

"""
    END OF THE STUDENT SECTION
"""

"""
    START OF THE COMPANY ADMIN SECTION
"""

def download_cv(request, filename):
    # Construct the full path to the file
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        # Serve the file as a response
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    else:
        # Handle file not found
        return HttpResponse("File not found.", status=404)
    
def company_dashboard(request):
    if request.user.is_anonymous:
        return redirect('adminlogin')
    if not request.user.is_anonymous and request.user.is_student:
        return redirect("studentdashboard")
    company=CompanyProfile.objects.get(user=request.user)
    list_of_jobs=Job.objects.all().filter(company=company)
    jobs=[]
    for  job in list_of_jobs:

        jobs.append(
            {
                "pk": str(job.pk),
                "title": job.title,
                "company_name": company.company_name,
                "place": job.location,
                "monthly_salary":job.monthly_salary,
                "no_of_opening":job.no_of_opening,
                "application_starting_date":job.application_starting_date,
                "application_ending_date":job.application_ending_date,
                "description":job.description,
                "job_thumbnail":job.job_thumbnail,
                "job_requirements":job.job_requirements
            }
        )

    total_jobs=Job.objects.filter(company=company).count()
    # current_jobs=jobs.filte
    total_applicants_count=ApplicationForm.objects.filter(job__company=company).count()
    
    return render(request, "dashboard/company_dashboard.html", {'jobs':jobs,'total_applicants_count':total_applicants_count,'total_jobs':total_jobs,"full_name": request.user.username,"company_name":company.company_name})

def post_job(request, job_id=None):
    if request.user.is_anonymous:
        return redirect('adminlogin')
    if not request.user.is_anonymous and request.user.is_student:
        return redirect("studentdashboard")
    company=CompanyProfile.objects.get(user=request.user)
    try:
        if request.method == 'POST':
            title = request.POST['title']
            monthly_salary = request.POST['monthly_salary']
            description = request.POST['description']
            location=request.POST['location']
            no_of_opening=request.POST['no_of_opening']
            
            application_starting_date = request.POST['application_starting_date']
            application_ending_date = request.POST['application_ending_date']
            job_requirements=request.POST['job_requirements']
            job_thumbnail = request.FILES['job_thumbnail']
            application_data = Job(
                title=title,
                company=company,
                monthly_salary=monthly_salary,
                description=description,
                location=location,
                no_of_opening=no_of_opening,
                application_starting_date=application_starting_date,
                application_ending_date=application_ending_date,
                job_requirements=job_requirements,
                active=True,
                job_thumbnail=job_thumbnail
            )
            # application_data.job_thumbnail.save(job_thumbnail.name, ContentFile(job_thumbnail))
            application_data.save()
            return redirect('companydashboard')
    except Exception as e:
        print(str(e))
    return render(request, 'dashboard/company/job_management.html')

def job_applications(request, job_id=None):
    if request.user.is_anonymous:
        return redirect("adminlogin")
    if not request.user.is_anonymous and request.user.is_student:
        return redirect("studentdashboard")
    company=CompanyProfile.objects.get(user=request.user)
    applicants=ApplicationForm.objects.all().filter(job__company=company)
    return render(request, 'dashboard/company/job_applications.html', {"applicants":applicants})

def redirect_to_company_dashboard(request):
    if not request.user.is_anonymous and request.user.is_company:
        return redirect("companydashboard")

def redirect_to_ctudent_dashboard(request):
    if not request.user.is_anonymous and request.user.is_student:
        return redirect("studentdashboard")