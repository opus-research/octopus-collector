from octopus.git import ProjectGit
import csv


class RepoFile:

    def __init__(self, file_name, start, end):
        self.file_name = file_name
        self.start = start
        self.end = end
        self.repositories = self.load()

    def load(self):
        def get_int_value(value):
            if value:
                return int(value)
            else:
                return None
        with open(self.file_name) as repos_file:
            reader = csv.DictReader(repos_file, delimiter=';', quotechar='"')
            row_count = 1
            selected = []
            for row in reader:
                if self.start <= row_count <= self.end:
                    if row["git_url"].strip()[0] == "#":
                        continue
                    starting_commit = get_int_value(row["starting_commit"])
                    ending_commit = get_int_value(row["ending_commit"])
                    project = ProjectGit(row["git_url"], row["main_branch"], row["source_folder"],
                                         starting_commit=starting_commit, ending_commit=ending_commit)
                    selected.append(project)
                row_count += 1
            return selected
