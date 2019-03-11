from django.shortcuts import render, redirect,get_object_or_404, get_list_or_404
from .models import *
from user_profile.models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader, RequestContext
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.forms import modelformset_factory
from django.contrib.auth.forms import UserCreationForm
from itertools import chain
from django.core.files.base import ContentFile
from io import BytesIO
import urllib.request
from PIL import Image
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .tokens import password_reset_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import SetPasswordForm
from django.core.mail import send_mass_mail
import json
import datetime
import html2markdown
from django.core.paginator import Paginator , EmptyPage, PageNotAnInteger

json.JSONEncoder.default = lambda self,obj: (obj.isoformat() if isinstance(obj, datetime.datetime) else None)

def home(request):
    return render(request, 'home.html')

def tagging_add(q_id, t_id):
    p = Taggings.objects.create(question=get_object_or_404(Questions, pk=q_id), tag=get_object_or_404(Tags, pk=t_id))
    return

def bulk_tagging_add(question, tags):
    taggings = []
    for tag in tags:
        taggings.append(Taggings(question=question, tag=tag))
    Taggings.objects.bulk_create(taggings)
    return

VALID_IMAGE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
]

def valid_url_extension(url, extension_list=VALID_IMAGE_EXTENSIONS):
    end=([url.endswith(e) for e in extension_list])
    count=1
    for e in end:
        if e == True:
          if count==1:
              type=".jpg"
          elif count==2:
              type=".jpeg"
          elif count==3:
              type=".png"
          elif count==4:
              type=".gif"
        count+=1
    return type

@login_required
def add_question(request):
    form = Questionform(request.POST or None)

    Tagform = modelformset_factory(Tags, fields=('name',), extra=5)
    if request.method=='POST':
        form2 = Tagform(request.POST)
        if form.is_valid() and form2.is_valid():
            f = form.save(commit=False)
            f.user_id = request.user
            form.save()
            f2 = form2.save(commit=False)
            tagging_list = []
            q_id = f.id
            for item in f2:
                if Tags.objects.filter(name=item.name).exists():
                    tag = Tags.objects.get(name=item.name)
                else:
                    item.save()
                    tag=item
                if tag not in tagging_list:
                    tagging_list.append(tag)

            bulk_tagging_add(f, tagging_list)  # use a bulk create function which accepts a list
            profiles=Profile.objects.filter(role = 2)
            messages=()
            for profile in profiles:
                user = profile.user
                current_site = get_current_site(request)
                subject = 'New Activity in AskREC'
                message = render_to_string('new_question_entry_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'question' : Questions.objects.get(pk=f.id),
                })
                msg=(subject, message, 'webmaster@localhost', [user.email])
                messages += (msg,)
                result = send_mass_mail(messages, fail_silently=False)
            return redirect('forum:list_questions')

    else:
         form2 = Tagform(queryset=Tags.objects.none())
    
    return render(request, 'forum/questions-form.html', {'form': form,'form2':form2,})

def list_questions(request):
    questions = Questions.objects.all()
    paginator = Paginator(questions, 5)
    page = request.GET.get('page')
    try:
        questions_list = paginator.page(page)
    except PageNotAnInteger:
        questions_list = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        questions_list = paginator.page(paginator.num_pages)
    q_count=questions.count()
    answers=Answers.objects.all()
    follows=Follows.objects.all()
    taggings_recent = Taggings.objects.all().order_by('-updated_at')
    tags_recent=Tags.objects.all().order_by('-updated_at')
    tags_popular=[]
    if tags_recent.count()>10:
        limit=10
    else:
        limit=tags_recent.count()
    for tag in tags_recent:
        tagging = Taggings.objects.filter(tag=tag)
        count=tagging.count()
        tags_popular.append([count,tag])
    tags_popular.sort(key=lambda x: x[0],reverse=True)
    tags_recent_record=[]
    tags_popular_record=[]
    for i in range(limit):
        tags_popular_record.append(tags_popular[i][1])
    count=0
    while len(tags_recent_record)!= limit:
        if taggings_recent[count].tag not in tags_recent_record:
           tags_recent_record.append(taggings_recent[count].tag)
        count+=1

    args = {'questions':questions_list, 'answers':answers, 'follows':follows, 'tags':tags_recent, 'taggings':taggings_recent, 'tags_recent':tags_recent_record, 'tags_popular':tags_popular_record, 'q_count':q_count}
    if request.is_ajax():
        return render(request, 'list.html', args)
    return render(request, 'questions.html', args)

