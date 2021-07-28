from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db.models import Q , Subquery

from django.http import HttpResponse
from django.core.paginator import Paginator
from collections import Counter

from user import models as user_model
from medic import models as medic_model
from .models import *

import datetime


# views

# error
def error(request):
	return render(request, "main/error.html" , {'page_title':'Error'} )




# basic validation functions
#checking if doctor
def user_is_doctor(request):
	if request.user.user_type != user_model.User.USER_TYPE_DOC:
		messages.info(request, 'Error. Only doctos can access this page')
		return False
	else:
		return True


def user_is_doc_asst(request):
	if request.user.user_type == user_model.User.USER_TYPE_DOC:
		return
		# if the user is doctor, then of course he should NOT get this error
		# because a doctor has access to all the features that an asst. can access
	
	if request.user.user_type != user_model.User.USER_TYPE_DOC_ASST:
		messages.info(request, 'Error. Only Doctos Assistants can access this page')
		return False
	else:
		return True


def get_appointment_history_list(user):
	obj = medic_model.Appointment.objects.filter(patient=user).order_by('-schedule__start_date')
	return obj


# view related functions
def home(request):
	if request.user.is_authenticated:
		return user_home(request)
	else:
		return search_page(request)

def search_page(request):
	context = { 
		'page_title' : 'Search',
	}

	if request.GET.get('keyword',False) :
		context['page_title'] = 'Search Result'
		search_text = request.GET['keyword']
		context['search_text'] = search_text

		if request.GET.get('checkbox_doc', False):
			context['doc_checked'] = True
			context['doctors'] = user_model.DoctorProfile.objects.filter( 
					Q(user__first_name__icontains=search_text) |
					Q(user__last_name__icontains=search_text) |
					Q(bio_desc__icontains=search_text) |
					Q(education__icontains=search_text) |
					Q(field__icontains=search_text) |
					Q(seach_tags__icontains=search_text) |
					Q(user__address__icontains=search_text) |
					Q(user__city__icontains=search_text) |
					Q(user__district__icontains=search_text)
					).filter(apprived=True).order_by('-review_rating')
		if request.GET.get('checkbox_Hospital', False):
			context['hospital_checked'] = True
			context['hospitals'] = medic_model.Hospital.objects.filter( 
					Q(name__icontains=search_text) |
					Q(additional_info__icontains=search_text) |
					Q(name_in_google_maps__icontains=search_text) |
					Q(address__icontains=search_text) |
					Q(city__icontains=search_text) |
					Q(district__icontains=search_text)
					).filter(active=True)
		
		return render(request, "main/search_result.html" , context )

	return render(request, "main/search.html" , context )

@login_required
def user_home(request):
	context = { 
		'page_title' : 'Home',
	}
	if request.user.is_superuser:
		return redirect('/admin/') #redirect to admin page if admin

	if request.user.user_type == user_model.User.USER_TYPE_PATIENT:
		obj = get_appointment_history_list(request.user)
		context['object'] = obj.filter(status=medic_model.Appointment.STATUS_CONFIRMED)
		return render(request, "main/home-user.html" , context )
	
	elif request.user.user_type == user_model.User.USER_TYPE_DOC:
		context['new_activity'] = len( DoctorAsstReq.objects.filter(doctor__id=request.user.doctorprofile.id) ) # + profile info by asst
		context['appointment_today'] = medic_model.Appointment.objects.filter(schedule__start_date=datetime.date.today())
		return render(request, "main/home-doctor.html" , context )
	else : 
		appointment_list_2_sided(request, context)
		return render(request, "main/home-asst.html" , context )


def manage_appointment(request):
	context = {'page_title' : 'Manage Appointments'}
	appointment_list_2_sided(request, context, user_is_doc_asst=False)
	return render(request, "main/home-asst.html" , context )


def appointment_list_2_sided(request, context, user_is_doc_asst=True):
	context['user_is_doc_asst'] = user_is_doc_asst
	context['awaiting_appointment_list'] = get_appointment_list(request.user, request.GET.get('page'))
	context['confirmed_appointment_list'] = get_appointment_list(request.user, request.GET.get('page'), confirmed_only=True)

	# print("===============================================================================")
	# now = datetime.now()
	# test= datetime.combine( context['confirmed_appointment_list'][0].schedule.start_date , context['confirmed_appointment_list'][0].schedule.end_time )
	# print(now < test)

	if request.method=='POST':
		accept_appointment_req(request)

	return render(request, "main/home-asst.html" , context )


