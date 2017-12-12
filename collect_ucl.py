import sys
import os
import csv
import json
import traceback

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


def reviews_history(repository):
    reviews = []
    project = repository.name()
    with open("code-reviews/%s.csv" % project) as review_file:
        reader = csv.DictReader(review_file)
        for row in reader:
            reviews.append(row)
    return reviews


def collect(repository, twin):
    reviews = reviews_history(repository)
    finished = repository.results_git.finished_commits()
    processed = 0
    for review in reviews:
        commit = review["after_commit_id"]
        parent = review["before_commit_id"]

        processed += 1
        print "::: Processing commit %s out of %s :::" % (processed, len(reviews))
        if should_skip(repository, processed):
            print "Skipping due to selection made on the repositories file"
            continue

        #  checks if this commit was already processed
        if commit in finished:
            print "Commit %s already processed. Skipping..." % commit
            continue

        repository.checkout(commit)
        twin.checkout(parent)

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

            # save the results into results repository and push them to the remote server
            repository.results_git.create_state_file()
            review_json = json.dumps(review, indent=4, sort_keys=True)
            repository.results_git.create_meta_file("review.json", review_json)
            repository.results_git.commit(repository.current_commit)
            repository.results_git.push()
        except:
            print "Unexpected error:", sys.exc_info()[0]
            traceback.print_exc(file=sys.stdout)
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
