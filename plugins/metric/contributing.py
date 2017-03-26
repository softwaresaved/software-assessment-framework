import logging
import plugins.metric.metric as metric


class ContributingMetric(metric.Metric):
    """
    Locate a CONTRIBUTING file
    Looks in the root of the repository, for files named: 'CONTRIBUTING',
    'CONTRIBUTING.txt', 'CONTRIBUTING.md', 'CONTRIBUTING.html'
    Scores:
    0 if no CONTRIBUTING file found
    100 if CONTRIBUTING file with non-zero length contents is found
    """
    # TODO: decide which category this metric should fall into

    NAME = "Contribution Policy"
    IDENTIFIER = "uk.ac.software.saf.contributing"
    CATEGORY = "USABILITY"
    SHORT_DESCRIPTION = "Has a CONTRIBUTING file?"
    LONG_DESCRIPTION = "Test for the existence of CONTRIBUTING file."

    def run(self, software, helper):
        """
        :param software: An Software entity
        :param helper: A Repository Helper
        :return:
        """
        self.score = 0
        self.feedback = "A short, descriptive, CONTRIBUTING file can provide a useful first port of call for new developers."
        candidate_files = helper.get_files_from_root(['CONTRIBUTING', 'CONTRIBUTING.txt', 'CONTRIBUTING.md', 'CONTRIBUTING.html'])
        for file_name, file_contents in candidate_files.items():
            logging.info('Locating CONTRIBUTING')
            self.score = 0
            if file_contents is not None:
                self.score = 100
                self.feedback = "CONTRIBUTING file found"
                break
            else:
                self.score = 0
                self.feedback = "A short, descriptive, CONTRIBUTING file can provide a useful first port of call for new developers."

    def get_score(self):
        """Get the results of running the metric.
        :returns:
            0 if no CONTRIBUTING found
            100 if an identifiable CONTRIBUTING file is found
        """
        return self.score

    def get_feedback(self):
        """
        A few sentences describing the outcome, and providing tips if the outcome was not as expected
        :return:
        """
        return self.feedback
