from __future__ import division
from os.path import expanduser
import subprocess
from taskw import TaskWarrior
from base64 import b64encode
import requests
import json
import sys
from sys import argv

w = TaskWarrior(marshal=True)
home = expanduser("~")


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def get_taskwarrior_task():
    """ Return a Taskwarrior task based on the first arg to the script. """
    if (len(argv[1]) > 4):
        # Assume that IDs larger than 4 characters are UUIDs.
        task = w.get_task(uuid=argv[1])
    else:
        task = w.get_task(id=argv[1])
    return task


def get_harvest_comment(task):
    """ Load a Harvest comment to associate with the time record. """
    if (task['harvestcomment'] is not None):
        comment = task['harvestcomment']
    else:
        comment = raw_input('Enter a log message: ')
    return comment


def get_harvest_project(task):
    """ Load information about a Harvest project based on the Taskwarrior
        project.
    """
    project_map = get_project_map()
    if (task['project'] in project_map):
        return int(project_map[task['project']]['id']), \
            project_map[task['project']]['name']
    else:
        print('Project not in map.')
        exit(1)


def get_harvest_task_type(task, harvest_project_id):
    " Return a list of valid task types. """
    valid_task_types = get_task_type_map(harvest_project_id)
    # Reformat
    valid_task_type_dict = {}
    for task_type in valid_task_types:
        valid_task_type_dict[task_type['id']] = task_type['name']
    # Get user input
    # TODO: Make a select list
    for task_type in valid_task_types:
        print(str(task_type['id']) + " - " + task_type['name'])
    print('Enter the ID of the task type: ')
    user_task_type = int(raw_input())
    if (user_task_type in valid_task_type_dict):
        return int(user_task_type), valid_task_type_dict[user_task_type]
    else:
        print('Invalid task type ID')
        exit(1)


def get_project_map():
    """ Return a map of Taskwarrior projects to Harvest projects. """
    project_data = open(home + '/.harvest.projects.json')
    return json.load(project_data)


def get_task_type_map(project_id):
    """ Load the task type map. """
    json_data = open(home + '/.harvest.tasks.json')
    task_type_map = json.load(json_data)
    projects = task_type_map['projects']
    for project in projects:
        if int(project_id) == int(project['id']):
            return project['tasks']

    print('Invalid task type')
    exit(1)


def main():
    _, task = get_taskwarrior_task()
    print('Logging time for task "%s" in project "%s"' % (
        task['description'], task['project']))
    try:
        taskwarrior_timer = subprocess.check_output(
            ['task %d inf | grep "Total active time"' % task['id']],
            stderr=subprocess.STDOUT, shell=True)
        print('Taskwarrior timer: %s' % taskwarrior_timer)
    except subprocess.CalledProcessError as e:
        print('No time stored in taskwarrior')

    # TODO: Prompt for input
    if (task['actual'] is None):
        print('You need to log an actual time for this task first')
        exit(1)

    actual_time = (int(task['actual']) / 60) / 60
    harvest_comment = get_harvest_comment(task)
    harvest_project_id, harvest_project_name = get_harvest_project(task)
    harvest_task_type_id, harvest_task_type_name = get_harvest_task_type(
        task, harvest_project_id)

    print('Summary')
    print('-------')
    print('Task: %s' % task['description'])
    print('Log message: %s' % harvest_comment)
    print('Time: %s hours of %s in project %s' % (
        actual_time, harvest_task_type_name, harvest_project_name))

    if (query_yes_no("Continue with logging time?") is False):
        exit(1)

    payload = json.dumps({
        'notes': harvest_comment,
        'hours': actual_time,
        'project_id': harvest_project_id,
        'task_id': harvest_task_type_id,
        'spent_at': task['modified'].strftime("%a, %d %b %Y")
    })

    credentials_data = open(home + '/.harvest.credentials.json')
    credentials = json.load(credentials_data)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Basic ' + b64encode(
            '%s:%s' % (credentials['email'],
                        credentials['password']))
    }
    print('Posting to Harvest...')
    r = requests.post(
        "https://%s.harvestapp.com/daily/add" % credentials['subdomain'],
        data=payload, headers=headers)
    response = r.json()
    print("Successfully logged %s hours for task %s in project %s" % (
        response['hours'], response['task'], response['project']))
    # Update taskwarrior task
    task['harvestcomment'] = harvest_comment
    task['harvesttasktype'] = harvest_task_type_id
    task['harvestproject'] = harvest_project_id
    task['logged'] = 'true'
    w.task_update(task)
    w.task_annotate(task, "Logged %s hours in Harvest" % response['hours'])
    # Prompt to complete task if it is pending.
    if (task['status'] is 'pending' and query_yes_no(
            'Complete task "%s"?' % task['description'])):
        w.task_done(uuid=task['uuid'])
        print('Task %d is complete!' % task['id'])

main()