def detail_questions(request, id):
    comform = Commentform(request.POST or None)
    ansform = Answerform(request.POST or None)

    try:
        questions =get_object_or_404( Questions,pk=id)
    except:
        return HttpResponse("id does not exist")
    answers = Answers.objects.filter(question_id = questions)
    follows = Follows.objects.filter(question = questions)
    tags = Tags.objects.all()
    taggings = Taggings.objects.all()
    upvotes=Upvotes.objects.all()
    comments=Comments.objects.filter(question = questions)
    comments_answers=Comments_Answers.objects.all()
    if User.objects.filter(username=request.user).exists():
        ans = Answers.objects.filter(user_id=request.user).filter(question_id=questions)
        if ans.count() > 0:
            ans = ans[0]
        else:
            ans = None
    else:
        ans=None
    user = request.user
    user_profile = Profile.objects.get(user=user)
    user_permission = user_profile.role
    flag=0
    id_list = []
    if User.objects.filter(username=request.user).exists():
        if Follows.objects.filter(question=questions, user=user).exists():
            flag = 1
        votes = Upvotes.objects.filter(user=user).values("answer_id")
        id_list = [id['answer_id'] for id in votes]  # voted answers id


    args = {'user_permission':user_permission,'comform':comform,'ansform':ansform,'questions': questions, 'answers': answers, 'follows': follows, 'tags':tags, 'taggings':taggings, 'upvotes':upvotes, 'comments':comments,'comments_answers':comments_answers,'ans':ans,'flag':flag,'voted':id_list, }
    return render(request, 'forum/detail.html', args)

@login_required
def update_questions(request, id):
    try:
        question = get_object_or_404(Questions, pk=id)
    except:
        return HttpResponse("id does not exist")

    form = Questionform(request.POST or None, instance=question)
    Tagform = modelformset_factory(Tags, fields=('name',), extra=1)
    if request.method == 'POST':
        form2 = Tagform(request.POST or None)
        if form.is_valid() and  form2.is_valid():
            description = form.cleaned_data.get('description')
            f = form.save(commit=False)
            f.user_id = request.user
            form.save()
            to_del = Taggings.objects.filter(question=question)  # delete all prev taggings
            if to_del.exists():
                to_del.delete()
            tagging_list = []
            for item in form2:  # create new taggings
                if item.cleaned_data.get("name") != None:  # if a tag was removed
                    try:
                        tag_name = item.cleaned_data.get('name')
                        tag = get_object_or_404(Tags, name=tag_name)  # see if tag exists
                    except:
                        tag = Tags.objects.create(name=tag_name)  # if not create

                    if tag not in tagging_list:
                        tagging_list.append(tag)

            bulk_tagging_add(question, tagging_list)  # use a bulk create function which accepts a list
            profiles = Profile.objects.filter(role=2)
            follows = Follows.objects.filter(question=question)
            messages = ()
            for profile in profiles:
                user = profile.user
                current_site = get_current_site(request)
                subject = 'New Activity in AskREC'
                message = render_to_string('update_question_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'question': question,
                })
                msg = (subject, message, 'webmaster@localhost', [user.email])
                messages += (msg,)
            for follow in follows:
                user = follow.user
                current_site = get_current_site(request)
                subject = 'New Activity in AskREC'
                message = render_to_string('update_question_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'question': question,
                })
                msg = (subject, message, 'webmaster@localhost', [user.email])
                if msg not in messages:
                    messages += (msg,)
            result = send_mass_mail(messages, fail_silently=False)
            return redirect('forum:list_questions')
    else:
        question.description = html2markdown.convert(question.description)
        form = Questionform(instance=question) 
        question = Questions.objects.get(pk=id)
        id_list = Taggings.objects.filter(question=question).values('tag_id')  # get all tag ids from taggings
        id_list = [id['tag_id'] for id in id_list]  # convert the returned dictionary list into a simple list
        form2 = Tagform(queryset=Tags.objects.filter(id__in=id_list))  # populate form with tags

    return render(request, 'forum/questions-form.html', {'form': form, 'form2': form2, 'question': question})

