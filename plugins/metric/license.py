import logging
import plugins.metric.metric as metric


class LicenseMetric(metric.Metric):
    """
    Find and attempt to identify a software license file
    """

    category = 'USABILITY'

    def run(self, software, helper):
        """"
        Attempt to identify licence
        :returns A string identifying the license
        """
        self.license_text = helper.get_license()
        logging.info('Identifying license')
        self.score = 0
        if self.license_text is not None:
            self.score = 100
            if "LESSER" in self.license_text:
                self.license_type = "LGPL"
            elif "GNU GENERAL PUBLIC LICENSE" in self.license_text:
                self.license_type = "GPL"
            elif " MIT " in self.license_text:
                self.license_type = "MIT"
            elif "(INCLUDING NEGLIGENCE OR OTHERWISE)" in self.license_text:
                self.license_type = "BSD"
            elif "Apache" in self.license_text:
                if "2.0" in self.license_text:
                    self.license_type = "Apache 2.0"
                elif "1.1" in self.license_text:
                    self.license_type = "Apache 1.1"
                elif "1.0" in self.license_text:
                    self.license_type = "Apache 1.0"
                else:
                    self.license_type = "Apache"
            else:
                self.license_type = None
                self.score = 50

            if self.license_type is not None:
               self.feedback = "Well done! This code is licensed under the %s license." % (self.license_type)
            else:
                self.feedback = "Well done! This code is licensed, but we can't work out what license it is using. Is it a standard open-source licence?"

        return self.license_type

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
        return ("Has a license file?")

    def get_long_description(self):
        """ (Optional) A longer descriptions of the metric
        :return:
         description of the metric"""
        return ("Test for the existence of file 'LICENSE' and attempt to identify it from it's content.")

    def get_feedback(self):
        """
        A few sentences describing the outcome, and providing tips if the outcome was not as expected
        :return:
        """
        return self.feedback