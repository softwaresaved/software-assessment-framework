import logging

from plugins.metric.license import LicenseMetric
from plugins.repository.helper import RepositoryHelper


class BitBucketHelper(RepositoryHelper):
    def can_process(self, url):
        if "bitbucket.com" in url:
            self.repo_url = url
            return True
        else:
            return False

    def __init__(self, repo_url=None):
        self.repo_url = repo_url

        if self.repo_url is not None:
            logging.info('Logging in to BitBucket')

    def get_license(self):
        """Identify and return license file
            :returns
                The contents of the license file as a (something - Weakly typed ftw)
        """
        return LicenseMetric(filename="Dummy", license_text="None")