@login_required
def add_answer(request, id):

    try:
        question = get_object_or_404(Questions, pk=id)

    except:
        return HttpResponse("id does not exist")

    ans=Answers.objects.filter(user_id=request.user).filter(question_id=question)
    if ans.count()>0:
        return HttpResponse("you have already answered,kindly update it instead")
    form = Answerform(request.POST or None)
    if request.POST.get('ajax_call') == "True" :
        if form.is_valid():
            description = form.cleaned_data.get('description')
            print(description)
            if len(description) < 10:
                return HttpResponse("Very Short Answer!")
            f = form.save(commit=False)
            f.question_id=question
            f.user_id = request.user
            form.save()
            profiles = Profile.objects.filter(role=2)
            follows=Follows.objects.filter(question=question)
            messages = ()
            for profile in profiles:
                user = profile.user
                current_site = get_current_site(request)
                subject = 'New Activity in AskREC'
                message = render_to_string('new_answer_entry_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'question': question,
                })
                msg = (subject, message, 'webmaster@localhost', [user.email])
                messages += (msg,)
            for follow in follows:
                user = follow.user
                current_site = get_current_site(request)
                subject = 'New Activity in AskREC'
                message = render_to_string('new_answer_entry_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'question': question,
                })
                msg = (subject, message, 'webmaster@localhost', [user.email])
                if msg not in messages:
                    messages += (msg,)
            result = send_mass_mail(messages, fail_silently=False)
            user= request.user
            f_q_id=Questions.objects.get(pk=id)
            f.question_id=f_q_id
            f.user_id =user
            f.save()

            return HttpResponse(json.dumps({
              'id':f.id,
              'description':f.description,
              'created_at' :f.created_at,
              'updated_at' :f.updated_at,
              'user_id':user.username,
              'Success':'Success'
            }))
        else :
            return HttpResponse("we failed to insert in db")
    else:
        return render(request, 'forum/answer.html', {'form': form})

@login_required
def update_answer(request, id):
    try:
        answer =get_object_or_404(Answers, pk=id)
        question=answer.question_id
    except:
        return HttpResponse("id does not exist")
    else:
        form = Answerform(request.POST or None, instance=answer)
        if request.method == 'POST':
            if form.is_valid():
                description = form.cleaned_data.get('description')
                if description.__len__() < 10:
                    return HttpResponse("Very Short Answer!")
                user = request.user
                user_profile = Profile.objects.get(user=user)
                user_permission = user_profile.role
                if request.user == answer.user_id or user_permission == '2' or user_permission == '1':
                    f=form.save()
                    profiles = Profile.objects.filter(role=2)
                    follows=Follows.objects.filter(question=question)
                    messages = ()
                    for profile in profiles:
                        user = profile.user
                        current_site = get_current_site(request)
                        subject = 'New Activity in AskREC'
                        message = render_to_string('answer_update_email.html', {
                            'user': user,
                            'domain': current_site.domain,
                            'question': question,
                        })
                        msg = (subject, message, 'webmaster@localhost', [user.email])
                        messages += (msg,)
                    for follow in follows:
                        user = follow.user
                        current_site = get_current_site(request)
                        subject = 'New Activity in AskREC'
                        message = render_to_string('answer_update_email.html', {
                            'user': user,
                            'domain': current_site.domain,
                            'question': question,
                        })
                        msg = (subject, message, 'webmaster@localhost', [user.email])
                        if msg not in messages:
                            messages += (msg,)
                    result = send_mass_mail(messages, fail_silently=False)
                    return HttpResponse(json.dumps({
                        'id':f.id,
                        'description':f.description,
                        'created_at' :f.created_at,
                        'updated_at' :f.updated_at,
                        'user_id':request.user.username,
                        'Success':'Success'
                            }))
        
        answer.description=html2markdown.convert(answer.description)
        form=Answerform(instance=answer)


    return render(request, 'forum/answer.html', {'upform': form, 'ans': answer})

