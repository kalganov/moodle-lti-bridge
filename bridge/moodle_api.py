import logging
import uuid

import requests
from lti import ToolConsumer

from bridge.constants import FIRST_NAME, LAST_NAME, EMAIL

logger = logging.getLogger(__name__)


def get_best_grade(api_url, token, user_id, quiz_id):
    function = 'mod_quiz_get_user_best_grade'
    data = {
        'userid': user_id,
        'quizid': quiz_id
    }
    response = moodle_function(api_url, token, function, data)
    if response['hasgrade']:
        return response['grade']
    else:
        return -1


def get_user_attempts(api_url, token, user_id, quiz_id):
    function = 'mod_quiz_get_user_attempts'
    data = {
        'userid': user_id,
        'quizid': quiz_id,
        'status': 'all'
    }
    return moodle_function(api_url, token, function, data)


def get_quizzes_by_courses(api_url, token, course_id):
    function = 'mod_quiz_get_quizzes_by_courses'
    data = {
        'courseids[0]': course_id
    }
    return moodle_function(api_url, token, function, data)


def get_user(api_url, token, email):
    function = 'core_user_get_users'
    # function = 'core_search_get_relevant_users'
    data = {
        'criteria[0][key]': 'email',
        'criteria[0][value]': email
    }
    users = moodle_function(api_url, token, function, data)['users']
    if not users:
        return None
    return users[0]


def moodle_function(api_url, token, function, data):
    logger.info("Call moodle function: " + api_url)
    logger.info("Request data: " + str(data))
    return requests.post(api_url.format(token, function), data=data, verify=False).json()


if __name__ == "__main__":
    #An example of using
    user = get_user('https://194.85.169.105:80/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}',
                       '7be25066e116fb2a4cf12d9441f2675c', 'solodkovnikita08@gmail.com')
    user_id = user['id']
    consumer = ToolConsumer(consumer_key='50116f79-0e69-4556-b800-d3ed286bb419',
                            launch_url='https://194.85.169.105:80/enrol/lti/tool.php?id=36',
                            consumer_secret='test',
                            params={'lti_message_type': 'basic-lti-launch-request',
                                    'lti_version': 'LTI-1p0',
                                    'tool_consumer_info_product_family_code': 'moodle',
                                    'roles': 'Student',
                                    FIRST_NAME: user['firstname'],
                                    LAST_NAME: user['lastname'],
                                    EMAIL: user['email'],
                                    'resource_link_id': str(uuid.uuid4())})
    quiz_id = list(filter(lambda x: x['name'] == 'Структуры 1', get_quizzes_by_courses(
        'https://194.85.169.105:80/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}',
        '7be25066e116fb2a4cf12d9441f2675c', 2)['quizzes']))[0]['id']
    attempt_id = get_user_attempts(
        'https://194.85.169.105:80/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}',
        '7be25066e116fb2a4cf12d9441f2675c', user_id, quiz_id)['attempts'][0]['id']
