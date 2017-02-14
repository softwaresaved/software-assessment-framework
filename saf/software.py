import logging
import plugins.metric
from plugins.repository.helper import *

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
