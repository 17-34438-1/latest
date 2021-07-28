from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test

from django.views.generic import ListView, DetailView


from .forms import *
from .models import *

from medic.models import Hospital

from main.views import user_is_doctor, user_is_doc_asst


# Create your views here.
def register(request):
	if request.user.is_authenticated:
		return redirect('user-home') #redirecting

	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			new_user = form.save() #save the form in db
			username = form.cleaned_data.get('username') #grabbing the already entered username
			# messages.success(request, f'Account created for {username}. Thank you for registering.') #sending a flash message (one time message) to the user, maybe getting added with the "request" object
			new_user = authenticate(username=form.cleaned_data['username'],
									password=form.cleaned_data['password1'],
									)
			login(request, new_user)
			return redirect('welcome') #redirecting
	else:
		form = UserCreationForm()

	return render(request, 'user/register.html', {'page_title': 'Create New Account', 'form':form})


@login_required
def edit_profile(request):
	doctor = patient = docasst = False

	# retreiving the user profile according to the user type
	if request.user.user_type == User.USER_TYPE_PATIENT:
		patient = True
		user_profile = request.user.patientprofile
	elif request.user.user_type == User.USER_TYPE_DOC:
		doctor = True
		user_profile = request.user.doctorprofile
	else:
		docasst = True
		user_profile = request.user.docasstprofile

	if request.method == 'POST':
		try:	
			u_form = UserUpdateForm(request.POST, instance=request.user)

			if doctor: 
				p_form = DoctorProfileUpdate(request.POST, request.FILES, instance=user_profile)
			elif patient:
				p_form = PatientProfileUpdate(request.POST, request.FILES, instance=user_profile)
			else:
				p_form = DocAsstProfileUpdate(request.POST, request.FILES, instance=user_profile)

			# save the settings
			if u_form.is_valid() and p_form.is_valid():
				u_form.save()
				p_form.save()

				messages.success(request, f'Successfully Updated')
				return redirect('profile') #redirecting
		except Exception as e:
			messages.error(request, f'An error occured. {e}')
			return redirect('profile') #redirecting
	else:
		u_form = UserUpdateForm(instance=request.user)

		if patient:
			p_form = PatientProfileUpdate(instance=user_profile)
		elif doctor:
			p_form = DoctorProfileUpdate(instance=user_profile)
		else:
			p_form = DocAsstProfileUpdate(instance=user_profile)

	context = {
		'u_form': u_form,
		'p_form': p_form,
		'page_title': 'Profile',
		'profile': user_profile,
	}

	return render(request, "user/edit_profile.html" , context )


@login_required
def profile(request):
	doctor = patient = docasst = False

	# retreiving the user profile according to the user type
	if request.user.user_type == User.USER_TYPE_PATIENT:
		patient = True
	elif request.user.user_type == User.USER_TYPE_DOC:
		doctor = True
	else:
		docasst = True

	if doctor:
		return redirect('/doctor/'+str(request.user.doctorprofile.id))
	elif patient:
		return render(request, "user/patients_profile.html" , {'page_title':'My Profile', 'patient' : request.user , 'me' : True } )
	else:
		return redirect('/docasst/'+str(request.user.docasstprofile.id))

	return 0


@login_required
def settings(request):
	return render(request, 'main/settings.html', {'page_title' : 'Settings'})



class DoctorDetailsView(DetailView):
	model = DoctorProfile
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['page_title'] = 'Dr. ' + context['object'].user.first_name + ' ' + context['object'].user.last_name
		doc = DoctorProfile.objects.filter(id=self.object.id)
		context['hospitals'] = Hospital.objects.filter(doctors__in=doc)
		return context


class DocAsstDetailsView(DetailView):
	model = DocAsstProfile
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['page_title'] = context['object'].user.first_name + ' ' + context['object'].user.last_name
		return context


@login_required
def patient_profile(request):
	context = {
		'page_title':'My Profile',
	}

	if user_is_doc_asst(request) or user_is_doctor(request):
		pass
	else: 
		return redirect('error')

	if request.GET.get('id', False):
		patient_id = request.GET['id']
		try:
			patient = User.objects.get(id=patient_id)

			if patient == request.user :
				context['me'] = True

			if patient.user_type == User.USER_TYPE_PATIENT :
				context['photo'] = patient.patientprofile.image.url
				context['last_updated'] = patient.patientprofile.last_update
			if patient.user_type == User.USER_TYPE_DOC :
				context['photo'] = patient.doctorprofile.image.url
				context['last_updated'] = patient.doctorprofile.last_update
			if patient.user_type == User.USER_TYPE_DOC_ASST :
				context['photo'] = patient.docasstprofile.image.url
				# context['last_updated'] = patient.docasstprofile.last_update
		except Exception as e:
			messages.warning(request, f'Error. {e}')
			return redirect('error')
	else: 
		messages.warning(request, 'No id parameter found')
		return redirect('error')

	context['patient'] = patient

	return render(request, "user/patients_profile.html" , context )









@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user/change_password.html', {
    	'page_title' : 'Change Password',
        'form': form
    })