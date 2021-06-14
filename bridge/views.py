import logging
import uuid
from urllib.parse import urlparse

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from lti import ToolConsumer

from bridge import moodle_api, models, engine
from bridge.constants import *
from ltibridge.settings import SERVER_URL

logger = logging.getLogger(__name__)


@csrf_exempt
def moodle_provider(request):
    if request.method == 'POST':
        logger.info('Incoming request to provider from ' + str(request.POST))
        netloc = urlparse(request.headers.get('Origin')).netloc.split(':')[0]

        logger.info('Host from url ' + netloc)
        source = models.get_source(netloc)

        if not source:
            # TODO return 404 when source not found
            logger.error('No source for ' + netloc)

        request.session['source_url'] = source.api_url
        request.session['source_token'] = source.token

        internal_user = moodle_api.get_user(source.api_url, source.token, request.POST.get(EMAIL))
        if not internal_user:
            user_create_request = {
                FIRST_NAME: request.POST.get(FIRST_NAME),
                LAST_NAME: request.POST.get(LAST_NAME),
                EMAIL: request.POST.get(EMAIL)
            }
            logger.info('User was not found in moodle create a new one' + str(user_create_request))
            models.create_user(user_create_request)
            request.session['user_id'] = None
        else:
            logger.info('User was found in moodle ' + str(internal_user))
            request.session['user_id'] = internal_user['id']

        request.session['user_data'] = {
            FIRST_NAME: request.POST.get(FIRST_NAME),
            LAST_NAME: request.POST.get(LAST_NAME),
            EMAIL: request.POST.get(EMAIL),
            TITLE: request.POST.get('resource_link_title')
        }

        response = render(request, 'bridge/provider.html', {'grade_url': SERVER_URL + '/bridge/grade'})
        if request.COOKIES.get('MoodleSessionltiprovider'):
            logger.info("User has already login, remove cookie")
            response.delete_cookie('MoodleSessionltiprovider')
        return response
    return HttpResponse('')


@csrf_exempt
def grade(request):
    user_data = request.session['user_data']

    if not request.session['user_id']:
        user = moodle_api.get_user(request.session['source_url'], request.session['source_token'], user_data[EMAIL])
        if not user:
            logger.info("User has not assigned for the course yet " + request.session['user_id'])
            return JsonResponse({})
        user_id = user['id']
    else:
        user_id = request.session['user_id']

    user = models.get_user(user_data[EMAIL])

    task_label = request.session['task_label']
    task = models.get_task(task_label)

    if user.did.get(task, 'grade'):
        return JsonResponse(user.did.get(task, 'grade'))

    user_best_grade = moodle_api.get_best_grade(request.session['source_url'],
                                                request.session['source_token'],
                                                user_id, request.session['quiz_id'])

    if user_best_grade != -1:
        models.update_user(engine.commit_result(user, task, user_best_grade))

        return JsonResponse({
            'grade': user.did.get(task, 'grade')
        })

    return JsonResponse({})


def consumer(request):
    logger.info('Incoming request to consumer from ' + str(request.GET))
    logger.info("Request cookies: " + str(request.COOKIES.items()))
    logger.info("Request session: " + str(request.session.items()))
    activity, quiz_id = get_activity(request)

    if not activity:
        return render_results(request)

    request.session['quiz_id'] = quiz_id

    return render(
        request,
        'bridge/consumer.html',
        {
            'launch_data': activity.generate_launch_data(),
            'launch_url': activity.launch_url,
            'grade_url': SERVER_URL + '/bridge/grade'
        }
    )


def render_results(request):
    user_data = request.session['user_data']
    user = models.get_user(user_data[EMAIL])
    topic = models.get_topic(user_data[TITLE])
    descriptors = list()
    for descriptor in topic.sub_descriptors:
        thi = user.knows.get(descriptor, THI)
        if thi:
            descriptors.append({
                'label': descriptor.label,
                'thi': thi,
                'error': user.knows.get(descriptor, ERROR)
            })
    return render(request, 'bridge/provider_finish.html', {
        'descriptors': descriptors
    })


def get_activity(request):
    user_data = request.session['user_data']

    task, user = get_current_task(user_data)
    if not task:
        return None, None

    request.session['task_label'] = task.label
    logger.info('Launch url for current task ' + task.launch_url)
    consumer = ToolConsumer(consumer_key=user.consumer_key,
                            launch_url=task.launch_url,
                            consumer_secret=task.secret,
                            params={'lti_message_type': 'basic-lti-launch-request',
                                    'lti_version': 'LTI-1p0',
                                    'tool_consumer_info_product_family_code': 'moodle',
                                    'roles': 'Student',
                                    FIRST_NAME: user_data[FIRST_NAME],
                                    LAST_NAME: user_data[LAST_NAME],
                                    EMAIL: user_data[EMAIL],
                                    'resource_link_id': str(uuid.uuid4())})
    return consumer, task.quiz_id


def get_current_task(user_data):
    user = models.get_user(user_data[EMAIL])
    if not user:
        logger.error('User was not found in graph')
        # TODO Try to sync user in mooodle and model
        logger.info('Try to create a User ' + str(user_data))
        user_create_request = {
            FIRST_NAME: user_data[FIRST_NAME],
            LAST_NAME: user_data[LAST_NAME],
            EMAIL: user_data[EMAIL]
        }
        models.create_user(user_create_request)
        user = models.get_user(user_data[EMAIL])

    tasks = models.find_tasks(user_data[EMAIL], user_data[TITLE])
    activity = engine.select_activity(tasks, user_data=user_data)
    logger.info("Activity was selected by engine: " + str(activity))
    return activity, user
