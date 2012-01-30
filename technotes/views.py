from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

def main_page(request):
	template = get_template('main_page.html')
	variables = Context({
		'head_title': 'techNotes',
		'page_title': 'Welcome to techNotes',
		'page_body': 'One mind in Tech Support!'
	})
	output = template.render(variables)
	return HttpResponse(output)