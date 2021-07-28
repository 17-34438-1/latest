from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin



from django.utils.html import mark_safe

import datetime, pytz

from .models import *
import user.models as user_model

from main.views import user_is_doctor, search_doctor, search_hospital, user_is_doc_asst, get_appointment_history_list

from .forms import *

# Create your views here.
@login_required
def get_appointment(request):
	if request.GET.get('schedule', ''):
		schedule_id = request.GET.get('schedule', '') #getting the schedule id from GET req param
		#schedule = DoctorsSchedule.objects.get(id=schedule_id)
		appointment_list = Appointment.objects.filter(patient=request.user)
		

		for appointment in appointment_list:
			if appointment.schedule.id == int(schedule_id):
				messages.success(request, 'You have already booked this appointment.')
				return redirect('error') #################################################################
		
		#initializing with None, value will be assigned if no error
		error_msg = None
		obj = None
		
		try:
			#check if schedule exists or not
			if DoctorsSchedule.objects.filter(id=schedule_id).exists()==False :
				error_msg = {'message':'Schedule not found', 'tag':'warning'}
			else:
				obj = DoctorsSchedule.objects.filter(id=schedule_id).first() #valid id is <int>
		except Exception as e: #if invalid id given in GET param (ie: string)
			error_msg = {'message':'Invalid Parameter', 'tag':'danger'}

		context = { 
			'schedule' : obj ,
			'page_title' : 'Get Appointment',
			'error': error_msg,
		}
	else:
		context = {
			'page_title': 'Error',
			'error': {'message':'No Parameter found', 'tag':'danger'}
		}

	return render(request, "medic/get_appointment.html" , context)


@login_required
def appointment_history(request):
	obj = get_appointment_history_list(request.user)

	#bd_time_now = pytz.timezone("Asia/Dhaka").localize(datetime.datetime.now())

	context = {
		'object' : obj,
		'page_title' : 'Appointmet History',
		'num_of_appointments' : len(obj),
		#'now' : bd_time_now,
	}

	# for time in obj:
	# 	t = time.schedule.start_date_time
	# 	appointment_time = t.replace(tzinfo=bd_timezone)
	

	return render(request, "medic/appointment_history.html" , context)

@login_required
def create_hospital(request):
	if user_is_doctor(request):
		if request.user.doctorprofile.apprived == False:
			messages.error(request, 'Doctor Profile must be approved to be able to create Hospitals')
			return redirect('error')

		if request.method == "POST":
			form = CreateOrUpdateHospitalForm(request.POST)

			if form.is_valid() : 
				new_hospital = form.save(manager_doctor=request.user.doctorprofile)
				messages.success(request, 'Hospital Created Successfully')
				return redirect('my_hospitals')

		else:
			form = CreateOrUpdateHospitalForm()

		context = {
			'page_title' : 'Create Hospital',
			'form' : form,
			'error': False,
		}
		return render(request, "medic/create_hospital.html" , context)
	else:
		return redirect('error')


class HospitalListView(ListView):
	model = Hospital
	queryset = Hospital.objects.filter(active=True)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['page_title'] = 'Hospitals'
		return context


class HospitalEditView(UpdateView):
	template_name = 'medic/create_hospital.html'
	form_class = CreateOrUpdateHospitalForm
	queryset = Hospital.objects.all()
	success_url = 'done'

	error = False

	def get_object(self):
		if user_is_doctor(self.request):
			id_ = self.kwargs.get("id")
			current_doctor = self.request.user.doctorprofile
			obj = get_object_or_404(Hospital, id=id_)

			doc_is_a_manager = False

			for d in obj.managers.all():
				if d == current_doctor:
					doc_is_a_manager = True

			if doc_is_a_manager:
				return obj
			else:
				self.error = True
				messages.error(self.request , 'You are not a manager of this hospital')
		else:
			self.error = True
			messages.error(self.request , 'You are not a manager of this hospital')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['page_title'] = 'Update Hospital'
		context['update'] = True
		context['error'] = self.error
		if self.error == False : 
			context['hospital_image'] = self.get_object().image.url
		return context



def update_done(request):
	return render(request, 'medic/update_done.html' , {'page_title' : 'Done'})


