from django import forms

from .models import *


class BlogPostForm(forms.ModelForm):
	title = forms.CharField(widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Title"}))
	subtitle = forms.CharField(widget=forms.TextInput(attrs={'class':'input_bottom_outline full_width', 'placeholder':"Subtitle (Optional)"}), required=False)
	description = forms.CharField(widget=forms.Textarea(attrs={'placeholder':"Write all the details here.", 'style':'height: 250px;'}))
	featured_image = forms.ImageField(label='Featured Image (Optional)', widget=forms.FileInput, required=False)
	
	def save(self, author=None, commit=True):
		instance = super().save(commit=False)

		if author:
			instance.author = author

		if commit:
			instance.save()
		
		return instance
	
	class Meta:
		model = Post
		fields = ['title','subtitle','description', 'featured_image']