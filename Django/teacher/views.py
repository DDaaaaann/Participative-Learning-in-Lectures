from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime, timedelta
from collections import Counter
from random import shuffle
from operator import itemgetter

from courses.models import Course
from courses.models import Lecture
from courses.models import Question
from courses.models import Answer
from courses.models import Lecture_student
from courses.models import Course_teachers



def course_results(request, course_id):
    response = "You're looking at the results of course %s."
    return HttpResponse(response % course_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

def course_detail(request, course_id):
    return HttpResponse("You're looking at course %s." % course_id)

    
@staff_member_required
def course_index(request):
    course_list = request.user.course_set.all().order_by('course_text')
    #course_list = Course.objects.filter(teachers_id=request.user.id).order_by('-course_text')

    template = loader.get_template('teacher/course_index.html')

    context = RequestContext(request, {
        'title': 'Select a Course',
        'course_list': course_list,
    })

    return HttpResponse(template.render(context))
    
@staff_member_required
def lecture_index(request, course_id):
    course_list = request.user.course_set.all()
    course = get_object_or_404(course_list, id=course_id)
    
    lecture_list = course.lectures.order_by('lecture_text')

    template = loader.get_template('teacher/lecture_index.html')

    context = RequestContext(request, {
        'title': 'Lectures',
        'lecture_list': lecture_list,
        'course_id' : course_id
    })

    return HttpResponse(template.render(context))

@staff_member_required
def question_index(request, course_id, lecture_id):
    lecture = Lecture.objects.get(id=lecture_id)
    question_list = lecture.questions.order_by('-pub_date')
    
    if question_list:
        for q in question_list:
            print q
        
            #votingstart = q.vote_start - timedelta(seconds=q.answer_time)
            votingend = q.vote_start + timedelta(seconds=(3*q.vote_duration))
            now = datetime.now() + timedelta(hours=1)
        
            if votingend < now:
                q.voting = 0
        
            q.save()

    template = loader.get_template('teacher/question_index.html')

    context = RequestContext(request, {
        'title': 'Questions',
        'question_list': question_list,
        'course_id': course_id,
        'lecture_id': lecture_id,
    })

    return HttpResponse(template.render(context))

def patternRecognition(question_id):
    # This function only works with one question at a time. The site completely
    # blocks when multiple questions are selected at the question_index page. I
    # think, however, this isn't a problem we should be worrying about, since
    # this function should be automatically called at the teacher's answer_index
    # page.
    """
    Search the answers of a question for commonalities. This might help the
    teacher to get an overall impression of the students' knowledge on the
    subject.
    """
    # Get the language from the question.
    englishQuestion = Question.objects.filter(id=question_id)[0].english
    # Set up a list of all the words that should be filtered.
    if englishQuestion:
        nonNouns = ['a', 'an', 'of', 'the']
    else:
        nonNouns = ['de', 'het', 'een', 'of']
    # Get all the answers out of the database.
    list_of_answers = Answer.objects.filter(question_id=question_id)
    if not list_of_answers:
        return []
    # Put all the words of the answers into an array, or a list.
    words = []
    for answer in list_of_answers:
        words += answer.answer_text.lower().split()
    # Remove all interpunction.
    newWords = []
    for word in words:
        #newWord = ''.join(c for c in word if c not in '.,?:!/;')
        newWords.append(''.join(c for c in word if c not in '.,?:!/;'))
    # Remove the abundant words.
    newList = [item for item in newWords if item not in nonNouns]
    # Search for repeating words.
    count = Counter(newList).most_common(20)
    # Show the most repeating words, nicely.
    print "Counted the words:"
    print count
    maxAmount = max(list(count), key=itemgetter(1))[1]
    finalRanking = []
    maxFontSize = 7
    for item, amount in list(count):
        fontSize = max(1, (maxFontSize * amount) / maxAmount)
        finalRanking.append((item, fontSize))
    shuffle(finalRanking)
    return finalRanking
    
@staff_member_required
def answer_index(request, question_id, course_id, lecture_id):
    question = Question.objects.get(id=question_id)
    answer_list = question.answers.order_by('-answer_text')
    count = patternRecognition(question_id)
    template = loader.get_template('teacher/answer_index.html')

    context = RequestContext(request, {
        'title': 'Answers',
        'answer_list': answer_list,
        'course_id': course_id,
        'lecture_id': lecture_id,
        'question_id': question_id,
        'count': count,
    })

    return HttpResponse(template.render(context))

def openVoting(request, course_id, lecture_id):
    l = get_object_or_404(Lecture, pk=lecture_id)
    try:
        givenQuestionID = request.GET['question_id']
    except (KeyError, Question.DoesNotExist):
        # Redisplay the question_index page.
        return render(request, 'teacher/question_index.html', {
        })
    else:
        m = l.questions.get(id=givenQuestionID)
        m.answerable=True
        m.voting=True
        
        if m.vote_duration is 0:
            m.vote_duration = 30;
        
        if m.answer_time is 0:
            m.answer_time = 60;
        
        m.vote_start = datetime.now() + timedelta(seconds=m.answer_time) + timedelta(hours=1)
        m.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('teacher:question_index', args=(course_id, lecture_id,)))

