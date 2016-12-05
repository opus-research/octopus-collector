import os

from octopus.bash import run_cmd
from octopus.settings import Settings


class Organic:
    def __init__(self, repository):
        self.repository = repository
        self.settings = Settings()

    def smell_file(self):
        out = self.repository.results_git.path()
        return out + "/smells.json"

    def agglomeration_file(self):
        out = self.repository.results_git.path()
        return out + "/agglomerations.json"

    def collect(self):
        equinox = self.settings.equinox()
        organic = "organic.Organic"
        main = "org.eclipse.core.launcher.Main"
        cmd = 'java -jar -Xms1g -Xmx20g "%s" %s -application %s -sf "%s" -af "%s" -src "%s"'
        cmd = cmd % (equinox, main, organic, self.smell_file(), self.agglomeration_file(), self.repository.path())
        run_cmd(cmd)