@login_required
def welcome(request):
	context = {
		'page_title':'Welcome',
		'user_type_doc': user_model.User.USER_TYPE_DOC,
		'user_type_patient': user_model.User.USER_TYPE_PATIENT,
		'user_type_docasst': user_model.User.USER_TYPE_DOC_ASST,
	}

	# if doctor
	if request.user.user_type == user_model.User.USER_TYPE_DOC:
		context['profile'] = request.user.doctorprofile

	return render(request, "main/welcome.html" , context )


def user_login(request):
	return render(request, "main/signin.html" , {'page_title' : 'Login',} )


def doc_list(request):
	context = {
		'page_title' : 'Doctor\'s List',
		'doc_list' : user_model.DoctorProfile.objects.all().order_by('-review_rating'),
	}

	if request.GET.get('search', False):
		search_text = request.GET.get('search', False)
		context['search'] = search_text
		context['search_result'] = search_doctor(search_text)

	return render(request, "main/doctors_list.html" , context )



def doc_schedule(request):
	doc_id = None 
	user_is_doctor = False 

	if request.GET.get('doc', False) == False and hasattr(request.user, 'doctorprofile') :
		doc_id = request.user.doctorprofile.id
		user_is_doctor = True


	if request.GET.get('doc', False) or doc_id:
		if doc_id==None:
			doc_id = request.GET.get('doc', '') #getting the doctor id from GET req param
		
		#initializing with None, value will be assigned if no error
		error_msg = None
		doc = None
		obj = None
		
		try:
			#check if doc exists or not
			if len(user_model.DoctorProfile.objects.filter(id=doc_id))==0:
				error_msg = {'message':'Doctor not found', 'tag':'warning'}
			else:
				obj = medic_model.DoctorsSchedule.objects.filter(doctor=doc_id) #valid id is <int>
				doc = user_model.DoctorProfile.objects.get(id=doc_id)
				if len(obj)==0: #if no schedule found
					error_msg = {'message':'No Schedule found for this Doctor', 'tag':'warning'}
		except Exception as e: #if invalid id given in GET param (ie: string)
			error_msg = {'message':'Invalid Parameter', 'tag':'danger'}

		context = { 
			'object_list' : obj ,
			'doc': doc,
			'page_title' : 'Schedule',
			'error': error_msg,
		}
	else:
		context = {
			'page_title': 'Error',
			'error': {'message':'No Parameter found', 'tag':'danger'}
		}

	context['user_is_doctor'] = user_is_doctor

	return render(request, "medic/doctorsschedule_list.html" , context )


@login_required
def assistant_activity(request):
	if user_is_doctor(request):
		req_list = DoctorAsstReq.objects.filter(doctor=request.user.doctorprofile.id)
		my_asst_list = DocAsstProfile.objects.filter(doctor=request.user.doctorprofile.id)

		if len(my_asst_list) == 0: # if no assassin exists (intentional typo lol)
			my_asst_list = False

		if len(req_list) == 0:
			req_list = False

		context = {
			'page_title' : 'Assistant Activity',
			'req_list' : req_list,
			'my_asst_list' : my_asst_list,
		}

		return render(request, "main/assistant_activity.html" , context )
	return redirect('error')


@login_required
def search_assistant(request):
	if user_is_doctor(request):
		search_result = None
		num_of_result = None

		if request.GET.get('search',False):
			search_text = request.GET['search']
			if search_text.isnumeric() :
				search_result = DocAsstProfile.objects.filter(id=search_text)
			else:
				search_result = DocAsstProfile.objects.filter( 
					Q(user__first_name__icontains=search_text) |
					Q(user__last_name__icontains=search_text)
					)
			num_of_result = len(search_result)

		context = {
			'page_title' : 'Search Assistant',
			'search_result' : search_result,
			'num_of_result' : num_of_result,
		}

		return render(request, "main/search_assistant.html" , context )
	return redirect('error')



