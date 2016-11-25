from octopus.git import GitRepository


class RepoFile:

    def __init__(self, file_name, start, end):
        self.file_name = file_name
        self.start = start - 1
        self.end = end - 1
        self.repositories = self.load()

    def load(self):
        with open(self.file_name) as repos_file:
            rows = repos_file.readlines()
            selected = [rows[i].strip() for i in range(self.start, self.end + 1)]
            return [GitRepository(i) for i in selected]