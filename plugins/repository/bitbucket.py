import logging

from github3 import GitHub

import config
from plugins.repository.helper import *


class BitBucketHelper(RepositoryHelper):

    def __init__(self, repo_url=None):
        self.repo_url = repo_url

    def can_process(self, url):
        if "bitbucket.com" in url:
            self.repo_url = url
            return True
        else:
            return False

    def login(self):
        """
        Login using the appropriate credentials
        :return:
        """
        raise NotImplementedError("This method must be overridden")

    def get_files_from_root(self, candidate_filenames):
        """
        Given a list of candidate file names, examine the repository root, returning the file names and contents
        :param candidate_filenames: A list of the files of interest e.g. ['COPYING','LICENSE']
        :return: A Dictionary of the form {'filename':file_contents,...}
        """
        raise NotImplementedError("This method must be overridden")