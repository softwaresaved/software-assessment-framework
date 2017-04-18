import logging

from pybitbucket.bitbucket import Client
from pybitbucket.auth import(
     Authenticator,
     Anonymous, BasicAuthenticator,
     OAuth1Authenticator,
     OAuth2Grant, OAuth2Authenticator)
from pybitbucket.snippet import(
     open_files, Snippet)
from pybitbucket.repository import Repository

import config
from plugins.repository.helper import *


class BitBucketHelper(RepositoryHelper):

    def __init__(self, repo_url=None):
        self.repo_url = repo_url
        self.user_name = None
        self.repo_name = None
        self.repo = None


    def can_process(self, url):
        if "bitbucket.org" in url:
            self.repo_url = url
            return True
        else:
            return False

    def login(self):
        """
        Login using the appropriate credentials
        :return:
        """
        logging.info('Logging into bitbucket')
        try:
            # Try connecting with the consumer key and secret
            # ToDo: Check what actual happens when wrong credentials supplied

            consumer_key = config.bitbucket_consumer_key
            consumer_secret = config.bitbucket_consumer_secret
            bitbucket = Client(
                OAuth1Authenticator(consumer_key, consumer_secret))
            logging.info('Logged into ' + bitbucket.get_bitbucket_url())

            logging.info('url: ' + self.repo_url)

            tokens = self.repo_url.split('/')
            numTokens = len(tokens)
            self.user_name = tokens[numTokens - 2]
            self.repo_name = tokens[numTokens - 1]
            if ('.git') in self.repo_name:
                self.repo_name = self.repo_name.split('.git')[0]

            logging.info('username:' + self.user_name + ' repository:' + self.repo_name)

            full_name = self.user_name + '/' + self.repo_name
            logging.info('full name -> ' + full_name)
            repo = Repository.find_repository_by_full_name(full_name, bitbucket)
            if isinstance(repo, Repository):
                logging.info('Successfully connected to repository ' + full_name)


        except:
            logging.warning('Login to bitbucket failed')


    def get_files_from_root(self, candidate_filenames):
        """
        Given a list of candidate file names, examine the repository root, returning the file names and contents
        :param candidate_filenames: A list of the files of interest e.g. ['COPYING','LICENSE']
        :return: A Dictionary of the form {'filename':file_contents,...}
        """

        found_files = {}
        return found_files





