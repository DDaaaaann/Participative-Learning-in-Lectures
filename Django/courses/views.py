from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views import generic

from models import Course
from models import Lecture
from models import Question
from models import Answer


def course_results(request, course_id):
    response = "You're looking at the results of course %s."
    return HttpResponse(response % course_id)

def course_detail(request, course_id):
    return HttpResponse("You're looking at course %s." % course_id)

def course_index(request):
    course_list = Course.objects.order_by('course_text')
    #course_list = Course.objects.filter(teachers_id=request.user.id).order_by('course_text')

    template = loader.get_template('courses/course_index.html')

    context = RequestContext(request, {
        'course_list': course_list,
        'title': "",
    })

    return HttpResponse(template.render(context))

def lecture_index(request, course_id):
    course = Course.objects.get(id=course_id)
    #course = course.lectures.get(teacher_id=request.user.id)
    lecture_list = course.lectures.order_by('lecture_text')
    #lecture_list = course.lectures.filter(teacher_id=request.user.id).order_by('-lecture_text')

    template = loader.get_template('courses/lecture_index.html')

    context = RequestContext(request, {
        'lecture_list': lecture_list,
        'course_id' : course_id,
    })

    return HttpResponse(template.render(context))


def question_index(request, course_id, lecture_id):
    lecture = Lecture.objects.get(id=lecture_id)
    question_list = lecture.questions.order_by('-pub_date')
    template = loader.get_template('courses/question_index.html')
    context = RequestContext(request, {
        'lecture': lecture,
        'question_list': question_list,
        'course_id': course_id,
        'lecture_id': lecture_id,
    })

    return HttpResponse(template.render(context))


def answer_index(request, course_id, lecture_id, question_id):
    question = Question.objects.get(id=question_id)
    answer_list = question.answers.order_by('answer_text')
    template = loader.get_template('courses/answer_index.html')    
    context = RequestContext(request, {
        'answer_list': answer_list,
        'course_id': course_id,
        'lecture_id': lecture_id,
        'question_id': question_id,
    })

    return HttpResponse(template.render(context))

def results(request, course_id, lecture_id, question_id):
    q = get_object_or_404(Question, pk=question_id)
    l = get_object_or_404(Lecture, pk=lecture_id)
    return render(request, 'courses/results.html', {'question': q, 'lecture': l})

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
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('courses:vote', args=(course_id, lecture_id, question_id,)))

def question(request, course_id, lecture_id):
    l = get_object_or_404(Lecture, pk=lecture_id)
    try:
        givenQuestion = request.POST['question']
        print givenQuestion
        tags = request.POST['tags']
        print tags
    except (KeyError, Question.DoesNotExist):
        # Redisplay the Set-The-Question screen.
        return render(request, 'courses/question.html', {
            'lecture': l,
        })
    else:
        l.questions.create(question_text=givenQuestion, tags=tags)
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('courses:question_index', args=(course_id, lecture_id,)))

def lecture(request, course_id):
    c = get_object_or_404(Course, pk=course_id)
    try:
        givenLecture = request.POST['lecture']
        print givenLecture
    except (KeyError, Lecture.DoesNotExist):
        # Redisplay the Set-The-Lecture screen.
        return render(request, 'courses/lecture.html', {
            'course': c,
        })
    else:
        c.lectures.create(lecture_text=givenLecture, teacher_id=11)
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('courses:lecture_index', args=(course_id,)))

def course(request):
    try:
        givenCourse = request.POST['course']
        print givenCourse
    except (KeyError, Course.DoesNotExist):
        # Redisplay the Set-The-Course screen.
        return render(request, 'courses/course.html', {
        })
    else:
        c = Course.objects.create(course_text=givenCourse, teachers_id=11)
        c.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('courses:course_index',))
