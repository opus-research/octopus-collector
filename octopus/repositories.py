from octopus.git import ProjectGit
import csv


class RepoFile:

    def __init__(self, file_name, start, end):
        self.file_name = file_name
        self.start = start
        self.end = end
        self.repositories = self.load()

    def load(self):
        with open(self.file_name) as repos_file:
            reader = csv.DictReader(repos_file, delimiter=';', quotechar='"')
            row_count = 1
            selected = []
            for row in reader:
                if self.start <= row_count <= self.end:
                    project = ProjectGit(row["git_url"], row["main_branch"], row["source_folder"])
                    selected.append(project)
                row_count += 1
            return selected
