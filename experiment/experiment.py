import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.cluster import KMeans

from bridge.constants import THI, ERROR
from bridge.models import Task, User
from ltibridge.settings import graph


def print_user_stats(user):
    print('User ' + user.last_name + ' did ' + str(len(user.did)) + ' tasks')
    for skill in user.knows:
        print(skill.label + ' ' + str(user.knows.get(skill, THI)) + ' ' + str(user.knows.get(skill, ERROR)))
        user_did_for_this_skill = sorted(list(filter(lambda x: skill in list(x.sub_descriptor), list(user.did))),
                                         key=lambda x: user.did.get(x, 'num'))
        for task in user_did_for_this_skill:
            print(task.label + ' ' + str(user.did.get(task, 'grade')) + ' ' + str(user.did.get(task, 'num')))


if __name__ == "__main__":
    predicted_scores = pd.read_csv('compet.csv', sep=';',
                                   encoding='UTF-8', index_col='Имя')
    corelation_csv = predicted_scores.copy()
    irt_scores = predicted_scores.copy()

    tasks = list(Task.match(graph))
    users = list(User.match(graph))

    completed_tasks_count = 0
    min_task_count = 10000
    most_success_user = None
    users_participated = 0

    skills_to_mark = {}

    for user in users:
        name = user.last_name
        if name != 'Тодиков' \
                and name != 'Шэн' \
                and name != 'Усольцев' \
                and name != 'Севастьянова' \
                and name != 'Храпова':
            user_tasks_count = len(user.did)
            if user_tasks_count == 0:
                continue

            print_user_stats(user)

            for skill in user.knows:
                thi = user.knows.get(skill, THI)
                marks = skills_to_mark.get(skill.label)
                if not marks:
                    skills_to_mark.update({skill.label: [(user.last_name, thi)]})
                else:
                    marks.append((user.last_name, thi))
                    skills_to_mark.update({skill.label: sorted(marks, key=lambda mark: mark[1])})

            if user_tasks_count < min_task_count:
                min_task_count = user_tasks_count
                most_success_user = user

            completed_tasks_count = completed_tasks_count + user_tasks_count
            users_participated = users_participated + 1
            print('-------------------------------------------------------------')

    print('Users participated: ' + str(users_participated))
    print('Completed tasks count: ' + str(completed_tasks_count))
    print('Average tasks ' + str(completed_tasks_count / users_participated))
    print('The strongest user ' + most_success_user.last_name)
    print_user_stats(most_success_user)

    partitioning = {
        'Умеет работать с полями структуры': [-0.5, 1.5],
        'Знает правила объявления структур': [-0.6, 1.4],
        'Умеет выделять память под структуры': [0.5, 1.5],
        'Знает, что такое  формат CSV': [1.5, 2.5],
        'Умеет работать с файлами формата CSV': [1, 2],
        'Умеет выделять память под массивы структур': [-0.5, 1.5],
        'Умеет работать с полями массивов структур': [2, 3],

    }

    k_means_partitioning = {}

    corelation = {}

    y_true = {}
    y_pred = {}

    for label in skills_to_mark.keys():
        y_true.update({label: []})
        y_pred.update({label: []})

    for label, values in skills_to_mark.items():
        x_values = np.arange(len(values))
        marks = list(map(lambda x: x[1], values))

        plt.plot(marks, x_values, 'bo')
        plt.title(label, fontsize=15)
        plt.xlabel('θ', fontsize=15)
        plt.yticks(x_values, list(map(lambda x: x[0], values)))

        for i, thi in enumerate(marks):
            plt.text(thi + 0.1, i - 0.1, np.round(thi, 2))

        scores = np.array(marks).reshape(-1, 1)
        kmeans = KMeans(n_clusters=2, random_state=0).fit(scores)

        centres = list(sorted(map(lambda x: x[0], kmeans.cluster_centers_)))
        for line in centres:
            plt.axvline(x=line, color='r')
        k_means_partitioning.update({label: centres})

        user_to_score = dict(map(lambda x: (x[0], x[1]), values))
        right_correlation = 0
        sum_correlation = 0
        for name, score in user_to_score.items():
            if name != 'Тодиков' \
                    and name != 'Шэн' \
                    and name != 'Усольцев' \
                    and name != 'Севастьянова' \
                    and name != 'Храпова':
                # try:
                irt_scores[label][name] = np.round(score, 2)
                pred_score = predicted_scores[label][name]
                intervals = list(k_means_partitioning[label])
                intervals.append(10)
                predicted_class = 0
                for center in intervals:
                    if float(pred_score.replace(',', '.')) < center and score < center:
                        predicted_class = predicted_class + 1
                        continue

                    if not (float(pred_score.replace(',', '.')) < center or score < center):
                        y_true.update({label: y_true.get(label) + [predicted_class]})
                        y_pred.update({label: y_pred.get(label) + [predicted_class]})
                        right_correlation = right_correlation + 1
                        corelation_csv[label][name] = True
                        break
                    else:
                        if not float(pred_score.replace(',', '.')) < center:
                            y_true.update({label: y_true.get(label) + [predicted_class]})
                        else:
                            y_true.update({label: y_true.get(label) + [predicted_class + 1]})

                        if not score < center:
                            y_pred.update({label: y_pred.get(label) + [predicted_class]})
                        else:
                            y_pred.update({label: y_pred.get(label) + [predicted_class + 1]})
                        print(f"Wrong correlation {label} {name} {score} {pred_score}")
                        corelation_csv[label][name] = False
                        break
                sum_correlation = sum_correlation + 1
        corelation.update({label: right_correlation / sum_correlation})

        plt.show()

    warnings.filterwarnings('ignore')
    for label in y_true.keys():
        print(label)
        print(metrics.confusion_matrix(y_true.get(label), y_pred.get(label)))
        print(metrics.classification_report(y_true.get(label), y_pred.get(label)))

    for label in y_true.keys():
        print(f"{label} : {np.round(metrics.accuracy_score(y_true.get(label), y_pred.get(label)), 2)}")

    print('-------------------------------------------------------')
    for label in y_true.keys():
        print(f"{label} : {np.round(metrics.precision_score(y_true.get(label), y_pred.get(label)), 2)}")

    print('-------------------------------------------------------')
    for i in k_means_partitioning.items():
        print(f"{i[0]}: {np.round(i[1], 2)}")

    print('-------------------------------------------------------')
    for i in corelation.items():
        print(f"{i[0]}: {np.round(i[1], 2)}")

    corelation_csv.to_csv('correlation.csv')
    irt_scores.to_csv('irt_score.csv')
