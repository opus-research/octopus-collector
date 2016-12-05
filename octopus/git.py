
import os
from octopus.settings import Settings
from bash import run_cmd
from abc import ABCMeta
from abc import abstractmethod


class Git(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.current_commit = "HEAD"

    @abstractmethod
    def path(self): pass

    @abstractmethod
    def history_file(self): pass

    def clone(self):
        if os.path.exists(self.path()):
            print self.url, "already cloned"
            return
        params = {"url": self.url, "dest_folder": self.path()}
        cmd = "git clone %(url)s %(dest_folder)s" % params
        run_cmd(cmd)

    def stash(self):
        cmd = "git -C %s stash --quiet" % self.path()
        run_cmd(cmd)

    def reset(self):
        cmd = "git -C %s reset HEAD --hard --quiet" % self.path()
        run_cmd(cmd)

    def checkout(self, commit):
        self.stash()
        self.reset()
        cmd = "git -C %s checkout %s --quiet" % (self.path(), commit)
        run_cmd(cmd)
        self.current_commit = commit

    def extract_history(self):
        cmd = "git -C %s rev-list --format=\"%%H;%%P;%%ae;%%an;%%ai;%%s\" --no-merges --branches=master HEAD "
        cmd += "| grep -v \"commit \" > %s"
        cmd = cmd % (self.path(), self.history_file())
        run_cmd(cmd)

    def is_git(self):
        return os.path.isdir(self.path() + "/.git")

    def commits(self):
        """
        Lists commit objects in reverse chronological order
        :return:
        """
        with open(self.history_file()) as history_file:
            commits_list = []
            rows = history_file.readlines()
            for row in rows:
                row = row.split(";")
                commit = row[0]
                parent = row[1]
                message = row[-1]
                commits_list.append((commit, parent, message))
            return commits_list


class ResultsGit(Git):

    def __init__(self, project_git):
        self.project_git = project_git
        self.settings = Settings()
        if self.is_git():
            self.extract_history()
        else:
            self.create()

    def path(self):
        """
        Path to the repository where the results must be saved
        :return: path
        """
        return self.project_git.out_folder() + "/" + self.settings.results_repo_name()

    def finished_commits(self):
        """
        Returns the list of commits from ProjectGit that were already processed, i.e.,
        where all collectors finished their job successfully
        :return:
        """
        finished = set()
        for commit in self.commits():
            finished.add(commit[-1].strip())
        return finished

    def create(self):
        out = self.path()
        if not os.path.isdir(out):
            run_cmd("mkdir -p %s" % out)
        cmd = "git -C %s init" % out
        run_cmd(cmd)
        run_cmd('echo results of %s > %s/README.txt' % (self.project_git.name(), self.path()))
        self.commit("initial commit")

    def create_state_file(self):
        run_cmd('echo commit: %s > %s/state.txt' % (self.project_git.current_commit, self.path()))

    def commit(self, message):
        params = {"dir": self.path(), "message": message}
        cmd = "git -C %(dir)s add --all" % params
        run_cmd(cmd)

        cmd = "git -C %(dir)s commit -m \"%(message)s\"" % params
        run_cmd(cmd)

    def history_file(self):
        """
        Returns the name of the history file. This file contains the list of
        all commits and their parents in reverse chronological order
        :return:
        """
        return self.project_git.out_folder() + "/processed_commits.txt"

class ProjectGit(Git):

    def __init__(self, url, name_sufix=""):
        self.url = url
        self.name_suffix = name_sufix
        self.settings = Settings()
        self.create_output_folder()
        self.results_git = ResultsGit(self)

    def twin(self):
        return ProjectGit(self.url, "_twin")

    def create_output_folder(self):
        out = self.out_folder()
        if not os.path.isdir(out):
            run_cmd("mkdir -p %s" % out)

    def name(self):
        parts = self.url.split("/")
        return parts[-2] + "_" + parts[-1]

    def cp(self, destination):
        if os.path.exists(destination):
            print "Destination already exists", destination
            return
        """
        Copies the cloned repository to another folder
        :return:
        """
        cmd = "cp -r %s %s" % (self.path(), destination)
        run_cmd(cmd)

    def path(self):
        """
        Folder where all the repository files are stored
        :return:
        """
        return self.settings.repositories_folder() + "/" + self.name() + self.name_suffix

    def out_folder(self):
        """
        Folder where all results related to this repo are saved (smells, agglomerations,
        refactorings...)
        :return:
        """
        return self.settings.output_folder() + "/" + self.name()

    def history_file(self):
        """
        Returns the name of the history file. This file contains the list of
        all commits and their parents in reverse chronological order
        :return:
        """
        return self.out_folder() + "/commits_history.txt"
