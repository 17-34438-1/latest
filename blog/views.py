from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib import messages
from django.shortcuts import get_object_or_404


from .models import *
from .forms import *

from main.views import user_is_doctor

# Create your views here.
class PostListView(ListView):
	queryset = Post.objects.all().order_by('-date_created')

	def get_queryset(self):
		if self.request.GET.get('author'):
			queryset = super().get_queryset().filter(author__id=self.request.GET['author']).order_by('-date_created')
		else:
			queryset = super().get_queryset().order_by('-date_created')
    	
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['page_title'] = 'Blog'
		if hasattr(self.request.user, 'doctorprofile'):
			context['doctor'] =  True
    	
		return context




class PostUpdateView(UpdateView):
	template_name = 'blog/create_post.html'
	form_class = BlogPostForm
	queryset = Post.objects.all()
	success_url = '/blog'

	error = False

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['page_title'] = 'Edit Post'
		
		if self.request.user.id == self.get_object().author.user.id :
			pass
		else : 
			self.error = True
			context['error_msg'] = 'You are not the author of this post.'
		
		context['error'] = self.error
		
		return context


class PostDetailView(DetailView):
	model = Post
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['page_title'] = context['object'].title

		if self.get_object().author.user.id == self.request.user.id :
			context['current_user_is_author'] = True


		return context
			
			
			
@login_required
def create_blog_post(request):
	if user_is_doctor(request):
		if request.user.doctorprofile.apprived : 
			pass
		else: 
			messages.error(request, 'Your profile has not been approved yet. You can not create posts at this moment.')
			return redirect('error')
	else:
		return redirect('error')
	

	if request.method == "POST":
		form = BlogPostForm(request.POST)
		
		if form.is_valid():
			form.save(request.user.doctorprofile) #save the form in db
	else:
		form = BlogPostForm()

	return render(request, 'blog/create_post.html', {'page_title': 'Create New Post', 'form':form} )