@login_required
def doc_hospital_list(request):
	if user_is_doctor(request):
		# doc = DoctorProfile.objects.filter(id=request.user.doctorprofile.id)
		# my_hospitals = Hospital.objects.filter(managers__in=doc)
		my_hospitals = request.user.doctorprofile.manages.all()

		context = {
			'page_title' : 'My Hospital',
			'my_hospitals' : my_hospitals,
			'num_of_hospitals': len(my_hospitals),
		}
		
		return render(request, 'medic/my_hospitals-doctors.html', context )
	else:
		return redirect('error')




class HospitalDetailsView(DetailView):
	model = Hospital
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['page_title'] = context['object'].name
		return context


class AppointmentDetails(LoginRequiredMixin, DetailView):
	model = Appointment

	##############################################################################################################
	# do not forget to add "UserPassesTestMixin" 
	# enter validation here
	# def test_func(self):
	# 	if self.get_object().patient != self.request.user :
	# 		# or self.get_object().schedule.doctor != self.request.user.doctorprofile
	# 		messages.error(self.request, 'This is not your appointment.')
	# 		return False
	# 	else : 
	# 		return True

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['page_title'] = f"Appointment #{context['object'].id}"
		context['appointment_status_text'] = Appointment.STATUS_CHOICES[context['object'].status][1]
		if context['object'].status == 0 : # awaiting confirmation
			context['appointment_status_color'] = '#95a5a6'
		elif context['object'].status == 1 : # awaiting payment
			context['appointment_status_color'] = '#f39c12'
		elif context['object'].status == 2 : # confirmed
			context['appointment_status_color'] = '#27ae60'
		elif context['object'].status == 3 : # cancelled
			context['appointment_status_color'] = '#e74c3c'
		else:
			context['appointment_status_color'] = 'default'

		if self.request.user == context['object'].patient : 
			context['i_gotta_pay'] = True

		if self.request.user.user_type == user_model.User.USER_TYPE_PATIENT : 
			if self.request.user == context['object'].patient :
				context['my'] = True
			else : 
				context['my'] = False
				messages.warning(self.request , "Not your appointment")

		if self.request.user.user_type == user_model.User.USER_TYPE_DOC : 
			if self.request.user.doctorprofile == context['object'].schedule.doctor :
				context['my'] = True
			else : 
				context['my'] = False
				messages.warning(self.request , "Not your appointment")

		if self.request.user.user_type == user_model.User.USER_TYPE_DOC_ASST : 
			if self.request.user.docasstprofile.doctor == context['object'].schedule.doctor :
				context['my'] = True
			else : 
				context['my'] = False
				messages.warning(self.request , "Not your appointment")

		return context


@login_required
def hospital_manager(request):
	if user_is_doctor(request):
		if request.method == "GET":
			if request.GET.get('hospital', False) : 
				hospital_id = request.GET['hospital']
				
				try:
					hospital = Hospital.objects.get(id=hospital_id)
				except Exception as e:
					messages.error(request, f'Invalid Parameter {e}')
					return redirect('error')
				
				my_hospitals = request.user.doctorprofile.manages.all()

				if hospital in my_hospitals:
					context = {
						'page_title' : 'Add Manager',
						'hospital' : hospital,
						'managers' : hospital.managers.all(),
					}

					return render(request, 'medic/add_manager.html' , context)
				else : 
					messages.error(request, 'You don\'t manage this hospital. You can not use this feature.')
					return redirect('error')

			else :
				messages.error(request, 'No Parameter Found')
	
	# if use is not doctor
	return redirect('error')



def search_doc_ajax(request):
	search_text = request.GET.get('search' , False)
	hospital = request.GET.get('hospital' , False)


	if hospital == False : 
		return HttpResponse("Error")

	def get_action_button(doc_id, hospital):
		if request.GET.get('manager', False) == "1":
			html_text = f"""
			<a href="/add_hospital_manager/?doctor={doc_id}&hospital={hospital}">
			  <button class="btn_small">Add as Manager</button>
			</a>
			"""
		else:
			html_text = f"""
			<a href="/add_hospital_doctor/?doctor={doc_id}&hospital={hospital}">
			  <button class="btn_small">Add Doctor</button>
			</a>
			"""
		return html_text

	if search_text :
		if search_text == "":
			return HttpResponse("<span style='color: #e74c3c'>Please enter something to search</span>")

		result = search_doctor(search_text)

		http_response_text = """
		<table>
		<tr>
			<th width="64">ID</th>
			<th>Doctor Name</th>
			<th width="256"> &nbsp; </th>
		</tr>""";

		if len(result)==0 : 
			http_response_text += """<tr><td colspan="3" class="text-center review_num_text">No result found</td></tr>"""
		
		for doc in result:
			http_response_text += f"""
			<tr>
				<td>{doc.id}</td>
				<td>
					<a href="/doctor/{doc.id}" target="_blank" title="View this Profile">
						<img src="{doc.image.url}" class="profile_image small">
						{doc.user.first_name} {doc.user.last_name}
					</a>
				</td>
				<td>
					{ get_action_button(doc.id, hospital) }
				</td>
			</tr>
			"""
		http_response_text += "</table>"

	else : 
		return HttpResponse("Error. No Parameter Found.")

	return HttpResponse(http_response_text)



