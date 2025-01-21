#!/usr/bin/venv python3
import uuid
from django.db import models

from auths.models import CompanyProfile, StudentProfile
# from auths.models import User


class Job(models.Model):
    """
    Represents a job posting.

    Attributes:
        title (CharField): The title of the job.
        company_name (CharField): The name of the company offering the job.
        monthly_salary (DecimalField): The monthly salary for the job.
        description (TextField): A detailed description of the job responsibilities and requirements.
        location (CharField): The location of the job.
        no_of_opening (PositiveIntegerField): The number of available positions for this job.
        application_starting_date (DateField): The date when applications for this job begin.
        application_ending_date (DateField): The date when applications for this job close.
        active (BooleanField): Indicates whether the job posting is currently active. Defaults to False.
        job_requirements (TextField): A list of requirements for the job.
        job_thumbnail (ImageField): An image associated with the job posting.

    """
    title=models.CharField(null=True,blank=True,max_length=1000)
    company=models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, null=True, blank=True)
    monthly_salary=models.CharField(null=True,blank=True,max_length=100)
    description=models.TextField(null=True,blank=True)
    location=models.TextField(null=True,blank=True)
    no_of_opening=models.IntegerField(null=True,blank=True)
    application_starting_date = models.DateField(null=True, blank=True)
    application_ending_date = models.DateField(null=True, blank=True)
    active=models.BooleanField(default=True,null=True,blank=True)
    job_requirements=models.TextField(null=True,blank=True)
    job_thumbnail=models.FileField(upload_to='photos',null=True,blank=True)


    def __str__(self):
        return self.title
    
class ApplicationForm(models.Model):
    """
    Represents an application submitted for a job posting.

    Attributes:
        user (ForeignKey): The user who submitted the application.
        full_name (TextField): The full name of the applicant.
        email (EmailField): The email address of the applicant.
        phone_number (CharField): The phone number of the applicant.
        cover_letter (TextField): The applicant's cover letter.
        resume (FileField): The applicant's resume.
        job (ForeignKey): The Job object for which the application was submitted.
        application_date (DateField): The date and time when the application was submitted.
        job_status (TextField): The current status of the application (e.g., "under_review", "interviewed", "rejected").
    """
    full_name=models.TextField(null=True,blank=True)
    email=models.EmailField(null=True,blank=True)
    phone_number=models.CharField(max_length=15,null=True,blank=True)
    cover_letter=models.TextField(null=True,blank=True)
    resume=models.FileField(upload_to='photos',null=True,blank=True)
    job=models.ForeignKey(Job,on_delete=models.CASCADE,null=True,blank=True)
    application_date=models.DateField(auto_now_add=True,null=True,blank=True)
    job_status=models.TextField(null=True,blank=True,default="under_review")
    student=models.ForeignKey(StudentProfile, on_delete=models.CASCADE, null=True, blank=True)


    
    def __str__(self):
        return f"{self.student.full_name} applied for {self.job.title} job"
    

