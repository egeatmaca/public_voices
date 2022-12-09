from django.shortcuts import render
from public_voices.models import Topic, Comment, User


def index(request):
    return render(
        request,
        'hot_topics.html',
        {
            'topics': [Topic(i, f'Topic {i}',
                             'Lorem ipsum lorem ipsum lorem ipsum.', 0)
                       for i in range(1, 11)]
        }
    )


def topic(request, topic_id):
    return render(
        request,
        'topic.html',
        {
            'topic': Topic(topic_id, f'Topic {topic_id}',
                           'Lorem ipsum lorem ipsum lorem ipsum.', 0),
            'comments': [Comment(i, f'Comment {i}',
                                    'Lorem ipsum lorem ipsum lorem ipsum.', 0)
                         for i in range(1, 11)]
        }
    )