def add_manager(request):
	if user_is_doctor(request):
		if request.method == "POST":
			if not request.POST.get('hospital', False) or not request.POST.get('doctor', False) : 
				messages.error(request, 'Parameter missing')
				return redirect('error')
			
			hospital_id = request.POST['hospital']
			hospital = Hospital.objects.get(id=hospital_id)

			doctor_id = request.POST['doctor']
			doctor = DoctorProfile.objects.get(id=doctor_id)

			# validation
			my_hospitals = request.user.doctorprofile.manages.all()

			if hospital in my_hospitals:
				hospital.managers.add(doctor)
				hospital.doctors.add(doctor)
				return redirect('/update_hospital/done')
			else : 
				messages.error(request, 'You don\'t manage this hospital. You can not use this feature.')
				return redirect('error')

			
		if request.method == "GET":
			if request.GET.get('hospital', False) and request.GET.get('doctor', False) : 
				hospital_id = request.GET['hospital']
				doctor_id = request.GET['doctor']

				try:
					hospital = Hospital.objects.get(id=hospital_id)
					doctor = DoctorProfile.objects.get(id=doctor_id)
				except Exception as e:
					messages.error(request, f'Invalid Parameter {e}')
					return redirect('error')

				# validation
				my_hospitals = request.user.doctorprofile.manages.all()

				if hospital in my_hospitals:
					context = {
						'page_title' : 'Add Manager',
						'hospital' : hospital,
						'object' : doctor,
					}

					return render(request, 'medic/add_manager_confirm.html' , context)
				else : 
					messages.error(request, 'You don\'t manage this hospital. You can not use this feature.')
					return redirect('error')

			else :
				messages.error(request, 'Parameter Missing')
	
	# if use is not doctor
	return redirect('error')


@login_required
def create_doctor_schedule(request):
	if request.user.user_type == User.USER_TYPE_DOC_ASST or user_is_doctor(request):
		if request.user.user_type == User.USER_TYPE_DOC_ASST:
			hospitals = request.user.docasstprofile.doctor.hospital_set.all()
		else:
			hospitals = request.user.doctorprofile.hospital_set.all()

		if len(hospitals) == 0:
			messages.error(request, mark_safe("You have not added any hospital yet. You need to <a href='/add_hospital/'>add a hospital</a> first."))
			return redirect('error')

		if request.method == "GET":
			form = DoctorScheduleForm()

		if request.method == "POST":
			form = DoctorScheduleForm(request.POST)

			try:
				chember_id = request.POST['hospital']
				chember = Hospital.objects.filter(id=chember_id)

				if form.is_valid():
					if request.user.user_type == User.USER_TYPE_DOC_ASST:
						form.save(request.user.docasstprofile.doctor, chember_id)
					else:
						form.save(request.user.doctorprofile, chember_id)

					messages.success(request, 'Schedule Created Successfully')
					return redirect('my_schedule')
			
			except Exception as e:
				messages.error(request, f'Error. {e}')
				return redirect('error')

		context = {
			'page_title' : 'Create Schedule',
			'form' : form , 
			'hospitals' : hospitals,
		}

		return render(request, 'medic/doc_schedule_create_update.html' , context)

	return redirect('error')



