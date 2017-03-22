import logging
import plugins.metric.metric as metric


class ReadmeMetric(metric.Metric):
    """
    Locate a README file
    Looks in the root of the repository, for files named: 'README', 'README.txt', 'README.md', 'README.html'
    Scores:
    0 if no README found
    100 if README file with non-zero length contents is found
    """

    # FixMe - implement IDENTIFIER = "uk.ac.software.saf.readme"
    INTERACTIVE = False
    CATEGORY = "USABILITY"
    SHORT_DESCRIPTION = "Has a README file?"
    LONG_DESCRIPTION = "Test for the existence of file 'README'."

    def run(self, software, helper):
        """
        :param software: An Software entity
        :param helper: A Repository Helper
        :return:
        """
        self.score = 0
        candidate_files = helper.get_files_from_root(['README', 'README.txt', 'README.md', 'README.html'])
        for file_name, file_contents in candidate_files.items():
            logging.info('Locating README')
            self.score = 0
            if file_contents is not None:
                self.score = 100
                self.feedback = "README found"
                break
            else:
                self.score = 0
                self.feedback = "A short, descriptive, README file can provide a useful first port of call for new users."

    def get_score(self):
        """Get the results of running the metric.
        :returns:
            0 if no README found
            100 if an identifiable README is found
        """
        return self.score

    def get_feedback(self):
        """
        A few sentences describing the outcome, and providing tips if the outcome was not as expected
        :return:
        """
        return self.feedback
