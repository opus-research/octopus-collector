import sys
import os
import argparse

from octopus.eh_facts_extractor import EHFactsExtractor
from octopus.organic import Organic
from octopus.refactoring import RefactoringMiner
from octopus.repositories import RepoFile
from octopus.understand import Understand


def prepare(repository):
    repository.clone()
    repository.checkout("master")
    repository.extract_history()
    twin = repository.twin()
    repository.cp(twin.path())
    twin.checkout("master")
    return repository, twin


def collect(repository, twin):
    commits = repository.commits()
    finished = repository.results_git.finished_commits()
    processed = 1
    for (commit, parent, message) in commits:
        print "::: Processing commit %s out of %s :::" % (processed, len(commits))
        processed += 1
        #  checks if this commit was already processed
        if commit in finished:
            print "Commit %s already processed. Skipping..." % commit
            continue
        repository.checkout(commit)
        twin.checkout(parent)  # one version before in order to collect refactorings
        print "Collecting metrics"
        Understand(repository).collect()
        print "Collecting smells and agglomerations"
        Organic(repository).collect()
        print "Collecting refactorings"
        RefactoringMiner(repository, twin).collect()
        print "Collecting EH facts"
        EHFactsExtractor(repository).collect()
        repository.results_git.create_state_file()
        repository.results_git.commit(repository.current_commit)


def start():
    repositories_file = os.path.abspath(sys.argv[1])
    starting_line = int(sys.argv[2])
    ending_line = int(sys.argv[3])

    repo_file = RepoFile(repositories_file, starting_line, ending_line)
    for repository in repo_file.repositories:
        repository, twin = prepare(repository)
        collect(repository, twin)
        
start()
