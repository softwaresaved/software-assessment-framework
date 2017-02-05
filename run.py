import config
import plugins.repository
from saf.software import *
from datetime import datetime
from yapsy.PluginManager import PluginManager
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s %(funcName)s() - %(message)s')


def main():
    logging.info('Start')

    # TODO instantiate from JSON - perhaps add functionality in Software __init__()
    sw = Software(software_id=None,
                  name='Climate Analysis',
                  description='Contrived code for Software Carpentry workshops',
                  version='1.0',
                  submitter='JSR',
                  submitted=datetime.utcnow(),
                  url='https://github.com/js-robinson/climate-analysis',
                  upload_path='github')

    process_software(sw)

def process_software(sw):
    """
    The main process.  Identify and run appropriate metrics.
    :param sw: An instance of Software representing a the subject of appraisal
    :return: None
    """
    logging.info('Processing software item: '+sw.name)
    # Examine the URL, identify which repository helper to use

    if sw.url and sw.url != "".strip():
        repos_helper = find_repository_helper(sw.url)
        if repos_helper is None:
            logging.info('Unable to process software item: ' + sw.name)
            exit(1)

    #Find / Iterate through metrics
    logging.info("Finding metrics")
    metrics = plugins.metric.load()
    for metric in metrics:
        logging.info("Running metric: "+metric.get_short_description())
        metric.run(sw, repos_helper)
        logging.info(metric.get_score())
        logging.info(metric.get_feedback())

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

if __name__ == '__main__':
    main()
