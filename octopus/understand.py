from octopus.bash import run_cmd


class Understand:
    def __init__(self, repository):
        self.repository = repository

    def settings(self):
        cmd = "und settings -MetricOutputFile \"%s\" %s" % (self.metrics_file(), self.udb_file())
        run_cmd(cmd)
        cmd = "und settings -MetricMetrics all  %s" % self.udb_file()
        run_cmd(cmd)
        cmd = "und settings -MetricFileNameDisplayMode RelativePath %s" % self.udb_file()
        run_cmd(cmd)
        cmd = "und settings -MetricDeclaredInFileDisplayMode RelativePath %s" % self.udb_file()
        run_cmd(cmd)
        cmd = "und settings -MetricShowDeclaredInFile on %s" % self.udb_file()
        run_cmd(cmd)
        cmd = "und settings -MetricShowFunctionParameterTypes on %s" % self.udb_file()
        run_cmd(cmd)

    def udb_file(self):
        out = self.repository.results_git.path()
        return out + "/project.udb"

    def metrics_file(self):
        out = self.repository.results_git.path()
        return out + "/metrics.csv"

    def create_udb(self):
        cmd = "und create -db %s -languages java" % self.udb_file()
        run_cmd(cmd)

    def add_files(self):
        files = self.repository.out_folder() + "/files"
        cmd = "find %s -name \"*.java\"  > %s" % (self.repository.src_folder(), files)
        run_cmd(cmd)
        cmd = "und -quiet -db %s add @%s" % (self.udb_file(), files)
        run_cmd(cmd)

    def analyze(self):
        cmd = "und -quiet analyze %s" % self.udb_file()
        run_cmd(cmd)

    def collect(self):
        print "Collecting", self.metrics_file()
        self.create_udb()
        self.add_files()
        self.analyze()
        self.settings()
        cmd = "und metrics -db %s" % self.udb_file()
        run_cmd(cmd)
        cmd = "rm -f %s" % self.udb_file()
        run_cmd(cmd)