def closeVoting(request, course_id, lecture_id):
    l = get_object_or_404(Lecture, pk=lecture_id)
    try:
        givenQuestionID = request.GET['question_id']
    except (KeyError, Question.DoesNotExist):
        # Redisplay the question_index page.
        return render(request, 'teacher/question_index.html', {
        })
    else:
        m = l.questions.get(id=givenQuestionID)
        m.answerable=False
        m.voting=False
        m.vote_start = datetime.now() + timedelta(hours=1)
        m.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('teacher:question_index', args=(course_id, lecture_id,)))
        
def startSession(request, course_id, lecture_id):
    l = get_object_or_404(Lecture, pk=lecture_id)
    
    lecture = Lecture.objects.get(id=lecture_id)
    question_list = lecture.questions.order_by('-pub_date')
    
    i = 0
    
    totaltime = 7200
    
    if question_list:
        for q in question_list:
            q.voting=True
            q.answerable=True
            
            if q.vote_duration is 0:
                q.vote_duration = 30;
        
            if q.answer_time is 0:
                q.answer_time = 60;
                
            totaltime += q.answer_time
                
            q.vote_start = datetime.now() + timedelta(seconds=totaltime) 
            
            totaltime += (3 * q.vote_duration)
            
            i += 1
            
            q.save()
    
    return HttpResponseRedirect(reverse('teacher:question_index', args=(course_id, lecture_id,)))

def editToggleLecture(request, course_id):
    c = get_object_or_404(Course, pk=course_id)
    try:
        givenLectureID = request.GET['lecture_id']
    except (KeyError, Lecture.DoesNotExist):
        # Redisplay the question_index page.
        return render(request, 'teacher/lecture_index.html', {
        })
    else:
        m = c.lectures.get(id=givenLectureID)
        m.editable = not m.editable
        m.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('teacher:lecture_index', args=(course_id,)))

def editToggleQuestion(request, course_id, lecture_id):
    l = get_object_or_404(Lecture, pk=lecture_id)
    try:
        givenQuestionID = request.GET['question_id']
    except (KeyError, Question.DoesNotExist):
        # Redisplay the question_index page.
        return render(request, 'teacher/question_index.html', {
        })
    else:
        m = l.questions.get(id=givenQuestionID)
        print m.editable
        m.editable = not m.editable
        print m.editable
        m.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('teacher:question_index', args=(course_id, lecture_id,)))

