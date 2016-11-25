import os

from octopus.bash import run_cmd
from octopus.settings import Settings


class Organic:
    def __init__(self, repository):
        self.repository = repository
        self.settings = Settings()

    def smell_file(self):
        return self.repository.out_folder() + "/%s_smells.json" % self.repository.current_commit

    def agglomeration_file(self):
        return self.repository.out_folder() + "/%s_agglomerations.json" % self.repository.current_commit

    def collect(self):
        if os.path.exists(self.smell_file()) and os.path.exists(self.agglomeration_file()):
            print "Smells and agglomerations already collected for", self.repository.current_commit
            return
        equinox = self.settings.equinox()
        organic = "organic.Organic"
        main = "org.eclipse.core.launcher.Main"
        cmd = 'java -jar -Xms1g -Xmx20g "%s" %s -application %s -sf "%s" -af "%s" -src "%s"'
        cmd = cmd % (equinox, main, organic, self.smell_file(), self.agglomeration_file(), self.repository.contents_folder())
        run_cmd(cmd)