@login_required
def edit_following(request, id):
    try:
        question =get_object_or_404( Questions,pk=id)
    except:
        return HttpResponse("id does not exist")
    user = request.user
    if user != question.user_id:
       if Follows.objects.filter(question=question, user=user).exists():
           follow = Follows.objects.get(question=question, user=user)
           follow.delete()
       else:
           follow = Follows.objects.create(question=question, user=user)
           follow.save()
    return HttpResponseRedirect(reverse('forum:detail_questions', args=(question.id,)))

@login_required
def add_comment(request, id):
    try:
        question = get_object_or_404(Questions, pk=id)
    except:
        return HttpResponse("id does not exist")
    form = Commentform(request.POST or None)
    if form.is_valid():
        f = form.save(commit=False)
        f.question=question
        f.user = request.user
        form.save()
        profiles = Profile.objects.filter(role=2)
        follows=Follows.objects.filter(question=question)
        messages = ()
        for profile in profiles:
            user = profile.user
            current_site = get_current_site(request)
            subject = 'New Activity in AskREC'
            message = render_to_string('new_comment_entry_email.html', {
                'user': user,
                'domain': current_site.domain,
                'question': question,
            })
            msg = (subject, message, 'webmaster@localhost', [user.email])
            messages += (msg,)
        for follow in follows:
            user = follow.user
            current_site = get_current_site(request)
            subject = 'New Activity in AskREC'
            message = render_to_string('new_comment_entry_email.html', {
                'user': user,
                'domain': current_site.domain,
                'question': question,
            })
            msg = (subject, message, 'webmaster@localhost', [user.email])
            if msg not in messages:
                messages += (msg,)
        result = send_mass_mail(messages, fail_silently=False)
        user= request.user
        return HttpResponse(json.dumps({
              'id':f.id,
              'body':f.body,
              'created_at' :f.created_at,
              'updated_at' :f.updated_at,
              'user_id':user.username,
              'Success':'Success'
            }))
    else:
        return  HttpResponse("Invalid")

    return render(request, 'forum/comment.html', {'form': form})

@login_required
def update_comment(request, id):
    print(id)
    try:
        comment =get_object_or_404(Comments, pk=id)
        question=comment.question
    except:
        return HttpResponse("id does not exist")
    else:
        if request.method == 'POST':
            form = Commentform(request.POST or None, instance=comment)
            if form.is_valid():
                user = request.user
                user_profile = Profile.objects.get(user=user)
                user_permission = user_profile.role
                if request.user == comment.user or user_permission == '2' or user_permission == '1':
                    f=form.save()
                    profiles = Profile.objects.filter(role=2)
                    follows=Follows.objects.filter(question=question)
                    messages = ()
                    for profile in profiles:
                        user = profile.user
                        current_site = get_current_site(request)
                        subject = 'New Activity in AskREC'
                        message = render_to_string('update_comment_email.html', {
                            'user': user,
                            'domain': current_site.domain,
                            'question': question,
                        })
                        msg = (subject, message, 'webmaster@localhost', [user.email])
                        messages += (msg,)
                    for follow in follows:
                        user = follow.user
                        current_site = get_current_site(request)
                        subject = 'New Activity in AskREC'
                        message = render_to_string('update_comment_email.html', {
                            'user': user,
                            'domain': current_site.domain,
                            'question': question,
                        })
                        msg = (subject, message, 'webmaster@localhost', [user.email])
                        if msg not in messages:
                            messages += (msg,)
                    result = send_mass_mail(messages, fail_silently=False)
                    return HttpResponse(json.dumps({
                    'id':f.id,
                    'body':f.body,
                    'created_at' :f.created_at,
                    'updated_at' :f.updated_at,
                    'user_id':request.user.username,
                    'Success':'Success'
                    }))
        
        comment.body=html2markdown.convert(comment.body)
        form=Commentform(instance=comment)
    return render(request, 'forum/comment.html', {'upform': form, 'comment': comment})

