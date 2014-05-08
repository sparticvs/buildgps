#!/usr/bin/env python
"""
" File: buildgps_ws.py
" Desc: BuildGPS WebSocket Proxy
" Author(s): Charles `sparticvs' Timko <sparticvs@popebp.com>
"""
from tornado.gen import coroutine
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.httpclient import (HTTPClient,
                                HTTPError)
from tornado.websocket import (WebSocketHandler,
                               WebSocketClosedError,
                               websocket_connect)

from gitlab import Gitlab
from jenkinsapi.jenkins import Jenkins

import json
import threading
from urlparse import urljoin
from ConfigParser import ConfigParser
from abc import abstractmethod

## Register all Sockets that open into a list...
## then when data is received, push to all sockets
## Need polling thread to get updates

SOCKETS_LOCK = threading.Lock()
SOCKETS = []

WEBSOCK_DO_PUSH_EVENT = threading.Event()
BUILD_SYS_DO_POLL_EVENT = threading.Event()
SCM_DO_POLL_EVENT = threading.Event()

class StrictDict(dict):
    legal_keys = []

    def __getitem__(self, key):
        if key not in self.legal_keys:
            raise SyntaxError("Key (%s) is illegal" % key)
        elif key not in self.keys():
            return None
        else:
            return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if key not in self.legal_keys:
            raise SyntaxError("Key (%s) is illegal" % key)
        else:
            return dict.__setitem__(self, key, value)


class BuildItem(StrictDict):
    legal_keys = ["status",
                  "timestamp",
                  "label",
                  "cause"]


class RepoItem(StrictDict):
    legal_keys = ["branch",
                  "commit",
                  "blame",
                  "timestamp"]


class ProjectList(object):
    def __init__(self):
        self.proj_lock = threading.Lock()
        self.projects = []

    def __get_project(self, name):
        ndx = 0
        for proj in self.projects:
            if proj["name"] == name:
                return ndx
            ndx += 1
        return None

    def get_projects(self):
        return self.projects

    def add(self, name, build, repo):
        new = {}
        new["name"] = name
        new["build"] = build
        new["repo"] = repo
        if self.__get_project(name) is None:
            with self.proj_lock:
                self.projects.append(new)
        else:
            raise IndexError("Project Name Already Exists")

    def update(self, name, build, repo):
        ndx = self.__get_project(name)
        if ndx is None:
            raise IndexError("Project Name Doesn't Exist")
        else:
            with self.proj_lock:
                if build is not None:
                    self.projects[ndx]["build"] = build
                if repo is not None:
                    self.projects[ndx]["repo"] = repo

    def remove(self, name):
        ndx = self.__get_project(name)
        if ndx is None:
            raise IndexError("Project Name Doesn't Exist")
        else:
            with self.proj_lock:
                del self.projects[ndx]


class RepoServerRequestor(object):
    """Makes Repository Server Requests"""
    def __init__(self, uri, branch, **kwargs):
        self.uri = uri
        self.branch = branch
        self.options = kwargs
        self.initialize()

    def __str__(self):
        return self.uri

    def __repr__(self):
        return ''

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def do_poll(self):
        pass


class BuildSystemRequestor(object):
    """Makes Build System Requests"""
    def __init__(self, uri, **kwargs):
        self.uri = uri
        self.options = kwargs
        self.initialize()

    def __str__(self):
        return self.uri

    def __repr__(self):
        return ''

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def do_poll(self):
        pass


class GitLabRequestor(RepoServerRequestor):
    def initialize(self):
        pass

    def do_poll(self):
        pass


@coroutine
def jenkins_ws_callback(future):
    """Callback that handles WebSocket Messages from Jenkins"""
    conn = future.result()
    try:
        while True:
            msg = yield conn.read_message()
            if msg is None:
                break
            # Process Message that was received
            obj = json.loads(msg)
            print obj
    except WebSocketClosedError:
        pass
    finally:
        conn.close()


PROJECTS = ProjectList()


