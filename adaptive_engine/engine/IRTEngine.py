import logging

import numpy as np

from adaptive_engine.engine.IEngine import IEngine
from bridge import models
from bridge.constants import *

logger = logging.getLogger(__name__)


class IRTEngine(IEngine):

    def select_activity(self, activities, **params):
        logger.debug("(IRT) Activities: " + str(activities))
        if not activities:
            logger.error("(IRT) There are no activities")
            return None

        user_data = params['user_data']
        user = models.get_user(user_data[EMAIL])
        topic = models.get_topic(user_data[TITLE])

        target_descriptor = list(
            filter(lambda x: topic.sub_descriptors.get(x, 'target') is True, topic.sub_descriptors))
        logger.debug("(IRT) Target descriptor: " + str(target_descriptor))

        if target_descriptor:
            return get_most_satisfied_item(activities, target_descriptor[0], user)
        else:
            descriptors_to_learn = get_descriptors_to_learn(activities, topic.sub_descriptors, user)

            if descriptors_to_learn:
                return get_most_satisfied_item(activities, descriptors_to_learn[0], user)

    def commit_result(self, user, task, grade):
        if grade >= 1:
            grade = 1

        if grade < 1:
            grade = 0

        user.did.add(task, properties={'grade': grade, 'num': len(user.did)})

        for sd in task.sub_descriptor:
            task_answer = {
                'a': task.sub_descriptor.get(sd, 'a'),
                'b': task.sub_descriptor.get(sd, 'b'),
                'ans': grade
            }

            thi = get_thi(sd, user)

            numerator = get_numerator(sd, user)

            denominator = get_denominator(sd, user)

            new_thi, new_numerator, new_denominator = thi_next(thi, numerator, denominator, task_answer)

            user.knows.update(sd, properties={
                THI: new_thi,
                NUMERATOR: new_numerator,
                DENOMINATOR: new_denominator,
                ERROR: square_error(new_denominator)
            })

        return user


def P(thi, a, b):
    return np.exp(a * (thi - b)) / (1 + np.exp(a * (thi - b)))


def I(thi, x):
    p = P(thi, x['a'], x['b'])
    return x['a'] ** 2 * p * (1 - p)


def thi_next(thi, numerator, denominator, task_answer):
    p = P(thi, task_answer['a'], task_answer['b'])
    numerator = numerator + task_answer['a'] * (task_answer['ans'] - p)
    denominator = denominator + I(thi, task_answer)

    return thi + numerator / denominator, numerator, denominator


def square_error(denominator):
    return 1 / (denominator ** 0.5)


def get_thi(target_descriptor, user):
    thi = user.knows.get(target_descriptor, THI)
    if not thi:
        thi = APRIOR_THI
    return thi


def get_error(target_descriptor, user):
    error = user.knows.get(target_descriptor, ERROR)
    if not error:
        error = 100000
    return error


def get_denominator(target_descriptor, user):
    denominator = user.knows.get(target_descriptor, DENOMINATOR)
    if not denominator:
        denominator = 0
    return denominator


def get_numerator(target_descriptor, user):
    numerator = user.knows.get(target_descriptor, NUMERATOR)
    if not numerator:
        numerator = 0
    return numerator


def get_most_satisfied_item(activities, target_descriptor, user):
    thi = get_thi(target_descriptor, user)
    activities = list(filter(lambda x: x in target_descriptor.tasks, activities))
    I_max = -100
    most_satisfied_item = None
    for item in activities:
        task = {
            'a': item.sub_descriptor.get(target_descriptor, 'a'),
            'b': item.sub_descriptor.get(target_descriptor, 'b')
        }
        I_cur = I(thi, task)
        if I_cur > I_max:
            most_satisfied_item = item
            I_max = I_cur
    return most_satisfied_item


def get_descriptors_to_learn(activities, descriptors, user):
    descriptors_to_learn = list()
    for descriptor in descriptors:
        thi = get_thi(descriptor, user)
        error = get_error(descriptor, user)
        target_thi = descriptors.get(descriptor, THI)

        if thi - error > target_thi:
            continue

        tasks_to_learn_descriptor = list(filter(lambda x: x in descriptor.tasks, activities))

        if tasks_to_learn_descriptor:
            descriptors_to_learn.append(descriptor)
    return descriptors_to_learn
