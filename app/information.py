from datetime import datetime, date
import os
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .utils.send_sms import *
from .models import *
#for pdf
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required


# global variables
today = date.today()




#TODO:Student
#read_student
@login_required
def read_student(request):
    students = Student.objects.filter(active=True,student_class__active=True).order_by('student_class__number','name')
    
    
    #get query parameters
    query = request.GET.get('query', '')
    student_class_query = request.GET.get('student_class_query', '')
    school_query = request.GET.get('school_query', '')
    location_query = request.GET.get('location_query', '')
    blood_query = request.GET.get('blood_query', '')
    religion_query = request.GET.get('religion_query', '')
    gender_query = request.GET.get('gender_query', '')
    marital_status_query = request.GET.get('marital_status_query', '')
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(mob_no__icontains=query) |
            Q(email__icontains=query) |
            Q(roll_no__icontains=query)
        )
    if student_class_query:
        students = students.filter(student_class__id=student_class_query)
    if school_query:
        students = students.filter(school__id=school_query)
    if location_query:
        students = students.filter(location__id=location_query)
    if blood_query:
        students = students.filter(blood=blood_query)
    if religion_query:
        students = students.filter(religion=religion_query)
    if gender_query:
        students = students.filter(gender=gender_query)
    if marital_status_query:
        students = students.filter(marital_status=marital_status_query)
        
        
    # pagination for main_leave
    paginator = Paginator(students, 50)  # 50 records per page
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "students": students,
        "query_string": query_string,
        "student_classes": StudentClass.objects.filter(active=True).order_by('number'),
        "schools": School.objects.all().order_by('name'),
        "locations": Location.objects.all().order_by('name'),
        "bloods": Student.BLOOD_LIST,
        "religions": Student.RELIGION_LIST,
        "genders": Student.GENDER_LIST,
        "marital_statuses": Student.MARITAL_STATUS_LIST,
        "query": query,
        "student_class_query": int(student_class_query) if student_class_query else "",
        "school_query": int(school_query) if school_query else "",
        "location_query": int(location_query) if location_query else "",
        "blood_query": blood_query,
        "religion_query": religion_query,
        "gender_query": gender_query,
        "marital_status_query": marital_status_query,
        "inactive": False
    }
    return render(request,'student/read_student.html',context)

@login_required
def read_inactive_student(request):
    students = Student.objects.filter(Q(active=False) | Q(student_class__active=False)).order_by('student_class__number','name')
    
    #get query parameters
    query = request.GET.get('query', '')
    student_class_query = request.GET.get('student_class_query', '')
    school_query = request.GET.get('school_query', '')
    location_query = request.GET.get('location_query', '')
    blood_query = request.GET.get('blood_query', '')
    religion_query = request.GET.get('religion_query', '')
    gender_query = request.GET.get('gender_query', '')
    marital_status_query = request.GET.get('marital_status_query', '')
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(mob_no__icontains=query) |
            Q(email__icontains=query) |
            Q(roll_no__icontains=query)
        )
    if student_class_query:
        students = students.filter(student_class__id=student_class_query)
    if school_query:
        students = students.filter(school__id=school_query)
    if location_query:
        students = students.filter(location__id=location_query)
    if blood_query:
        students = students.filter(blood=blood_query)
    if religion_query:
        students = students.filter(religion=religion_query)
    if gender_query:
        students = students.filter(gender=gender_query)
    if marital_status_query:
        students = students.filter(marital_status=marital_status_query)
        
        
    # pagination for main_leave
    paginator = Paginator(students, 50)  # 50 records per page
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "students": students,
        "query_string": query_string,
        "student_classes": StudentClass.objects.filter(active=True).order_by('number'),
        "schools": School.objects.all().order_by('name'),
        "locations": Location.objects.all().order_by('name'),
        "bloods": Student.BLOOD_LIST,
        "religions": Student.RELIGION_LIST,
        "genders": Student.GENDER_LIST,
        "marital_statuses": Student.MARITAL_STATUS_LIST,
        "query": query,
        "student_class_query": int(student_class_query) if student_class_query else "",
        "school_query": int(school_query) if school_query else "",
        "location_query": int(location_query) if location_query else "",
        "blood_query": blood_query,
        "religion_query": religion_query,
        "gender_query": gender_query,
        "marital_status_query": marital_status_query,
        "inactive": True
    }
    return render(request,'student/read_student.html',context)

