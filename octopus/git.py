
import os
from octopus.settings import Settings
from bash import run_cmd

class GitRepository:

    def __init__(self, url, name_sufix = ""):
        self.url = url
        self.name_suffix = name_sufix
        self.settings = Settings()
        self.current_commit = "HEAD"
        self.create_output_folder()

    def twin(self):
        return GitRepository(self.url,"_twin")

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
        cmd = "cp -r %s %s" % (self.contents_folder(), destination)
        run_cmd(cmd)

    def contents_folder(self):
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

    def clone(self):
        if os.path.exists(self.contents_folder()):
            print self.url, "already cloned"
            return
        params = {"url": self.url, "dest_folder": self.contents_folder()}
        cmd = "git clone %(url)s %(dest_folder)s" % params
        run_cmd(cmd)

    def stash(self):
        cmd = "git -C %s stash --quiet" % self.contents_folder()
        run_cmd(cmd)

    def reset(self):
        cmd = "git -C %s reset HEAD --hard --quiet" % self.contents_folder()
        run_cmd(cmd)

    def checkout(self, commit):
        self.stash()
        self.reset()
        cmd = "git -C %s checkout %s --quiet" % (self.contents_folder(), commit)
        run_cmd(cmd)
        self.current_commit = commit

    def extract_history(self):
        cmd = "git -C %s rev-list --format=\"%%H;%%P;%%ae;%%an;%%ai;%%s\" --no-merges --branches=master HEAD "
        cmd += "| grep -v \"commit \" > %s"
        cmd = cmd % (self.contents_folder(), self.history_file())
        run_cmd(cmd)

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
                commits_list.append((commit, parent))
            return commits_list
