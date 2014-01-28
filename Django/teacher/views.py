from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, QueryDict
from django.template.response import TemplateResponse
from django.utils.http import base36_to_int, is_safe_url, urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import ugettext as _
from django.utils.six.moves.urllib.parse import urlparse, urlunparse
from django.shortcuts import resolve_url, get_object_or_404, render
from django.utils.encoding import force_bytes, force_text
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from datetime import datetime, timedelta

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required



from courses.models import Course
from courses.models import Lecture
from courses.models import Question
from courses.models import Answer

@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/userLogin.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    
    
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())
            
            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def logout(request, next_page=None,
           template_name='registration/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           current_app=None, extra_context=None):
    """
    Logs out the user and displays 'You are logged out' message.
    """
    auth_logout(request)

    if next_page is not None:
        next_page = resolve_url(next_page)

    if redirect_field_name in request.REQUEST:
        next_page = request.REQUEST[redirect_field_name]
        # Security check -- don't allow redirection to a different host.
        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = request.path

    if next_page:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page)

    current_site = get_current_site(request)
    context = {
        'site': current_site,
        'site_name': current_site.name,
        'title': _('Logged out')
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
        current_app=current_app)


def logout_then_login(request, login_url=None, current_app=None, extra_context=None):
    """
    Logs out the user if he is logged in. Then redirects to the log-in page.
    """
    if not login_url:
        login_url = settings.LOGIN_URL
    login_url = resolve_url(login_url)
    return logout(request, login_url, current_app=current_app, extra_context=extra_context)


def redirect_to_login(next, login_url=None,
                      redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Redirects the user to the login page, passing the given 'next' page
    """
    resolved_url = resolve_url(login_url or settings.LOGIN_URL)

    login_url_parts = list(urlparse(resolved_url))
    if redirect_field_name:
        querystring = QueryDict(login_url_parts[4], mutable=True)
        querystring[redirect_field_name] = next
        login_url_parts[4] = querystring.urlencode(safe='/')

    return HttpResponseRedirect(urlunparse(login_url_parts))


# 4 views for password reset:
# - password_reset sends the mail
# - password_reset_done shows a success message for the above
# - password_reset_confirm checks the link the user clicked and
#   prompts for a new password
# - password_reset_complete shows a success message for the above

@csrf_protect
def password_reset(request, is_admin_site=False,
                   template_name='registration/password_reset_form.html',
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def password_reset_done(request,
                        template_name='registration/password_reset_done.html',
                        current_app=None, extra_context=None):
    context = {}
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


# Doesn't need csrf_protect since no-one can guess the URL
@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        validlink = False
        form = None
    context = {
        'form': form,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

def password_reset_confirm_uidb36(request, uidb36=None, **kwargs):
    # Support old password reset URLs that used base36 encoded user IDs.
    # Remove in Django 1.7
    try:
      uidb64 = force_text(urlsafe_base64_encode(force_bytes(base36_to_int(uidb36))))
    except ValueError:
      uidb64 = '1' # dummy invalid ID (incorrect padding for base64)
    return password_reset_confirm(request, uidb64=uidb64, **kwargs)

def password_reset_complete(request,
                            template_name='registration/password_reset_complete.html',
                            current_app=None, extra_context=None):
    context = {
        'login_url': resolve_url(settings.LOGIN_URL)
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


@sensitive_post_parameters()
@csrf_protect
@login_required
def password_change(request,
                    template_name='registration/password_change_form.html',
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    current_app=None, extra_context=None):
    if post_change_redirect is None:
        post_change_redirect = reverse('password_change_done')
    else:
        post_change_redirect = resolve_url(post_change_redirect)
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


@login_required
def password_change_done(request,
                         template_name='registration/password_change_done.html',
                         current_app=None, extra_context=None):
    context = {}
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)



def course_results(request, course_id):
    response = "You're looking at the results of course %s."
    return HttpResponse(response % course_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

def course_detail(request, course_id):
    return HttpResponse("You're looking at course %s." % course_id)

def course_change(request, course_id):
    course = Course.objects.get(id=course_id)
    return HttpResponse("You're looking at change_course for %s." % course_id)
    
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
    course = Course.objects.get(id=course_id)
    #course = course.lectures.get(teacher_id=request.user.id)
    lecture_list = course.lectures.filter(teacher_id=request.user.id).order_by('-lecture_text')

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

    template = loader.get_template('teacher/question_index.html')

    context = RequestContext(request, {
        'title': 'Questions',
        'question_list': question_list,
        'course_id': course_id,
        'lecture_id': lecture_id,
    })

    return HttpResponse(template.render(context))
    
@staff_member_required
def answer_index(request, question_id, course_id, lecture_id):
    question = Question.objects.get(id=question_id)
    answer_list = question.answers.order_by('-answer_text')

    template = loader.get_template('teacher/answer_index.html')

    context = RequestContext(request, {
        'title': 'Answers',
        'answer_list': answer_list,
        'course_id': course_id,
        'lecture_id': lecture_id,
        'question_id': question_id,
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
        
        if m.vote_duration is 0:
            m.vote_duration = 30;
        
        if m.answer_time is 0:
            m.answer_time = 60;
        
        m.vote_start = datetime.now() + timedelta(seconds=m.answer_time) + timedelta(hours=1);
        
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
        m.vote_start = datetime.now() + timedelta(hours=1);
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
    
    totaltime = 0
    
    if question_list:
        for q in question_list:
            q.voting=1
            
            if q.vote_duration is 0:
                q.vote_duration = 30;
        
            if q.answer_time is 0:
                q.answer_time = 60;
                
            totaltime += q.answer_time
                
            q.vote_start = datetime.now() + totaltime
            
            totaltime += 3 * q.vote_duration
            
            i += 1
    
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
        c.lectures.create(lecture_text=givenLecture, teacher_id=15)
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('teacher:lecture_index', args=(course_id,)))

def course(request):
    try:
        givenCourse = request.POST['course']
        print givenCourse
    except (KeyError, Course.DoesNotExist):
        # Redisplay the Set-The-Course screen.
        return render(request, 'teacher/course.html', {
        })
    else:
        Course.objects.create(course_text=givenCourse)
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('teacher:course_index',))