class DoctorScheduleEditView(LoginRequiredMixin, UpdateView):
	template_name = 'medic/doc_schedule_create_update.html'
	form_class = DoctorScheduleForm
	queryset = DoctorsSchedule.objects.all()
	success_url = '/my_schedule' 
	success_message = "Successfully updated"

	error = False

	def get_object(self):
		if self.request.user.user_type == 'DA':
			id_ = self.kwargs.get("id")
			current_docasst = self.request.user.docasstprofile
			obj = get_object_or_404(DoctorsSchedule, id=id_)

			doc_is_the_owner = False

			if current_docasst.doctor == obj.doctor :
				doc_is_the_owner = True
				return obj
			else:
				self.error = True
				messages.error(self.request , 'This schedule does not belong to you or your supervisor doctor')
				
		elif user_is_doctor(self.request):
			id_ = self.kwargs.get("id")
			current_doctor = self.request.user.doctorprofile
			obj = get_object_or_404(DoctorsSchedule, id=id_)

			doc_is_the_owner = False

			if current_doctor == obj.doctor :
				doc_is_the_owner = True
				return obj
			else:
				self.error = True
				messages.error(self.request , 'This schedule belongs to another doctor')
		
		else:
			self.error = True
			messages.error(self.request , 'Only the owners of this schedule can access this page')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['page_title'] = 'Update Schedule'
		context['update'] = True
		context['error'] = self.error
		context['id'] = self.get_object().id
		context['chember'] = self.get_object().chember
		return context




@login_required
def add_hospital_doctor(request):
	if user_is_doctor(request):
		if request.method == "POST":
			if not request.POST.get('hospital', False) or not request.POST.get('doctor', False) : 
				messages.error(request, 'Parameter missing')
				return redirect('error')
			
			hospital_id = request.POST['hospital']
			doctor_id = request.POST['doctor']

			try:
				hospital = Hospital.objects.get(id=hospital_id)
				doctor = DoctorProfile.objects.get(id=doctor_id)
			except Exception as e:
				messages.error(request, f'Invalid Parameter {e}')
				return redirect('error')

			# validation
			my_hospitals = request.user.doctorprofile.manages.all()

			if hospital in my_hospitals:
				hospital.doctors.add(doctor)
				return redirect('/update_hospital/done')
			else : 
				messages.error(request, 'You don\'t manage this hospital. You can not use this feature.')
				return redirect('error')

			
		if request.method == "GET":
			if request.GET.get('hospital', False) and request.GET.get('doctor', False) : 
				hospital_id = request.GET['hospital']
				doctor_id = request.GET['doctor']

				try:
					hospital = Hospital.objects.get(id=hospital_id)
					doctor = DoctorProfile.objects.get(id=doctor_id)
				except Exception as e:
					messages.error(request, 'Invalid Parameter')
					return redirect('error')

				# validation
				my_hospitals = request.user.doctorprofile.manages.all()

				if hospital in my_hospitals:
					context = {
						'page_title' : 'Add Doctor',
						'hospital' : hospital,
						'object' : doctor,
					}

					return render(request, 'medic/add_doctor_confirm.html' , context)
				else : 
					messages.error(request, 'You don\'t manage this hospital. You can not use this feature.')
					return redirect('error')

			else :
				messages.error(request, 'Parameter Missing')
	
	# if use is not doctor
	return redirect('error')


@login_required
def hospital_doctors_for_managers(request):
	# list doctors
	if user_is_doctor(request):
		if request.method == "GET":
			if request.GET.get('hospital', False) : 
				hospital_id = request.GET['hospital']
				try:
					hospital = Hospital.objects.get(id=hospital_id)
				except Exception as e:
					messages.error(request, 'Invalid Parameter')
					return redirect('error')
				
				# validation
				my_hospitals = request.user.doctorprofile.manages.all()

				if hospital in my_hospitals:
					context = {
						'page_title' : 'Manage Doctors',
						'hospital' : hospital,
					}

					return render(request, 'medic/manage_hospital_doctors.html' , context)
				else : 
					messages.error(request, 'You don\'t manage this hospital. You can not use this feature.')
					return redirect('error')

			else :
				messages.error(request, 'Parameter Missing')

	return redirect('error')




