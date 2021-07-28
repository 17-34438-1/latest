"""DocHub_1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

from user import views as user_views
from main import views as main_view
from medic import views as medic_view
from blog import views as blog_view

from user.forms import LoginForm

urlpatterns = [
    path('', main_view.home, name='root'),
    path('admin/', admin.site.urls, name='admin-home'),
    path('error/', main_view.error, name='error'),
    path('search/', main_view.search_page, name='search'),
    path('home/', main_view.user_home, name='user-home'),
    path('welcome/', main_view.welcome, name='welcome'),
    path('login/', auth_views.LoginView.as_view(form_class=LoginForm, template_name='user/login.html',extra_context={'page_title':'Login',}), name='login', kwargs={'redirect_authenticated_user': True, 'redirect_if_logged_in': '/'}), 
    path('register/', user_views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('edit_profile/', user_views.edit_profile, name='edit-profile'),
    path('change_password/', user_views.change_password, name='change_password'),
    path('profile/', user_views.profile, name='profile'),
    path('settings/', user_views.settings, name='settings'),
    path('patient/', user_views.patient_profile, name='patient'),
    path('doctors/', main_view.doc_list, name='doctors'),
    path('doctor/<int:pk>/', user_views.DoctorDetailsView.as_view(), name='doctor-details'),
    path('docasst/<int:pk>/', user_views.DocAsstDetailsView.as_view(), name='docasst-details'),
    path('schedule/', main_view.doc_schedule, name='schedule'),
    path('get_appointment/', medic_view.get_appointment, name='get-appointment'),
    path('appointment_history/', medic_view.appointment_history, name='appointment-history'),
    path('assistant_activity/', main_view.assistant_activity, name='assistant-activity'),
    path('search_assistant/', main_view.search_assistant, name='search-assistant'),
    path('add_assistant/', main_view.add_assistant, name='add-assistant'),
    path('delete_assistant_join_request/', main_view.del_asst_join_req, name='del_asst_join_req'),
    path('join_doctor/', main_view.req_to_join, name='join_doctor'),
    path('hospitals/', medic_view.HospitalListView.as_view(), name='hospitals'),
    path('create_hospital/', medic_view.create_hospital, name='create_hospital'),
    path('hospital/<int:pk>', medic_view.HospitalDetailsView.as_view(), name='view-hospital'),
    path('update_hospital/<int:id>', login_required(medic_view.HospitalEditView.as_view()), name='update_hospital'),
    path('update_hospital/done', medic_view.update_done),
    path('my_hospitals/', medic_view.doc_hospital_list , name="my_hospitals"),
    path('hospital_manager/', medic_view.hospital_manager , name="hospital_manager"),
    path('search_doc_ajax/', medic_view.search_doc_ajax , name="search_doc_to_add_manager"),
    path('add_hospital_manager/', medic_view.add_manager , name="add_hospital_manager"),
    path('hospital_doctors/', medic_view.hospital_doctors_for_managers , name="hospital_doctors"),
    path('add_hospital_doctor/', medic_view.add_hospital_doctor , name="add_hospital_doctor"),
    path('delete_hospital_doctor/', medic_view.delete_hospital_doctor , name="delete_hospital_doctor"),
    path('remove_hospital/', medic_view.remove_hospital , name="remove_hospital"),
    path('add_hospital/', medic_view.add_hospital , name="add_hospital"),
    path('create_schedule/', medic_view.create_doctor_schedule , name="create_schedule"),
    path('update_schedule/<int:id>', medic_view.DoctorScheduleEditView.as_view() , name="update_schedule"),
    path('my_schedule/', main_view.doc_my_schedule , name="my_schedule"),
    path('blog/', blog_view.PostListView.as_view(),name='blog'),
    path('create_blog_post/', blog_view.create_blog_post,name='create_blog_post'),
    path('edit_post/<int:pk>', blog_view.PostUpdateView.as_view() , name="edit_post"),
    path('blog_post/<int:pk>', blog_view.PostDetailView.as_view() , name="blog_post"),
    path('confirm_appointment/', medic_view.confirm_appointment , name="confirm_appointment"),
    path('appointment/<int:pk>', medic_view.AppointmentDetails.as_view() , name="appointment-details"),
    path('calendar/', main_view.calendar , name="calendar"),
    path('all_appointments/', medic_view.AppointmentListView.as_view() , name="all_appointments"),
    path('reject_appointment/', medic_view.reject_appointment , name="reject_appointment"),
    path('notifications/', main_view.notifications , name="notifications"),
    path('mark_notification_as_read/', main_view.mark_notification_as_read , name="mark_notification_as_read"),
    path('check_for_notification/', main_view.check_for_notification , name="check_for_notification"),
    path('manage_appointment/', main_view.manage_appointment , name="manage_appointment"),
    path('pay/', main_view.pay_dummy , name="pay"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    


