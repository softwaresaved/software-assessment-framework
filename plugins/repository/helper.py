import yapsy.IPlugin
import logging
import plugins.repository


class RepositoryHelper(yapsy.IPlugin.IPlugin):
    """
    Base class for repository helper plugins
    """

    def can_process(self, url):
        """
        Parse URL string to determine if implementation can work with corresponding repository
        :param url: The repository URL
        :return: True if the helper can handle this URL. False if it can't
        """
        raise NotImplementedError("This method must be overridden")

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


def find_repository_helper(url):
    """
    Use the plugin system to find an implementation of RepositoryHelper that is able to communicate with the repository
    :param url: The repository URL
    :return: An implementation of RepositoryHelper
    """
    logging.info("Finding a repository helper plugin to handle URL:"+url)
    repository_helpers = plugins.repository.load()
    for helper in repository_helpers:
        if helper.can_process(url):
            logging.info(helper.__class__.__name__ + " - can handle that URL")
            return helper
        else:
            logging.debug(helper.__class__.__name__ + " - can't handle that URL")

    logging.warning("Unable to identidy a repository helper")
    return None

# Exceptions


class RepositoryHelperError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message):
        self.message = message


class RepositoryHelperRepoError(RepositoryHelperError):
    """Exception raised for errors accessing the given repository

    Attributes:
        message -- explanation of the error
    """

