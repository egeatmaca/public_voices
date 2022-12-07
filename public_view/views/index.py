from django.shortcuts import render
from public_view.models.Topic import Topic

def index(request):
    return render(
        request, 
        'index.html', 
        {
            'topics': [
                Topic(0, 'Some Sustainability Topic', 'This topic is mentioning very important problems regarding life under water.', 0),
                Topic(0, 'Another Topic', 'Lorem ipsum lorem ipsum lorem ipsum.', 0),
                Topic(0, 'Another Topic', 'Lorem ipsum lorem ipsum lorem ipsum.', 0)
            ]
        }
    )