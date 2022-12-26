from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from public_voices.models import Topic, Comment, User
from bson.objectid import ObjectId
from bcrypt import hashpw, gensalt, checkpw
from datetime import datetime as dt
from public_voices.TopicAnalyzer import TopicAnalyzer
import pandas as pd


# Path: /
def index(request):
    # if request.session.get('user_id'):
    #     return redirect('/hot_topics')
    # else:
    #     return redirect('/login')

    return redirect('/hot_topics')

# Path: /hot_topics
def hot_topics(request):
    topics = Topic.find({})

    for topic in topics:
        topic['url'] = f'/topic/{topic["_id"]}'
        topic['analyze_url'] = f'/analyze/{topic["_id"]}'
        topic['username'] = User.find_one(
            {'_id': ObjectId(topic['user_id'])})['username']

    return render(request, 'hot_topics.html', {'topics': topics,  'logged_in': request.session.get('user_id') is not None})


# Path: /create_topic
@csrf_exempt
def create_topic(request):
    Topic.insert_one(
        Topic(request.POST['title'], request.POST ['initial_comment'], request.session['user_id']))
    return redirect('/hot_topics')


# Path: /topic/<str:topic_id>
def topic(request, topic_id):
    topic = Topic.find_one({'_id': ObjectId(topic_id)})
    topic['create_comment_url'] = f'/create_comment/{topic_id}/'
    topic['username'] = User.find_one({'_id': ObjectId(topic['user_id'])})['username']

    comments = Comment.find({'topic_id': topic_id})
    for comment in comments:
        comment['username'] = User.find_one({'_id': ObjectId(comment['user_id'])})['username']

    return render(request, 'topic.html', 
                    {'topic': topic, 'comments': comments, 
                    'logged_in': request.session.get('user_id') is not None, 
                    'login_redirect_url': f'/topic/{topic_id}/'})


# Path: /create_comment/<str:topic_id>
@csrf_exempt
def create_comment(request, topic_id):
    # return HttpResponse(request.Path:)
    Comment.insert_one(Comment(request.POST['content'], request.POST['agree'], topic_id, request.session['user_id']))
    Topic.update_one({'_id': ObjectId(topic_id)}, {'$set': {'updated_at': dt.now()}})
    return redirect(f'/topic/{topic_id}')


# Path: /analyze/<str:topic_id>
def analyze(request, topic_id):
    context = {'topic_id': topic_id}
    ta = TopicAnalyzer(topic_id)

    ta.get_agree_distribution(save=True)
    
    ta.get_word_clouds()
    
    sentiment_analysis = ta.analyze_sentiments()
    context.update(sentiment_analysis)

    # try:
    ta.apply_pca()
    component_features = ta.map_components_to_features()
    component_features = pd.DataFrame([[k, ', '.join(v)] 
                                                    for k, v in component_features.items()],
                                                    columns=['Discussion Component', 'Associated Words'])
    component_effects = ta.get_component_effects().round(2).to_frame().rename(columns={0: 'Effect on Agree Pts.'})
    component_words_and_effects = component_features.join(
        component_effects, on='Discussion Component').sort_values(by='Discussion Component')
    context['component_words_and_effects'] = component_words_and_effects.to_html(index=False)
    # except Exception as e:
    #     context['component_words_and_effects'] = e

    return render(request, 'analyze.html', context)


# Path: /signup
@csrf_exempt
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html')
    elif request.method == 'POST':
        res = User.insert_one(User(request.POST['email'], request.POST['username']))
        return redirect(f'/set_password/{res.inserted_id}/')

# Path: /set_password
@csrf_exempt
def set_password(request, user_id):
    if request.method == 'GET':
        return render(request, 'set_password.html', {'user_id': user_id})
    elif request.method == 'POST' and user_id:
        User.update_one({'_id': ObjectId(user_id)},
                        {'$set': {'password': hashpw(request.POST['password'].encode('utf-8'), gensalt())}})
        request.session['user_id'] = user_id
        return redirect('/')

# Path: /login
@csrf_exempt
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        user = User.find_one({'email': request.POST['email']})
        redirect_url = request.POST.get('redirect_url')
        if redirect_url:
            if redirect_url.endswith('/'):
                redirect_url = redirect_url[:-1]
        else:
            redirect_url = '/'

        if not user:
            return render(request, 'login.html', {'error': 'Invalid email!'})

        password_check = checkpw(
            request.POST['password'].encode('utf-8'), user['password'])
        
        if not password_check:
            return render(request, 'login.html', {'error': 'Invalid password!'})

        request.session['user_id'] = str(user['_id'])
        
        return redirect(redirect_url, {'method': 'GET'})

# Path: /logout
def logout(request):
    request.session.flush()
    return redirect('/')