class JenkinsRequestor(BuildSystemRequestor):
    def initialize(self):
        """Initialize Jenkins Connections and Prepopulate Info"""
        if "username" in self.options.keys() and \
            "password" in self.options.keys():
            self.jenk_client = Jenkins(self.uri,
                                       username=self.options.pop("username"),
                                       password=self.options.pop("password"))
        else:
            self.jenk_client = Jenkins(self.uri)

        if "websocket" in self.options.keys():
            websocket_uri = self.options.pop("websocket")
            websocket_connect(websocket_uri, callback=jenkins_ws_callback)

    def do_poll(self):
        """Poll Jenkins Server to get Project Information"""
        while True:
        #while BUILD_SYS_DO_POLL_EVENT.wait():
            #BUILD_SYS_DO_POLL_EVENT.clear()

            # Get a list of ALL Jobs on Jenkins
            for job_name in self.jenk_client.keys():
                jobDetail = self.jenk_client[job_name]
                lastBuild = jobDetail.get_last_build()
                buildInfo = BuildItem()
                if lastBuild.is_running():
                    buildInfo["status"] = "STARTED"
                else:
                    buildInfo["status"] = lastBuild.get_status()
                buildInfo["timestamp"] = lastBuild.get_timestamp().isoformat()
                buildInfo["label"] = lastBuild.name
                buildInfo["cause"] = "" # Need a clean way to retrieve this value


                # TODO: swap GitLab specific library for Git Library
                gl_client = Gitlab(self.options["gitlab"], self.options["gitlab_key"])
                gl_client.auth()

                ### complete hack....
                try:
                    proj_url = jobDetail.get_scm_url()[0]
                except Exception:
                    continue

                sep = proj_url.rfind("/")
                start = proj_url.rfind("/", 0, sep-1)
                proj_name = proj_url[start+1:]
                project = None

                for proj in gl_client.Project():
                    if proj.path_with_namespace == proj_name:
                        project = proj

                if project is None:
                    continue # TODO raise error
                
                ### TODO remove the above ... soon

                commit = project.Commit(lastBuild.get_revision())

                repoInfo = RepoItem()
                repoInfo["branch"] = jobDetail.get_scm_branch()[0]
                repoInfo["commit"] = commit.id
                repoInfo["blame"] = commit.author_name
                repoInfo["timestamp"] = commit.created_at

                ### TODO Refactor to "JobsList" from ProjectsList
                try:
                    ## We use this order, since it will be in an infinite
                    ## loop, the likely scenario is that we will just be
                    ## updating the status of jobs
                    PROJECTS.update(job_name, buildInfo, repoInfo)
                except IndexError:
                    PROJECTS.add(job_name, buildInfo, repoInfo)

            WEBSOCK_DO_PUSH_EVENT.set()

def websock_do_push():
    """Thread to Push Data to bound sockets

        This is triggered by WEBSOCK_DO_PUSH_EVENT
    """
    while WEBSOCK_DO_PUSH_EVENT.wait():
        # Clean the event up, we are going to handle this
        WEBSOCK_DO_PUSH_EVENT.clear()
        data = { "jobs" : PROJECTS.get_projects() }
        je_data = json.dumps(data)
        for sock in SOCKETS:
            sock.write_message(je_data)


class MainHandler(WebSocketHandler):
    """Primary WebSocket Request Handler"""

    def open(self):
        with SOCKETS_LOCK:
            SOCKETS.append(self)

    def on_message(self, message):
        self.write_message("Server Ignores Data from Client")

    def on_close(self):
        with SOCKETS_LOCK:
            SOCKETS.remove(self)

APP = Application([
    (r"/buildgps", MainHandler),
])

if __name__ == "__main__":
    conf = ConfigParser()
    conf.read("../etc/buildgps.cfg")

    build = conf.get("buildgps", "build")
    build_list = build.split(',')
    
    ws_thread = threading.Thread(target=websock_do_push)
    ws_thread.daemon = True
    ws_thread.start()
    for ci_sys in build_list:
        sec = conf._sections["build_%s" % ci_sys]
        sec.pop("__name__")
        handler = eval(sec.pop("handler"))
        uri = sec.pop("uri")
        inst = handler(uri, **sec)
        thread = threading.Thread(target=inst.do_poll)
        thread.daemon = True
        thread.start()
        #BUILD_SYS_DO_POLL_EVENT.set()
        #inst.do_poll()

    APP.listen(8888)
    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
    finally:
        print "Cleaning Up Sockets"
        with SOCKETS_LOCK:
            for socket in SOCKETS:
                socket.close()