def saveChangesLecture(request, course_id):
    c = get_object_or_404(Course, pk=course_id)
    try:
        givenLectureID = request.POST['lecture_id']
        givenLectureText = request.POST['lectureText']
        givenAnswerTime = request.POST['answerTime']
        givenVoteTime = request.POST['voteTime']
    except (KeyError, Lecture.DoesNotExist):
        # Redisplay the question_index page.
        return render(request, 'teacher/lecture_index.html', {
        })
    else:
        l = c.lectures.get(id=givenLectureID)
        l.lecture_text=givenLectureText
        l.save()
        m = l.questions.all()
        for q in m:
            if givenAnswerTime is not u'':
                q.answer_time=givenAnswerTime
            if givenVoteTime is not u'':
                q.vote_duration=givenVoteTime
            q.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('teacher:lecture_index', args=(course_id,)))

def saveChangesQuestion(request, course_id, lecture_id):
    l = get_object_or_404(Lecture, pk=lecture_id)
    try:
        givenQuestionID = request.POST['question_id']
        givenQuestionText = request.POST['questionText']
        givenAnswerTime = request.POST['answerTime']
        givenVoteTime = request.POST['voteTime']
    except (KeyError, Question.DoesNotExist):
        # Redisplay the question_index page.
        return render(request, 'teacher/question_index.html', {
        })
    else:
        m = l.questions.get(id=givenQuestionID)
        m.question_text=givenQuestionText
        m.answer_time=givenAnswerTime
        m.vote_duration=givenVoteTime
        m.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('teacher:question_index', args=(course_id, lecture_id,)))

def profile_page(request):
    a=User.objects.get(pk=request.user.id)
    course_list = request.user.course_set.all().order_by('course_text')
    # profile = a.get_profile().username
    tid = request.user.id
    pw = request.user.password
    template = loader.get_template('teacher/profilepage.html')

    context = RequestContext(request, {
        'title': 'My profile',
        'profile': a,
        'teach_id': tid,
        'course_list': course_list,
    })

    return HttpResponse(template.render(context))

def answer(request, course_id, lecture_id, question_id):
    q = get_object_or_404(Question, pk=question_id)
    l = get_object_or_404(Lecture, pk=lecture_id)
    try:
        givenAnswer = request.POST['answer']

        print givenAnswer
    except (KeyError, Answer.DoesNotExist):
        # Redisplay the poll answering form.
        return render(request, 'teacher/answer.html', {
            'question': q,
            'lecture': l,
        })
    else:
        q.answers.create(answer_text=givenAnswer, votes=0)
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('teacher:answer_index', args=(course_id, lecture_id, question_id,)))

def question(request, course_id, lecture_id):
    l = get_object_or_404(Lecture, pk=lecture_id)
    try:
        givenQuestion = request.POST['question']
        print givenQuestion
        tags = request.POST['tags']
        print tags
    except (KeyError, Question.DoesNotExist):
        # Redisplay the Set-The-Question screen.
        return render(request, 'teacher/question.html', {
            'lecture': l,
        })
    else:
        l.questions.create(question_text=givenQuestion, tags=tags)
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('teacher:question_index', args=(course_id, lecture_id,)))

def lecture(request, course_id):
    c = get_object_or_404(Course, pk=course_id)
    try:
        givenLecture = request.POST['lecture']
        print givenLecture
    except (KeyError, Lecture.DoesNotExist):
        # Redisplay the Set-The-Lecture screen.
        return render(request, 'teacher/lecture.html', {
            'course': c,
        })
    else:
        lecture = Lecture(lecture_text=givenLecture, course_id=course_id, editable=False)
        lecture.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('teacher:lecture_index', args=(course_id,)))

def course(request):
    try:
        givenCourse = request.POST['course']
        print givenCourse
        givenCatNumber = request.POST['catNumber']
        print givenCatNumber
    except (KeyError, Course.DoesNotExist):
        # Redisplay the Set-The-Course screen.
        return render(request, 'teacher/course.html', {
        })
    else:
        course = Course(course_text=givenCourse, cat_number=givenCatNumber)
        course.save()
        course = Course_teachers(course_id=course.id, user_id=request.user.id)
        course.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('teacher:course_index',))

def analytics(request):
    return render(request, 'teacher/teacher_analytics.html', {
        })