import sys
import os

from octopus.eh_facts_extractor import EHFactsExtractor
from octopus.organic import Organic
from octopus.refactoring import RefactoringMiner
from octopus.repositories import RepoFile
from octopus.understand import Understand


def prepare(repository):
    repository.clone()
    repository.checkout(repository.main_branch)
    repository.extract_history()
    twin = repository.twin()
    repository.cp(twin.path())
    twin.checkout(twin.main_branch)
    return repository, twin


def should_skip(repository, processed):
    if not repository.has_commit_selection():
        return False
    if processed < repository.starting_commit or processed > repository.ending_commit:
        return True
    return False


def log_error(message):
    with open("errors.log", "a") as log_file:
        log_file.write(message + "\n")


def collect(repository, twin):
    commits = repository.commits()
    finished = repository.results_git.finished_commits()
    processed = 0
    for (commit, parent, message) in commits:
        processed += 1
        print "::: Processing commit %s out of %s :::" % (processed, len(commits))
        if should_skip(repository, processed):
            print "Skipping due to selection made on the repositories file"
            continue

        #  checks if this commit was already processed
        if commit in finished:
            print "Commit %s already processed. Skipping..." % commit
            continue

        repository.checkout(commit)
        twin.checkout(parent)  # one version before in order to collect refactorings

        if not repository.exists_src_folder():
            print "Source folder %s not found. Skipping" % repository.src_folder()
            continue

        try:
            print "Collecting metrics"
            Understand(repository).collect()
            print "Collecting smells and agglomerations"
            Organic(repository).collect()
            print "Collecting refactorings"
            RefactoringMiner(repository, twin).collect()
            print "Collecting EH facts"
            EHFactsExtractor(repository).collect()

            # save the results into results repository and push them to the remote server
            repository.results_git.create_state_file()
            repository.results_git.commit(repository.current_commit)
            repository.results_git.push()
        except:
            print "Unexpected error:", sys.exc_info()[0]
            log_error(commit + ";" + repository.url)


def start():
    repositories_file = os.path.abspath(sys.argv[1])
    starting_line = None
    ending_line = None
    if len(sys.argv) >= 4:
        starting_line = int(sys.argv[2])
        ending_line = int(sys.argv[3])

    repo_file = RepoFile(repositories_file, starting_line, ending_line)
    for repository in repo_file.repositories:
        repository, twin = prepare(repository)
        collect(repository, twin)

start()
