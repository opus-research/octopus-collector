import os

from octopus.bash import run_cmd
from octopus.settings import Settings


class EHFactsExtractor:
    def __init__(self, repository):
        self.repository = repository
        self.settings = Settings()

    def facts_file(self):
        return self.repository.out_folder() + "/%s_ehf_facts" % self.repository.current_commit

    def collect(self):
        if os.path.exists(self.facts_file()):
            print "Facts collected for", self.repository.current_commit
            return
        equinox = self.settings.equinox()
        ehfe = "EHFactsExtractor.EHFactsExtractor"
        main = "org.eclipse.core.launcher.Main"
        cmd = 'java -jar -Xms1g -Xmx6g "%s" %s -application %s "%s" "%s"'
        cmd = cmd % (equinox, main, ehfe, self.repository.contents_folder(), self.facts_file())
        run_cmd(cmd)