@login_required
def add_assistant(request):
	if user_is_doctor(request):
		# if method is post
		if request.method == 'POST':
			try:
				# retreiving the assistant profile
				doc_asst = DocAsstProfile.objects.filter(id=request.POST['asst_id']).first()

				if doc_asst.doctor: #if already someone's assistant
					messages.error(request, f'Error: This person has already been added as assistant by another doctor.')
					return redirect('error')

				doc_asst.doctor = request.user.doctorprofile #setting the doc
				doc_asst.save()

				# delete the join_request instance
				if request.POST.get('req_id',False):
					join_req_to_del = DoctorAsstReq.objects.get(id=request.POST['req_id'])
					join_req_to_del.delete()

				# adding the success message
				messages.success(request, f'Assistant added successfully')
				return redirect('assistant-activity')
			except Exception as e:
				messages.error(request, 'An unknown error has occured. Please contact an admin')
				return redirect('error')
			
		# if method is get
		if request.method == 'GET':
			assistant = None

			if request.GET.get('assistant',False):
				asst_id = int(request.GET['assistant'])
				assistant = DocAsstProfile.objects.filter(id=asst_id).first()
			else:
				messages.warning(request, f'Error: No Parameter Found')

			context = {
				'page_title' : 'Add Assistant',
				'asst' : assistant,
			}

			return render(request, "main/add_assistant.html" , context )
	return redirect('error')



@login_required
def del_asst_join_req(request):
	if user_is_doctor(request):
		if request.GET.get('req_id',False):
			req = DoctorAsstReq.objects.get(id=request.GET['req_id'])
			req.delete()

			messages.success(request, f'Request deleted')

			return redirect('assistant-activity')
	
	return redirect('error')


@login_required
def req_to_join(request):
	if user_is_doc_asst(request):
		if request.method == "POST":
			# retreiving and setting the info
			doctor = DoctorProfile.objects.get(id=request.POST['doctor_id'])
			additional_info = request.POST['additional_info']

			# creating the new req instance and saving it
			new_req = DoctorAsstReq(doctor=doctor, asst=request.user.docasstprofile, additional_info=additional_info)
			new_req.save()

			# showing the success message and redirecting
			messages.success(request, f'Request sent successfully. Please wait until the doctor checks your request')
			return redirect('user-home')
		
		if request.method == "GET" and request.GET.get('doc',False):
			if request.GET['doc'].isnumeric():
				try:
					doctor = DoctorProfile.objects.get(id=request.GET['doc'])
				except Exception as e:
					messages.warning(request, f'No doctor not found with the given id')
					return redirect('error')

				context = {
					'page_title' : 'Request to join as an Assistant',
					'doctor' : doctor,
				}
				return render(request, "main/req_to_join.html" , context )
			else:
				messages.error(request, f'Invalid Parameter Found')

		else:
			messages.error(request, f'No Parameter Found')
	
	return redirect('error')


def search_doctor(search_text, order_by='-review_rating'):
	search_result = DoctorProfile.objects.filter(
		Q(user__first_name__icontains=search_text) |
		Q(user__last_name__icontains=search_text) |
		Q(education__icontains=search_text) | 
		Q(field__icontains=search_text) | 
		Q(bio_desc__icontains=search_text) | 
		Q(seach_tags__icontains=search_text)
	).order_by(order_by)

	return search_result



def search_hospital(search_text):
	search_result = medic_model.Hospital.objects.filter(
		Q(name__icontains=search_text) |
		Q(phone_number__icontains=search_text) |
		Q(address__icontains=search_text) | 
		Q(city__icontains=search_text) | 
		Q(additional_info__icontains=search_text) | 
		Q(name_in_google_maps__icontains=search_text)
	)

	return search_result


@login_required
def doc_my_schedule(request):
	if user_is_doc_asst(request) or user_is_doctor(request) :
		if request.user.user_type == user_model.User.USER_TYPE_DOC :
			current_doc_id = request.user.doctorprofile.id
		else:
			current_doc_id = request.user.docasstprofile.doctor.id

		schedules = medic_model.DoctorsSchedule.objects.filter(doctor__id=current_doc_id).order_by('start_date')

		context = {
			'page_title' : 'My Schedule',
			'object_list' : schedules,
		}
		return render(request, 'main/doc_schedule.html' , context)
	else:
		return redirect('error')



