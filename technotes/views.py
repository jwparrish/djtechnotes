from django.http import HttpResponse

def main_page(request):
	output = '''
		<html>
			<head><title>%s</title></head>
			<body>
				<h1>%s</h1><p>%s</p>
			</body>
		</html>
	''' % (
		'techNotes',
		'Welcome to techNotes',
		'One Mind In Tech Support!'
	)
	return HttpResponse(output)