@login_required
def voting(request, id):
    try:
        answer =get_object_or_404( Answers,pk=id)
        question=answer.question_id
    except:
        return HttpResponse("id does not exist")
    user = request.user
    if user != answer.user_id:
       if Upvotes.objects.filter(answer=answer, user=user).exists():
           upvote= Upvotes.objects.get(answer=answer, user=user)
           upvote.delete()
       else:
           upvote = Upvotes.objects.create(answer=answer, user=user)
           upvote.save()
    return HttpResponseRedirect(reverse('forum:detail_questions', args=(question.id,)))




def filter_question(request ,id):
    try:
        required_tag=get_object_or_404(Tags, pk=id)
    except:
        return HttpResponse("Tag does not exist!")
    questions=[]
    answers=Answers.objects.all()
    follows=Follows.objects.all()
    taggings=Taggings.objects.filter(tag=required_tag)
    for tagging in taggings:
        questions.append(tagging.question)
    tags_recent=Tags.objects.all().order_by('-updated_at')
    taggings_recent=Taggings.objects.all().order_by('-updated_at')
    tags_popular = []
    if tags_recent.count() > 10:
        limit = 10
    else:
        limit = tags_recent.count()
    for tag in tags_recent:
        tagging = Taggings.objects.filter(tag=tag)
        count = tagging.count()
        tags_popular.append([count, tag])
    tags_popular.sort(key=lambda x: x[0], reverse=True)
    tags_recent_record = []
    tags_popular_record = []
    for i in range(limit):
        tags_popular_record.append(tags_popular[i][1])
    count=0
    while len(tags_recent_record)!= limit:
        if taggings_recent[count].tag not in tags_recent_record:
           tags_recent_record.append(taggings_recent[count].tag)
        count+=1
    q_count = Questions.objects.all().count() #For displaying total number of questions
    questions.reverse()
    paginator = Paginator(questions, 5)
    page = request.GET.get('page')
    try:
        questions_list = paginator.page(page)
    except PageNotAnInteger:
        questions_list = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        questions_list = paginator.page(paginator.num_pages)
    args = {'questions':questions_list, 'answers':answers, 'follows':follows, 'tags':tags_recent, 'taggings':taggings_recent, 'tags_recent':tags_recent_record, 'tags_popular':tags_popular_record, 'q_count':q_count}
    if request.is_ajax():
        return render(request, 'list.html', args)
    return render(request, 'questions.html', args)


