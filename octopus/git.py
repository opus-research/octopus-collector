
import os
from octopus.settings import Settings
from bash import run_cmd
from abc import ABCMeta
from abc import abstractmethod


class Git(object):
    __metaclass__ = ABCMeta

    def __init__(self, main_branch):
        self.current_commit = "HEAD"
        self.main_branch = main_branch

    @abstractmethod
    def path(self): pass

    @abstractmethod
    def history_file(self): pass

    def stash(self):
        cmd = "git -C %s stash --quiet" % self.path()
        run_cmd(cmd)

    def reset(self):
        cmd = "git -C %s reset HEAD --hard --quiet" % self.path()
        run_cmd(cmd)

    def checkout(self, commit):
        self.stash()
        self.reset()
        cmd = "git -C %s checkout -f %s --quiet" % (self.path(), commit)
        run_cmd(cmd)
        self.current_commit = commit

    def extract_history(self):
        cmd = "git -C %s rev-list --format=\"%%H;%%P;%%ae;%%an;%%ai;%%s\" --no-merges --branches=%s HEAD "
        cmd += "| grep -v \"commit \" > %s"
        cmd = cmd % (self.path(), self.main_branch, self.history_file())
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
        Git.__init__(self, "master")
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

    def remote_folder(self):
        """
        returns the remote folder's name. Ex: results_apache_derby/ufal5_results_repo
        :return:
        """
        template = "results_%s/%s_results_repo"
        project_name = self.project_git.name()
        machine = self.settings.git_remote()["local_name"]
        return template % (project_name, machine)

    def setup_remote(self):
        out = self.path()
        remote = self.settings.git_remote()

        # creates the remote repository
        create_cmd = remote["create_remote_cmd"] % self.remote_folder()
        run_cmd(create_cmd)

        add_remote = remote["add_remote_cmd"] % (out, self.remote_folder())
        run_cmd(add_remote)

    def push(self):
        out = self.path()
        cmd = "git -C %s push origin master" % out
        run_cmd(cmd)

    def create(self):
        out = self.path()
        if not os.path.isdir(out):
            run_cmd("mkdir -p %s" % out)
        cmd = "git -C %s init" % out
        run_cmd(cmd)
        run_cmd('echo results of %s > %s/README.txt' % (self.project_git.name(), self.path()))
        self.commit("initial commit")
        self.setup_remote()

    def create_state_file(self):
        run_cmd('echo commit: %s > %s/state.txt' % (self.project_git.current_commit, self.path()))

    def create_meta_file(self, filename, content):
        out = "%s/%s" % (self.path(), filename)
        with open(out, "w") as f:
            f.write(content)

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

    def __init__(self, url, main_branch="master", source_folder="", name_suffix="",
                 starting_commit=None, ending_commit=None):
        """
        :param url: git repository url. Used to clone the repository
        :param main_branch: main branch where the commits will be collected (usually, main)
        :param source_folder: instead of using all java files, you can inform a root of source folder.
        In this way, you can ignore all test files
        :param name_sufix:
        """
        Git.__init__(self, main_branch)
        self.url = url
        self.name_suffix = name_suffix
        self.source_folder = source_folder
        self.settings = Settings()
        self.create_output_folder()
        self.results_git = ResultsGit(self)
        self.starting_commit = starting_commit
        self.ending_commit = ending_commit

    def has_commit_selection(self):
        return self.starting_commit is not None and self.ending_commit is not None

    def twin(self):
        return ProjectGit(self.url, self.main_branch, self.source_folder, "_twin")

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

    def clone(self):
        if os.path.exists(self.path()):
            print self.url, "already cloned"
            return
        params = {"url": self.url, "dest_folder": self.path()}
        cmd = "git clone %(url)s %(dest_folder)s" % params
        run_cmd(cmd)

    def path(self):
        """
        Folder where all the repository files are stored
        :return:
        """
        return self.settings.repositories_folder() + "/" + self.name() + self.name_suffix

    def src_folder(self):
        return self.path() + "/" + self.source_folder

    def exists_src_folder(self):
        return os.path.exists(self.src_folder())

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
