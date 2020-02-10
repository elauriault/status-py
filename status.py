#!/usr/bin/python3

import requests
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--gitlab', '-g', help='gitlab url')
parser.add_argument('--token', '-t', help='private token')
parser.add_argument('groups',nargs='*')
args = parser.parse_args()


def get_group_id_by_name(name):
    page = 0
    while(True):
        page+=1
        r = get_from_gitlab('/api/v4/groups?page=' + str(page) + '&per_page=50&all=False')
        if r == "":
            return -1
        # print(json.dumps(r))
        for resp in r:
            if resp['name'] == name:
                return resp['id']

def get_projects_by_group(id):
    projects = get_all_from_gitlab('/api/v4/groups/' + str(id) + '/projects/')
    r = []
    for project in projects[0]:
        r.append({'id' : project['id'], 'name' : project['name']})
    return r

def get_pipelines(projects):
    r = []
    for project in projects:
        pipeline = get_from_gitlab('/api/v4/projects/' + str(project['id']) + '/pipelines/' + '?page=1&per_page=1&all=False')
        project.update({'status' : pipeline[0]['status']})
        r.append(project)
    return r       

def get_all_from_gitlab(path):
    page = 0
    results = []
    while(True):
        page+=1
        r = get_from_gitlab(path + '?page=' + str(page) + '&per_page=50&all=False')
        if r == []:
            return results
        results.append(r)

def get_from_gitlab(path):
    auth = {'Private-Token' : args.token}
    r = requests.get(args.gitlab + path, headers = auth)
    # print(json.dumps(r.json()))
    return r.json()

def get_pipelines_status_by_group(project_groups):

    r = []
    for projects_group in projects_groups:
        id = projects_group['id']
        projects = get_projects_by_group(id)
        projects = get_pipelines(projects)
        r.append({'name' : projects_group['name'], 'id': projects_group['id'], 'projects': projects})
    return r


projects_groups=[]
for group in args.groups:
    id = get_group_id_by_name(group)
    projects_groups.append({'name' : group, 'id' : id})

print(json.dumps(get_pipelines_status_by_group(projects_groups)))