@login_required
def delete_hospital_doctor(request):
	if user_is_doctor(request):
		if request.method == "POST":
			if not request.POST.get('hospital', False) or not request.POST.get('doctor', False) : 
				messages.error(request, 'Parameter missing')
				return redirect('error')
			
			hospital_id = request.POST['hospital']
			doctor_id = request.POST['doctor']

			try:
				hospital = Hospital.objects.get(id=hospital_id)
				doctor = DoctorProfile.objects.get(id=doctor_id)
			except Exception as e:
				messages.error(request, f'Invalid Parameter {e}')
				return redirect('error')

			# validation
			my_hospitals = request.user.doctorprofile.manages.all()

			if doctor in hospital.managers.all():
				messages.error(request, mark_safe('This doctor is a manager of this hospital, managers can not be removed.<br/>Please contact an admin to remove a manager.'))
				return redirect('error')

			if hospital in my_hospitals:
				hospital.doctors.remove(doctor)
				return redirect('/update_hospital/done')
			else : 
				messages.error(request, 'You don\'t manage this hospital. You can not use this feature.')
				return redirect('error')

			
		if request.method == "GET":
			if request.GET.get('hospital', False) and request.GET.get('doctor', False) : 
				hospital_id = request.GET['hospital']
				doctor_id = request.GET['doctor']

				try:
					hospital = Hospital.objects.get(id=hospital_id)
					doctor = DoctorProfile.objects.get(id=doctor_id)
				except Exception as e:
					messages.error(request, 'Invalid Parameter')
					return redirect('error')

				# validation
				my_hospitals = request.user.doctorprofile.manages.all()

				if hospital in my_hospitals:
					context = {
						'page_title' : 'Delete Doctor',
						'hospital' : hospital,
						'object' : doctor,
					}

					return render(request, 'medic/delete_doctor_confirm.html' , context)
				else : 
					messages.error(request, 'You don\'t manage this hospital. You can not use this feature.')
					return redirect('error')

			else :
				messages.error(request, 'Parameter Missing')
	
	# if use is not doctor
	return redirect('error')



@login_required
def remove_hospital(request):
	if user_is_doctor(request):
		if request.method == "POST":
			if not request.POST.get('hospital', False) : 
				messages.error(request, 'Parameter missing')
				return redirect('error')
			
			hospital_id = request.POST['hospital']

			try:
				hospital = Hospital.objects.get(id=hospital_id)
			except Exception as e:
				messages.error(request, f'Invalid Parameter {e}')
				return redirect('error')

			# validation
			my_hospitals = request.user.doctorprofile.hospital_set.all()

			if hospital in request.user.doctorprofile.manages.all():
				messages.warning(request, mark_safe("You are a manager of this hospital. You can not remove yourself.<br>Please contact an administrator in case of removing managers from hospitals."))
				return redirect('error')

			if hospital in my_hospitals:
				request.user.doctorprofile.hospital_set.remove(hospital)
				return redirect('/update_hospital/done')
			else : 
				messages.error(request, 'Hospital can not be removed. You are not in this hospital.')
				return redirect('error')

			
		if request.method == "GET":
			if request.GET.get('hospital', False):
				hospital_id = request.GET['hospital']

				try:
					hospital = Hospital.objects.get(id=hospital_id)
				except Exception as e:
					messages.error(request, f'Invalid Parameter {e}')
					return redirect('error')

				# validation
				my_hospitals = request.user.doctorprofile.hospital_set.all()

				if hospital in my_hospitals:
					context = {
						'page_title' : 'Remove Hospital',
						'hospital' : hospital,
					}

					return render(request, 'medic/remove_hospital.html' , context)
				else : 
					messages.error(request, 'You don\'t manage this hospital. You can not use this feature.')
					return redirect('error')

			else :
				messages.error(request, 'Parameter Missing')
	
	# if use is not doctor
	return redirect('error')



@login_required
def add_hospital(request):
	if not user_is_doctor(request):
		return redirect('error')
	
	context = {
		'page_title' : 'Add Hospital',
	}

	if request.method == "POST":
		try:
			hospital_id = request.POST['hospital']
			hospital = Hospital.objects.get(id=hospital_id)
			request.user.doctorprofile.hospital_set.add(hospital)
			messages.success(request, 'Hospital Added Successfully')
			return redirect('my_hospitals')
		except Exception as e:
			messages.error(request, f'Error. {e}')
			return redirect('error')


	if request.GET.get('search', False):
		search_text = request.GET.get('search', False)
		context['search'] = search_text
		context['search_result'] = search_hospital(search_text)

	return render(request, 'medic/add_hospital-GET.html', context)


