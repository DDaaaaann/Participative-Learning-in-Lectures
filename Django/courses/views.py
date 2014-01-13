from django.http import HttpResponse
from django.template import RequestContext, loader

from models import Course
from models import Lecture
from models import Question
from models import Answer


def course_results(request, course_id):
    response = "You're looking at the results of course %s."
    return HttpResponse(response % course_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

def course_detail(request, course_id):
    return HttpResponse("You're looking at course %s." % course_id)

def course_index(request):
    course_list = Course.objects.order_by('-course_text')

    template = loader.get_template('courses/course_index.html')

    context = RequestContext(request, {
        'course_list': course_list,
    })

    return HttpResponse(template.render(context))

def lecture_index(request, course_id):
    course = Course.objects.get(id=course_id)
    lecture_list = course.lectures.order_by('-lecture_text')

    template = loader.get_template('courses/lecture_index.html')

    context = RequestContext(request, {
        'lecture_list': lecture_list,
        'course_id' : course_id
    })

    return HttpResponse(template.render(context))


def question_index(request, course_id, lecture_id):
    lecture = Lecture.objects.get(id=lecture_id)
    question_list = lecture.questions.order_by('-pub_date')

    template = loader.get_template('courses/question_index.html')

    print question_list

    context = RequestContext(request, {
        'question_list': question_list,
        'course_id': course_id,
        'lecture_id': lecture_id,
    })

    return HttpResponse(template.render(context))


def answer_index(request, question_id, course_id, lecture_id):
    question = Question.objects.get(id=question_id)
    answer_list = question.answers.order_by('-answer_text')

    template = loader.get_template('courses/answer_index.html')

    context = RequestContext(request, {
        'answer_list': answer_list,
        'course_id': course_id,
        'lecture_id': lecture_id,
        'question_id': question_id,
    })

    return HttpResponse(template.render(context))

