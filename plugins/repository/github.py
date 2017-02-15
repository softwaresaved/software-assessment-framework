import logging

from github3 import GitHub

import config
import plugins.repository.helper as helper


class GitHubHelper(helper.RepositoryHelper):

    def can_process(self, url):
        if "github.com" in url:
            self.repo_url = url
            self.login()

            return True
        else:
            return False

    def login(self):
        # Log in
        logging.info('Logging in to GitHub')
        try:
            # Try
            self.gh_link = GitHub(token=config.github_api_token)
        except:
            logging.warning('Login to GitHub failed')

        # Check supplied repo url
        #  if 'http' in submitted_repo: we've got a full Github URL
        if ".git" in self.repo_url:
            # We're dealing with a clone URL
            if "git@github.com" in self.repo_url:
                # SSH clone URL
                splitted = self.repo_url.split(':')[1].split('/')
                username = splitted[-2]
                reponame = splitted[-1]
            elif "https" in self.repo_url:
                # HTTPS URL
                splitted = self.repo_url.split('/')
                username = splitted[-2]
                reponame = splitted[-1]
                self.reponame = reponame.replace('.git', '')
        else:
            splitted = self.repo_url.split('/')
            self.username = splitted[-2]
            self.reponame = splitted[-1]

        logging.info(
            'Trying to connect to repository with Username: ' + self.username + " / Repo: " + self.reponame + "...")

        try:
            self.repo = self.gh_link.repository(self.username, self.reponame)
            logging.info("...Success")

        except:
            logging.warning('Failed to connect to GitHub repository')
            return "Error - Repo doesn't exist!"

    def __init__(self, repo_url=None):
        self.repo_url = repo_url
        if self.repo_url is not None:
            self.login()

    # TODO - Change this to just fetch_file(name)

    def get_license(self):
        """Identify and return license file
            :returns
                The contents of the license file as a (something - Weakly typed ftw)
        """
        possible_filenames = ['COPYING', 'LICENSE']
        # Get all files in the root directory of the repo
        root_files = self.repo.contents('/')
        root_files_iter = root_files.items()

        for name, contents in root_files_iter:
            for poss_name in possible_filenames:
                if poss_name in name.upper():
                    logging.info("Found a candidate license file: " + name)
                    return self.repo.contents(name).decoded.decode('UTF-8')
