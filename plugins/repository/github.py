import logging

from github3 import GitHub

import config
from plugins.repository.helper import *


class GitHubHelper(RepositoryHelper):

    def __init__(self, repo_url=None):
        self.repo_url = repo_url
        self.user_name = None
        self.repo_name = None
        self.github = None # GitHub Object from github3.py
        self.repo = None
        self.api_token = config.github_api_token

    def can_process(self, url):
        if "github.com" in url:
            self.repo_url = url
            return True
        else:
            return False

    def login(self):
        # Log in
        logging.info('Logging in to GitHub')
        try:
            # Try connecting with the supplied API token
            # ToDo: Check what actual happens when wrong credentials supplied - I suspect nothing
            self.github = GitHub(token=self.api_token)
        except:
            logging.warning('Login to GitHub failed')

        # Check supplied repo url
        #  if 'http' in submitted_repo: we've got a full Github URL
        if ".git" in self.repo_url:
            # We're dealing with a clone URL
            if "git@github.com" in self.repo_url:
                # SSH clone URL
                splitted = self.repo_url.split(':')[1].split('/')
                self.user_name = splitted[-2]
                self.repo_name = splitted[-1]
            elif "https" in self.repo_url:
                # HTTPS URL
                splitted = self.repo_url.split('/')
                self.user_name = splitted[-2]
                self.repo_name = splitted[-1]
                self.repo_name = self.repo_name.replace('.git', '')
        else:
            if self.repo_url.endswith("/"):
                self.repo_url = self.repo_url[:-1]  # Remove trailing slash
            splitted = self.repo_url.split('/')
            self.user_name = splitted[-2]
            self.repo_name = splitted[-1]

        logging.info(
            'Trying to connect to repository with Username: ' + self.user_name + " / Repo: " + self.repo_name + "...")

        self.repo = self.github.repository(self.user_name, self.repo_name)
        if self.repo:
            logging.info("...Success")
        else:
            logging.warning("Unable to connect to selected GitHub repository - check the URL and permissions")
            raise RepositoryHelperRepoError("Unable to connect to selected GitHub repository - check the URL and permissions. Supply an API token if the repository is private.")

    def get_files_from_root(self, candidate_filenames):
        """
        Given a list of candidate file names, examine the repository root, returning the file names and contents
        :param candidate_filenames: A list of the files of interest e.g. ['COPYING','LICENSE']
        :return: A Dictionary of the form {'filename':file_contents,...}
        """
        found_files = {}
        # Get all files in the root directory of the repo
        root_files = self.repo.contents('/')
        root_files_iter = root_files.items()
        for name, contents in root_files_iter:
            for poss_name in candidate_filenames:
                if poss_name in name.upper():
                    logging.info("Found a candidate file: " + name)
                    found_files[name] = self.repo.contents(name).decoded.decode('UTF-8')

        return found_files

    def get_commits(self, sha=None, path=None, author=None, number=-1, etag=None, since=None, until=None):
        """
        Return a list of all commits in a repository
        :params:
        Parameters:
        sha (str) – (optional), sha or branch to start listing commits from
        path (str) – (optional), commits containing this path will be listed
        author (str) – (optional), GitHub login, real name, or email to filter commits by (using commit author)
        number (int) – (optional), number of commits to return. Default: -1 returns all commits
        etag (str) – (optional), ETag from a previous request to the same endpoint
        since (datetime or string) – (optional), Only commits after this date will be returned. This can be a datetime or an ISO8601 formatted date string.
        until (datetime or string) – (optional), Only commits before this date will be returned. This can be a datetime or an ISO8601 formatted date string.
        :return: a list of Commit
        """

        # TODO: Should investigate proper use of GitHubIterator to help ratelimiting: https://github3py.readthedocs.io/en/master/examples/iterators.html

        list_commits = []

        for c in self.repo.iter_commits(sha, path, author, number, etag, since, until):
            list_commits.append(c)

        logging.info('Retrieved ' + str(len(list_commits)) + ' commits from repository with Username: ' + self.user_name + " / Repo: " + self.repo_name + "...")

        return list_commits
