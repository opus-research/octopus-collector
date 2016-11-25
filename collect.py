import sys
import os

from octopus.organic import Organic
from octopus.refactoring import RefactoringMiner
from octopus.repositories import RepoFile
from octopus.understand import Understand


def prepare(repository):
    repository.clone()
    repository.checkout("master")
    repository.extract_history()
    twin = repository.twin()
    twin.checkout("master")
    repository.cp(twin.contents_folder())
    return repository, twin


def collect(repository, twin):
    commits = repository.commits()
    processed = 1
    for (commit, parent) in commits:
        print "Processing commit %s out of %s" % (processed, len(commits))
        repository.checkout(commit)
        twin.checkout(parent)  # one version before in order to collect refactorings
        #print "Collecting metrics"
        #Understand(repository).collect()
        #print "Collecting smells and agglomerations"
        #Organic(repository).collect()
        print "Collecting refactorings"
        RefactoringMiner(repository, twin).collect()
        # return
        processed += 1


def start():
    repositories_file = os.path.abspath(sys.argv[1])
    starting_line = int(sys.argv[2])
    ending_line = int(sys.argv[3])

    repo_file = RepoFile(repositories_file, starting_line, ending_line)
    for repository in repo_file.repositories:
        repository, twin = prepare(repository)
        collect(repository, twin)


start()