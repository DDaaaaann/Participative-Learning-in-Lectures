from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.template import RequestContext, loader
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from teacher.decorators import user_login_required
from datetime import datetime, timedelta

from models import Course
from models import Lecture
from models import Question
from models import Answer
from models import Lecture_student
from models import Course_teachers

@user_login_required
def course_enroll(request):
    try:
        action = request.POST['action']
        course_ids = request.POST.getlist('course_ids[]')
    except KeyError:
        pass
    else:
        if action == 'enroll':
            courses = Course.objects.filter(id__in=map(int, list(course_ids)))
            request.user.course_set.add(*courses)

    course_info = []
    course_list = Course.objects.exclude(id__in=request.user.course_set.all()).order_by('course_text')
    template = loader.get_template('courses/course_enroll.html')
    #teacher_list = User.object.filter(is_staff=1)
    
    for course in course_list:
        teachers = course.teachers.filter(is_staff=1)
        course_info.append((course, teachers))
    
    context = RequestContext(request, {
        'course_list': course_list,
        'course_info': course_info,
        'title': 'Select a course you want to enroll',
    })
    
    return HttpResponse(template.render(context))

def course_results(request, course_id):
    response = "You're looking at the results of course %s."
    return HttpResponse(response % course_id)

def course_detail(request, course_id):
    return HttpResponse("You're looking at course %s." % course_id)

@user_login_required
def course_index(request):
    #course_list = Course.objects.order_by('course_text')
    #course_list = Course.objects.filter(teachers_id=request.user.id).order_by('course_text')
    course_list = request.user.course_set.all().order_by('course_text')
    
    template = loader.get_template('courses/course_index.html')

    context = RequestContext(request, {
        'course_list': course_list,
        'title': 'Courses',
    })

    return HttpResponse(template.render(context))
    
@user_login_required
def lecture_index(request, course_id):
    course_list = request.user.course_set.all()
    course = get_object_or_404(course_list, id=course_id)
    
    lecture_list = course.lectures.order_by('lecture_text')

    template = loader.get_template('courses/lecture_index.html')

    context = RequestContext(request, {
        'lecture_list': lecture_list,
        'course_id' : course_id,
        'title': 'Lectures',
    })

    return HttpResponse(template.render(context))

@user_login_required
def question_index(request, course_id, lecture_id):
    course_list = request.user.course_set.all()
    get_object_or_404(course_list, id=course_id)
    
    lecture = Lecture.objects.get(id=lecture_id)
    
    question_list = lecture.questions.filter(voting=0).order_by('-pub_date')    
    
    template = loader.get_template('courses/question_index.html')
    context = RequestContext(request, {
        'lecture': lecture,
        'question_list': question_list,
        'course_id': course_id,
        'lecture_id': lecture_id,
        'title': 'Questions',
    })

    return HttpResponse(template.render(context))

@user_login_required
def answer_index(request, course_id, lecture_id, question_id):
    question = Question.objects.get(id=question_id)
    answer_list = question.answers.order_by('answer_text')
    template = loader.get_template('courses/answer_index.html')    
    context = RequestContext(request, {
        'answer_list': answer_list,
        'course_id': course_id,
        'lecture_id': lecture_id,
        'question_id': question_id,
        'title': 'Answers',
    })

    return HttpResponse(template.render(context))

@user_login_required
def results(request, course_id, lecture_id, question_id):
    q = get_object_or_404(Question, pk=question_id)
    l = get_object_or_404(Lecture, pk=lecture_id)
    return render(request, 'courses/results.html', {'question': q, 'lecture': l})

@user_login_required
def vote(request, course_id, lecture_id, question_id):
    q = get_object_or_404(Question, pk=question_id)
    l = get_object_or_404(Lecture, pk=lecture_id)
    try:
        selected_answer = q.answers.get(pk=request.POST['answer'])
        print selected_answer
    except (KeyError, Answer.DoesNotExist):
        # Redisplay the poll voting form.
        return render(request, 'courses/vote.html', {
            'question':q,
            'lecture':l,
        })
    else:
        selected_answer.votes += 1
        selected_answer.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('courses:results', args=(course_id, lecture_id, question_id,)))

@user_login_required
def answer(request, course_id, lecture_id, question_id):
    q = get_object_or_404(Question, pk=question_id)
    l = get_object_or_404(Lecture, pk=lecture_id)
    try:
        givenAnswer = request.POST['answer']

        print givenAnswer
    except (KeyError, Answer.DoesNotExist):
        # Redisplay the poll answering form.
        return render(request, 'courses/answer.html', {
            'question': q,
            'lecture': l,
        })
    else:
        q.answers.create(answer_text=givenAnswer, votes=0)
        lecture = Lecture_student(lecture_id = lecture_id, user_id = request.user.id)
        lecture.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('courses:vote', args=(course_id, lecture_id, question_id,)))

def ajax_vote(request, course_id, lecture_id, question_id):
    q = get_object_or_404(Question, pk=question_id)
    l = get_object_or_404(Lecture, pk=lecture_id)

    try:
        selected_choice = q.answers.get(pk=request.POST['choice'])
    except (KeyError, Answer.DoesNotExist):
        return HttpResponseServerError("You didn't select a choice.")
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('courses:results', args=(course_id, lecture_id, question_id,)))