@login_required
def calendar(request):
	context = {
		'page_title' : 'Calendar',
		'do_not_draw_header' : True,
	}

	return render(request, 'main/calendar.html' , context)


def get_appointment_list(user, page_number = False, confirmed_only = False):
	if user.user_type == user_model.User.USER_TYPE_DOC :
		doc = user.doctorprofile
	elif user.user_type == user_model.User.USER_TYPE_DOC_ASST:
		doc = user.docasstprofile.doctor

	# code to fetch the list
	if confirmed_only :
		query_set = medic_model.Appointment.objects.filter(schedule__doctor=doc, status=medic_model.Appointment.STATUS_CONFIRMED).order_by('schedule__start_date')
	else:
		query_set = medic_model.Appointment.objects.filter(schedule__doctor=doc, status=medic_model.Appointment.STATUS_AWAITING_CONFIRMATION).order_by('schedule__start_date')

	# pagination
	paginator = Paginator(query_set, 10) ######### Update it later

	page_obj = paginator.get_page(page_number)

	return page_obj


def accept_appointment_req(request):
	# validation : doctor/docasst
	# not needed as this function is only called from the user_home function when the user is a docasst

	if request.user.user_type == user_model.User.USER_TYPE_DOC :
		doc = request.user.doctorprofile
	elif request.user.user_type == user_model.User.USER_TYPE_DOC_ASST :
		doc = request.user.docasstprofile.doctor
	
	# check id to see if the req belongs to the current doc/docasst
	#getting the appointment using the id
	req_id = request.POST.get('req_id')
	appointment = medic_model.Appointment.objects.get(id=req_id)

	if appointment.schedule.doctor == doc:
		appointment.status = medic_model.Appointment.STATUS_AWAITING_PAYMENT
		appointment.save()
		messages.success(request, 'Appointment request accepted successfully')
		return redirect('/')
	else : 
		messages.error(request, 'Error. You do not have the permission to accept/reject this appointment request.')
		return redirect('error')

	return



@login_required
def notifications(request):
	context = {
		'page_title' : 'Notifications',
		'notifications' : Notification.objects.filter(user=request.user).order_by('seen'), 
	}
	return render(request, 'main/notifications.html' , context)


@login_required
def mark_notification_as_read(request):
	try:
		notification_id = request.GET['id']
		notification = Notification.objects.get(id=notification_id)

		if notification.user == request.user:
			notification.seen = True
			notification.save()
		else:
			return HttpResponse("Not your naughty-fication ;)")
	except Exception as e:
		return HttpResponse(f"e")

	return HttpResponse("Notification marked as read.") #return nothing , just process (will be called using ajax)


def check_for_notification(request):
	if request.user.is_authenticated:
		output = Notification.objects.filter(user=request.user).filter(seen=False).count()
		if output>0:
			return HttpResponse('y') # Yes: New notification is available
		else:
			return HttpResponse('n') # No : New notfification is not available
	else:
		return HttpResponse("Login Required") #when user not logged in




def pay_dummy(request):
	context = {
		'page_title' : 'Pay (dummy)'
	}

	if request.method == "POST" : 
		appointment_id = request.POST['appointment_id']
		appointment = medic_model.Appointment.objects.get(id=appointment_id)

		if appointment.patient == request.user :
			appointment.status = medic_model.Appointment.STATUS_CONFIRMED
			appointment.save()
			messages.success(request, 'Appointment Confirmed')
			return redirect(f'/appointment/{appointment_id}')
		else: 
			messages.warning(request, "This is not your appointment")
			return redirect('error')

	if request.GET.get('appointment', False) : 
		appointment_id = request.GET['appointment']
		appointment = medic_model.Appointment.objects.get(id=appointment_id)

		if appointment.patient == request.user :
			context['appointment'] = appointment
		else: 
			messages.warning(request, "This is not your appointment")
			return redirect('error')

	else: 
		messages.warning(request, 'Parameter missing')
		return redirect('error')

	return render(request, 'main/pay_dummy.html', context)