#create_student
@login_required
def create_student(request):
    if request.method == 'POST':
        # ✅ Extract Required Fields
        name = request.POST.get('name')
        school_id = request.POST.get('school')
        student_class_id = request.POST.get('student_class')
        mob_no = request.POST.get('mob_no')
        gender = request.POST.get('gender')
        location_id = request.POST.get('location') or None
        email = request.POST.get('email')
        roll_no = request.POST.get('roll_no')
        father_name = request.POST.get('father_name')
        mother_name = request.POST.get('mother_name')
        date_of_birth = request.POST.get('date_of_birth') or None
        father_mob_no = request.POST.get('father_mob_no')
        mother_mob_no = request.POST.get('mother_mob_no')
        marital_status = request.POST.get('marital_status')
        blood = request.POST.get('blood')
        religion = request.POST.get('religion')
        
        # ✅ Manual Required Validation
        if not all([name, school_id, student_class_id, mob_no]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('create_student')

        # ✅ Create Student Object
        student = Student(name=name, school_id=school_id, student_class_id=student_class_id, location_id=location_id, mob_no=mob_no, email=email, roll_no=roll_no, father_name=father_name, mother_name=mother_name, date_of_birth=date_of_birth, father_mob_no=father_mob_no, mother_mob_no=mother_mob_no, gender=gender, marital_status=marital_status, blood=blood, religion=religion, active=True)

        # ✅ Handle Picture Upload
        if request.FILES.get('picture'):
            student.picture = request.FILES['picture']

        student.save()
        messages.success(request, 'Student added successfully.')
        return redirect('create_student')
    
    context = {
        'schools': School.objects.all().order_by('name'),
        'locations': Location.objects.all().order_by('name'),
        'student_classes': StudentClass.objects.filter(active=True).order_by('number'),
        'genders': Student.GENDER_LIST,
        'bloods': Student.BLOOD_LIST,
        'religions': Student.RELIGION_LIST,
        'marital_statuses': Student.MARITAL_STATUS_LIST
    }
    return render(request,'student/create_student.html',context)

#update_student
@login_required
def update_student(request,id):
    student = get_object_or_404(Student, id=id)
    if request.method == 'POST':
        student.name = request.POST.get('name')
        student.school_id = request.POST.get('school')
        student.student_class_id = request.POST.get('student_class')
        student.location_id = request.POST.get('location') or None
        student.mob_no = request.POST.get('mob_no')
        student.email = request.POST.get('email')
        student.roll_no = request.POST.get('roll_no')
        student.father_name = request.POST.get('father_name')
        student.mother_name = request.POST.get('mother_name')
        student.date_of_birth = request.POST.get('date_of_birth') or None
        student.father_mob_no = request.POST.get('father_mob_no')
        student.mother_mob_no = request.POST.get('mother_mob_no')
        student.gender = request.POST.get('gender')
        student.marital_status = request.POST.get('marital_status')
        student.blood = request.POST.get('blood')
        student.religion = request.POST.get('religion')
        if request.FILES.get('picture'):
            student.picture = request.FILES['picture']
        student.save()
        messages.success(request, 'Student updated successfully.')
        return redirect('read_student')

    context = {
        'student': student,
        'schools': School.objects.all().order_by('name'),
        'locations': Location.objects.all().order_by('name'),
        'student_classes': StudentClass.objects.filter(active=True).order_by('number'),
        'genders': Student.GENDER_LIST,
        'bloods': Student.BLOOD_LIST,
        'religions': Student.RELIGION_LIST,
        'marital_statuses': Student.MARITAL_STATUS_LIST
    }
    return render(request,'student/update_student.html',context)

#delete_student
@login_required
def delete_student(request,id):
    student = Student.objects.get(id=id)
    messages.success(request,f"{student.name} was deleted successfully.")
    return redirect(read_student)

#activation_student
@login_required
def activation_student(request,id):
    student = Student.objects.get(id=id)
    if student.active == True:
        student.active = False
        student.inactive_date = today
        messages.success(request,f"{student.name} was deactivation successfully.")
    else:
        student.active = True
        student.inactive_date = None
        student.join_date = today
        messages.success(request,f"{student.name} was activation successfully.")
    student.save()
    return redirect(read_student)




#TODO:Teacher
#read_teacher
@login_required
def read_teacher(request):
    teachers = Teacher.objects.filter(active=True).order_by('name')
    
    
    query = request.GET.get('query', '')
    if query:
        teachers = teachers.filter(
            Q(name__icontains=query) |
            Q(mob_no__icontains=query) |
            Q(email__icontains=query)
        )
    
    
    # pagination for main_leave
    paginator = Paginator(teachers, 50)  # 50 records per page
    page_number = request.GET.get('page')
    teachers = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "teachers":teachers,
        "query_string": query_string,
        "query": query,
        "inactive": False
    }
    return render(request,'teacher/read_teacher.html',context)