@login_required
def confirm_appointment(request):
	if request.method == "POST":
		try:
			schedule_id = request.POST['schedule']
			schedule = DoctorsSchedule.objects.get(id=schedule_id)
			patient = User.objects.get(id=request.user.id)
			issue_title = request.POST['title']
			issue_desc = request.POST['desc']

			if schedule.slot_available() :
				appointment = Appointment(schedule=schedule, patient=patient, issue_title=issue_title, issue_desc=issue_desc)
				appointment.save()
				messages.success(request, mark_safe("Appointment request placed successfully. Please wait until the appointment is approved.<br>You will be able to make payment and confirm your slot booking after the request is approved."))
				return redirect('appointment-history')
			else :
				messages.error(request, mark_safe("Sorry. No slot available."))
				return redirect('error')

			# validations
			# see if already booked - done
			# see if slot empty
			# update slot info (slot-1) -> after asst/doc confirms

			############ SUCCESS URL + msg ############

		except Exception as e:
			messages.error(request, f'Error. {e}')
			return redirect('error')

	try:
		schedule_id = request.GET['schedule']
	except Exception as e:
		messages.error(request, f'Error. {e}')
		return redirect('error')

	context = {
		'page_title' : 'Confirm Appointment',
		'schedule_id' : schedule_id , 
	}
	return render(request, 'medic/confirm_appointment.html', context)


class AppointmentListView(LoginRequiredMixin, ListView):
	model = Appointment
	paginate_by = 20

	queryset = Appointment.objects.all()

	def get_queryset(self):
		if hasattr(self.request.user, 'docasstprofile') or hasattr(self.request.user, 'doctorprofile') :
			if hasattr(self.request.user, 'docasstprofile'):
				doc = self.request.user.docasstprofile.doctor
			else : 
				doc = self.request.user.doctorprofile

			return Appointment.objects.filter(schedule__doctor=doc).order_by('schedule__start_date')
		else :
			messages.error(self.request , 'Only doctors/doctor assistants can access this page')

		return Appointment.objects.filter(status=-99)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['page_title'] = 'All Appointments'

		obj = self.get_queryset()

		awaiting_confirmation_list = obj.filter(status=0)
		awaiting_payment_list = obj.filter(status=1)
		confirmed_list = obj.filter(status=2)
		cancelled_list = obj.filter(status=3)

		context['awaiting_confirmation_list'] = awaiting_confirmation_list
		context['awaiting_payment_list'] = awaiting_payment_list
		context['confirmed_list'] = confirmed_list
		context['cancelled_list'] = cancelled_list


		return context


@login_required
def reject_appointment(request):
	context = {
		'page_title' : 'Reject Appointment',
	}

	def valid_appointment(appointment):
		# appointment belongs to current doc/asst
		if appointment.schedule.doctor != doc:
			messages.warning(request, "Dissapointment... This appointment is not in your list.")
			return False

		# appointment is not already paid/confirmed
		if appointment.status == Appointment.STATUS_CONFIRMED or appointment.status == Appointment.STATUS_AWAITING_PAYMENT :
			messages.warning(request, mark_safe("This appointment can not be cancelled.<br>Because, it is already confirmed (by payment) or approved (waiting for payment)"))
			return False

		return True



	if user_is_doc_asst(request) or user_is_doctor(request):
		if hasattr(request.user, 'doctorprofile'):
			doc = request.user.doctorprofile
		else:
			doc = request.user.docasstprofile.doctor
		
		context['schedule_list'] = DoctorsSchedule.objects.filter(doctor=doc)

		if request.method=="POST":
			try:
				appointment_id = request.POST['id']
				appointment = Appointment.objects.get(id=appointment_id)

				if not valid_appointment(appointment):
					return redirect('error')

				if request.POST["action"]=="reschedule":
					schedule_id = request.POST['new_schedule']
					appointment.schedule = DoctorsSchedule.objects.get(id=schedule_id)
					appointment.status = Appointment.STATUS_AWAITING_PAYMENT
					appointment.save()

				if request.POST['action']=="cancel":
					appointment.status = Appointment.STATUS_CANCELLED
					appointment.save()

				messages.success(request, 'Appointment status updated successfully.')
				return redirect('/')

			except Exception as e:
				messages.error(request, f'Error (MEDI_V_815) : An unknown error has occured. {e} Please contact an administrator. ')

		
		#getting the appointment data using the id from the get parameter
		if request.method=="GET" and request.GET.get('id', False):
			a_id = request.GET['id']

			try:
				appointment = Appointment.objects.get(id=a_id)
			except Exception as e:
				messages.warning(request, f'{e}')
				return redirect('error')

				

			if not valid_appointment(appointment):
				return redirect('error')

			context['appointment'] = appointment

			return render(request, 'medic/reject_appointment.html', context)	
		else : 
			messages.warning(request, "Missing Parameter")
	
		
		# return render()

	return redirect('error')