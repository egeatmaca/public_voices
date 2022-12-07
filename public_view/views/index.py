from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {'topics': ['topic1', 'topic2', 'topic3']})