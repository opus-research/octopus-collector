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
        out = self.repo.results_git.path()
        return out + "/refactorings.json"

    def collect(self):
        params = {}
        params["jar"] = self.settings.ref_miner()
        params["old"] = self.old.path()
        params["new"] = self.repo.path()
        params["ref_file"] = self.ref_file() + ".ugly"
        cmd = 'java -jar %(jar)s "%(old)s" "%(new)s" > %(ref_file)s' % params
        run_cmd(cmd)

        # prettify the output file (useful for versioning - multiple lines)
        cmd = "cat %s | python -m json.tool > %s" % (params["ref_file"], self.ref_file())
        run_cmd(cmd)
        run_cmd("rm -rf %s" % params["ref_file"])
