import os

from octopus.bash import run_cmd
from octopus.settings import Settings


class EHFactsExtractor:
    def __init__(self, repository):
        self.repository = repository
        self.settings = Settings()

    def facts_file(self):
        out = self.repository.results_git.path()
        return out + "/ehf_facts"

    def collect(self):
        equinox = self.settings.equinox()
        ehfe = "EHFactsExtractor.EHFactsExtractor"
        main = "org.eclipse.core.launcher.Main"
        cmd = 'java -jar -Xms1g -Xmx6g "%s" %s -application %s "%s" "%s"'
        cmd = cmd % (equinox, main, ehfe, self.repository.src_folder(), self.facts_file())
        run_cmd(cmd)