@login_required
def read_inactive_teacher(request):
    teachers = Teacher.objects.filter(active=False).order_by('name')
    
    #get query parameters
    query = request.GET.get('query', '')
    if query:
        teachers = teachers.filter(
            Q(name__icontains=query) |
            Q(mob_no__icontains=query) |
            Q(email__icontains=query)
        )
    # pagination for main_leave
    paginator = Paginator(teachers, 50)  # 50 records per page
    page_number = request.GET.get('page')
    teachers = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "teachers":teachers,
        "query_string": query_string,
        "query": query,
        "inactive": True,
    }
    return render(request,'teacher/read_teacher.html',context)

#create_teacher
@login_required
def create_teacher(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mob_no = request.POST.get('mob_no')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('date_of_birth') or None
        marital_status = request.POST.get('marital_status')
        blood = request.POST.get('blood')
        religion = request.POST.get('religion')
        location_id = request.POST.get('location') or None

        if not all([name, mob_no]):
            messages.error(request, "Name, Mobile No, and Gender are required.")
            return redirect('create_teacher')

        teacher = Teacher.objects.create(name=os.name, mob_no=mob_no, gender=gender, email=email, date_of_birth=date_of_birth, marital_status=marital_status, blood=blood, religion=religion, location_id=location_id, active=True)


        if request.FILES.get('picture'):
            teacher.picture = request.FILES['picture']

        teacher.save()
        messages.success(request, "Teacher created successfully.")
        return redirect('create_teacher')

    context = {
        'genders': Teacher.GENDER_LIST,
        'bloods': Teacher.BLOOD_LIST,
        'religions': Teacher.RELIGION_LIST,
        'marital_statuses': Teacher.MARITAL_STATUS_LIST,
        'locations': Location.objects.all().order_by('name'),
    }
    return render(request,'teacher/create_teacher.html',context)

#update_teacher
@login_required
def update_teacher(request,id):
    teacher = get_object_or_404(Teacher, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        mob_no = request.POST.get('mob_no')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('date_of_birth') or None
        marital_status = request.POST.get('marital_status')
        blood = request.POST.get('blood')
        religion = request.POST.get('religion')
        location_id = request.POST.get('location') or None

        # Optional: Validate required fields
        if not all([name, mob_no]):
            messages.error(request, "Name, Mobile No are required.")
            return redirect('update_teacher', id=id)

        # Update fields
        teacher.name = name
        teacher.mob_no = mob_no
        teacher.gender = gender
        teacher.email = email
        teacher.date_of_birth = date_of_birth
        teacher.marital_status = marital_status
        teacher.blood = blood
        teacher.religion = religion
        teacher.location_id = location_id

        if request.FILES.get('picture'):
            teacher.picture = request.FILES['picture']

        teacher.save()
        messages.success(request, "Teacher updated successfully.")
        return redirect('read_teacher')

    # GET request — show the form with existing data
    context = {
        'teacher': teacher,
        'locations': Location.objects.all().order_by('name'),
        'genders': Teacher.GENDER_LIST,
        'bloods': Teacher.BLOOD_LIST,
        'religions': Teacher.RELIGION_LIST,
        'marital_statuses': Teacher.MARITAL_STATUS_LIST,
    }
    return render(request,'teacher/update_teacher.html',context)

#delete_teacher
@login_required
def delete_teacher(request,id):
    teacher = Teacher.objects.get(id=id)
    messages.success(request,f"{teacher.name} was deleted successfully.")
    return redirect(read_teacher)

#activation_teacher
@login_required
def activation_teacher(request,id):
    teacher = Teacher.objects.get(id=id)
    if teacher.active == True:
        teacher.active = False
        teacher.inactive_date = today
        messages.success(request,f"{teacher.name} was deactivation successfully.")
    else:
        teacher.active = True
        teacher.inactive_date = None
        messages.success(request,f"{teacher.name} was activation successfully.")
    teacher.save()
    return redirect(read_teacher)






@login_required
def read_student_pdf(request,inactive=False):
    if inactive == "True":
        students = Student.objects.filter(Q(active=False) | Q(student_class__active=False)).order_by('student_class__number','name')
    else:
        students = Student.objects.filter(active=True,student_class__active=True).order_by('student_class__number','name')
    
    #get query parameters
    query = request.GET.get('query', '')
    student_class_query = request.GET.get('student_class_query')
    school_query = request.GET.get('school_query')
    location_query = request.GET.get('location_query')
    blood_query = request.GET.get('blood_query', '')
    religion_query = request.GET.get('religion_query', '')
    gender_query = request.GET.get('gender_query', '')
    marital_status_query = request.GET.get('marital_status_query', '')
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(mob_no__icontains=query) |
            Q(email__icontains=query) |
            Q(roll_no__icontains=query)
        )
    if student_class_query:
        students = students.filter(student_class__id=student_class_query)
    if school_query:
        students = students.filter(school__id=school_query)
    if location_query:
        students = students.filter(location__id=location_query)
    if blood_query:
        students = students.filter(blood=blood_query)
    if religion_query:
        students = students.filter(religion=religion_query)
    if gender_query:
        students = students.filter(gender=gender_query)
    if marital_status_query:
        students = students.filter(marital_status=marital_status_query)
        
    context = {
        "students": students
    }
    # Load the HTML template and render it with context data
    template = get_template('pdf/read_student_pdf.html')
    html = template.render(context)

    # Create a response with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="students.pdf"'

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    
    return response



@login_required
def read_teacher_pdf(request,inactive=False):
    if inactive == "True":
        teachers = Teacher.objects.filter(active=False).order_by('name')
    else:
        teachers = Teacher.objects.filter(active=True).order_by('name')
    
    #get query parameters
    query = request.GET.get('query', '')
    if query:
        teachers = teachers.filter(
            Q(name__icontains=query) |
            Q(mob_no__icontains=query) |
            Q(email__icontains=query)
        )
        
    context = {
        "teachers": teachers
    }
    # Load the HTML template and render it with context data
    template = get_template('pdf/read_teacher_pdf.html')
    html = template.render(context)

    # Create a response with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="teachers.pdf"'

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    
    return response


