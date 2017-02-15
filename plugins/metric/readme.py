import logging
import plugins.metric.metric as metric


class ReadmeMetric(metric.Metric):
    """
    Find and attempt to identify a README file
    """

    def run(self, software, helper):
        """"
        Attempt to locate a REAME file licence
        """
        self.license_text = helper.get_readme()
        logging.info('Locating README')
        self.score = 0
        if self.license_text is not None:
            self.score = 100
        else:
            self.score = 0

            if self.license_type is not None:
               self.feedback = "README found"
            else:
                self.feedback = "A short, descriptive, README file can provide a useful first port of call for new users."

    def get_score(self):
        """Get the results of running the metric.
        :returns:
            0 if no license found
            50 if a license file is present but not idenitfiable
            100 if an identifiable license if found
        """
        return self.score

    def get_short_description(self):
        """A one or two sentence description of the metric"""
        return ("Has a README file?")

    def get_long_description(self):
        """ (Optional) A longer descriptions of the metric
        :return:
         description of the metric"""
        return ("Test for the existence of file 'REAMDE'.")

    def get_feedback(self):
        """
        A few sentences describing the outcome, and providing tips if the outcome was not as expected
        :return:
        """
        return self.feedback