@login_required
def add_comment_answer(request, id):
    try:
        answer = get_object_or_404(Answers, pk=id)
    except:
        return HttpResponse("id does not exist")
    form = Comment_Answerform(request.POST or None)
    if form.is_valid():
        question_id=answer.question_id
        f = form.save(commit=False)
        f.answer=answer
        f.user = request.user
        form.save()
        profiles = Profile.objects.filter(role=2)
        follows=Follows.objects.filter(question=question_id)
        messages = ()
        for profile in profiles:
            user = profile.user
            current_site = get_current_site(request)
            subject = 'New Activity in AskREC'
            message = render_to_string('new_answer_comment_entry_email.html', {
                'user': user,
                'domain': current_site.domain,
                'question': answer.question_id,
            })
            msg = (subject, message, 'webmaster@localhost', [user.email])
            messages += (msg,)
        for follow in follows:
            user = follow.user
            current_site = get_current_site(request)
            subject = 'New Activity in AskREC'
            message = render_to_string('new_answer_comment_entry_email.html', {
                'user': user,
                'domain': current_site.domain,
                'question': answer.question_id,
            })
            msg = (subject, message, 'webmaster@localhost', [user.email])
            if msg not in messages:
                messages += (msg,)
        result = send_mass_mail(messages, fail_silently=False)
        return HttpResponseRedirect(reverse('forum:detail_questions', args=(question_id.id,)))

    return render(request, 'forum/comment.html', {'form': form})

@login_required
def update_comment_answer(request, id):
    try:
        comment =get_object_or_404(Comments_Answers, pk=id)
        answer=comment.answer
    except:
        return HttpResponse("id does not exist")
    else:
        question_id=answer.question_id
        form = Comment_Answerform(request.POST or None, instance=comment)
        if form.is_valid():
            user = request.user
            user_profile = Profile.objects.get(user=user)
            user_permission = user_profile.role
            if request.user == comment.user or user_permission == '2' or user_permission == '1':
              form.save()
              profiles = Profile.objects.filter(role=2)
              follows=Follows.objects.filter(question=question_id)
              messages = ()
              for profile in profiles:
                  user = profile.user
                  current_site = get_current_site(request)
                  subject = 'New Activity in AskREC'
                  message = render_to_string('update_answer_comment_email.html', {
                      'user': user,
                      'domain': current_site.domain,
                      'question': answer.question_id,
                  })
                  msg = (subject, message, 'webmaster@localhost', [user.email])
                  messages += (msg,)
              for follow in follows:
                  user = follow.user
                  current_site = get_current_site(request)
                  subject = 'New Activity in AskREC'
                  message = render_to_string('update_answer_comment_email.html', {
                      'user': user,
                      'domain': current_site.domain,
                      'question': answer.question_id,
                  })
                  msg = (subject, message, 'webmaster@localhost', [user.email])
                  if msg not in messages:
                     messages += (msg,)
              result = send_mass_mail(messages, fail_silently=False)
            return HttpResponseRedirect(reverse('forum:detail_questions', args=(question_id.id,)))

    return render(request, 'forum/comment.html', {'form': form, 'comment': comment})


@login_required
def delete_answer(request, id):
    try:
        answer =get_object_or_404( Answers,pk=id)
        print(answer)
    except:
        return HttpResponse("id does not exist")
    user = request.user
    user_profile = Profile.objects.get(user=user)
    user_permission = user_profile.role
    question=answer.question_id
    if user_permission == '2' or user_permission == '1':
           answer.delete()
    return HttpResponseRedirect(reverse('detail_questions', args=(question.id,)))

@login_required
def delete_comment(request, id):
    try:
        comment =get_object_or_404( Comments,pk=id)
    except:
        return HttpResponse("id does not exist")
    user = request.user
    user_profile = Profile.objects.get(user=user)
    user_permission = user_profile.role
    question = comment.question
    if user_permission == '2' or user_permission == '1':
           comment.delete()
    return HttpResponseRedirect(reverse('detail_questions', args=(question.id,)))

@login_required
def delete_answer_comment(request, id):
    try:
        answer_comment =get_object_or_404( Comments_Answers,pk=id)
    except:
        return HttpResponse("id does not exist")
    user = request.user
    user_profile = Profile.objects.get(user=user)
    user_permission = user_profile.role
    question = answer_comment.answer.question_id
    if user_permission == '2' or user_permission == '1':
           answer_comment.delete()
    return HttpResponseRedirect(reverse('detail_questions', args=(question.id,)))