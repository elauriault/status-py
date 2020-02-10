#!/usr/bin/python3

import requests
import json
import argparse

class Gitlab:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def __get(self,path):
        auth = {'Private-Token' : self.token}
        r = requests.get(self.url + path, headers = auth)
        # print(json.dumps(r.json()))
        return r.json()

    def __get_all(self,path):
        page = 0
        results = []
        while(True):
            page+=1
            r = self.__get(path + '?page=' + str(page) + '&per_page=50&all=False')
            if r == []:
                return results
            results.append(r)

    def __get_projects_by_group(self,id):
        projects = self.__get_all('/api/v4/groups/' + str(id) + '/projects/')
        r = []
        for project in projects[0]:
            r.append({'id' : project['id'], 'name' : project['name']})
        return r

    def __get_pipelines(self,projects):
        r = []
        for project in projects:
            pipeline = self.__get('/api/v4/projects/' + str(project['id']) + '/pipelines/' + '?page=1&per_page=1&all=False')
            project.update({'status' : pipeline[0]['status']})
            r.append(project)
        return r

    def get_group_id_by_name(self,name):
        page = 0
        while(True):
            page+=1
            r = self.__get('/api/v4/groups?page=' + str(page) + '&per_page=50&all=False')
            if r == "":
                return -1
            # print(json.dumps(r))
            for resp in r:
                if resp['name'] == name:
                    return resp['id']

    def get_pipelines_status_by_group(self,project_groups):
        r = []
        for projects_group in projects_groups:
            id = projects_group['id']
            projects = self.__get_projects_by_group(id)
            projects = self.__get_pipelines(projects)
            r.append({'name' : projects_group['name'], 'id': projects_group['id'], 'projects': projects})
        return r

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--gitlab', '-g', help='gitlab url')
    parser.add_argument('--token', '-t', help='private token')
    parser.add_argument('groups',nargs='*')
    args = parser.parse_args()

    g = Gitlab(args.gitlab, args.token)

    projects_groups=[]
    for group in args.groups:
        id = g.get_group_id_by_name(group)
        projects_groups.append({'name' : group, 'id' : id})

    print(json.dumps(g.get_pipelines_status_by_group(projects_groups)))
