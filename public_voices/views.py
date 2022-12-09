from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from public_voices.models import Topic, Comment, User
from bson.objectid import ObjectId


# Path: /hot_topics
def hot_topics(request):
    topics = Topic.find({})

    for topic in topics:
        topic['url'] = f'/topic/{topic["_id"]}'
        topic['analyze_url'] = f'/analyze/{topic["_id"]}'

    return render(request, 'hot_topics.html', {'topics': topics})


# Path: /create_topic
@csrf_exempt
def create_topic(request):
    Topic.insert_one(
        Topic(request.POST['title'], request.POST['description'], 0))
    return redirect('/hot_topics')


# Path: /topic/<str:topic_id>
def topic(request, topic_id):
    topic = Topic.find_one({'_id': ObjectId(topic_id)})
    topic['create_comment_url'] = f'/create_comment/{topic_id}'

    comments = Comment.find({'topic_id': ObjectId(topic_id)})

    return render(request, 'topic.html', {'topic': topic, 'comments': comments})


# Path: /create_comment/<str:topic_id>
@csrf_exempt
def create_comment(request, topic_id):
    # return HttpResponse(request.POST)
    Comment.insert_one(Comment(request.POST['content'], topic_id, 0))
    return redirect(f'/topic/{topic_id}')


# Path: /analyze/<str:topic_id>
def analyze(request, topic_id):
    return render(request, 'analyze.html')


# Path: /signup
def signup(request):
    return render(request, 'signup.html')


# Path: /login
def login(request):
    return render(request, 'login.html')
