import os

from octopus.bash import run_cmd
from octopus.settings import Settings


class RefactoringMiner:

    def __init__(self,repository, old_repository):
        """
        :param repository: Repository in the current version to analyze
        :param old_repository: Repository in the previous version
        :return:
        """
        self.repo = repository
        self.old = old_repository
        self.settings = Settings()

    def ref_file(self):
        params = (self.old.current_commit, self.repo.current_commit)
        return self.repo.out_folder() + "/%s_to_%s_refactorings.json" % params

    def collect(self):
        if os.path.exists(self.ref_file()):
            params = (self.repo.current_commit, self.old.current_commit)
            print "Refactorings already collected for %s to %s" % params
            return
        params = {}
        params["jar"] = self.settings.ref_miner()
        params["old"] = self.old.contents_folder()
        params["new"] = self.repo.contents_folder()
        params["ref_file"] = self.ref_file()
        cmd = 'java -jar %(jar)s "%(old)s" "%(new)s" > %(ref_file)s' % params
        run_cmd(cmd)
