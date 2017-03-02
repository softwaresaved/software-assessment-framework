import logging
import plugins.metric.metric as metric


class LicenseMetric(metric.Metric):
    """
    Locate and attempt to identify a software license file
    Looks in the root of the repository, for files named: 'LICENSE', 'LICENSE.txt', 'LICENSE.md', 'LICENSE.html','LICENCE', 'LICENCE.txt', 'LICENCE.md', 'LICENCE.html'
    Identifies LGPL, GPL, MIT, BSD, Apache 1.0/1.1/2.0
    Scores:
    0 if no license found
    50 if a license file is present but not idenitfiable
    100 if an identifiable license if found
    """

    INTERACTIVE = False
    CATEGORY = "MAINTAINABILITY"
    SHORT_DESCRIPTION = "Has a license file?"
    LONG_DESCRIPTION = "Test for the existence of file called 'LICENSE' and attempt to identify it from its contents."

    def run(self, software, helper, form_data=None):
        """
        :param software: An Software entity
        :param helper: A Repository Helper
        :param form_data: (Optional) For interactive
        :return:
        """
        self.score = 0
        candidate_files = helper.get_files_from_root(['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'LICENSE.html','LICENCE', 'LICENCE.txt', 'LICENCE.md', 'LICENCE.html'])
        for file_name, file_contents in candidate_files.items():
            # Identify license
            # FixMe - If there is >1 file it's last man in - not desirable
            logging.info('Identifying license')
            if file_contents is not None:

                if "LESSER" in file_contents:
                    license_type = "LGPL"
                elif "GNU GENERAL PUBLIC LICENSE" in file_contents:
                    license_type = "GPL"
                elif " MIT " in file_contents:
                    license_type = "MIT"
                elif "(INCLUDING NEGLIGENCE OR OTHERWISE)" in file_contents:
                    license_type = "BSD"
                elif "Apache" in file_contents:
                    if "2.0" in file_contents:
                        license_type = "Apache 2.0"
                    elif "1.1" in file_contents:
                        license_type = "Apache 1.1"
                    elif "1.0" in file_contents:
                        license_type = "Apache 1.0"
                    else:
                        license_type = "Apache"
                else:
                    license_type = None

                if license_type is not None:
                    # License identifiable - full marks
                    self.score = 100
                    self.feedback = "Well done! This code is licensed under the %s license." % (license_type)
                    break
                else:
                    # License not identifiable - half marks
                    self.score = 50
                    self.feedback = "Well done! This code is licensed, but we can't work out what license it is using. Is it a standard open-source licence?"

    def get_score(self):
        """Get the results of running the metric.
        :returns:
            0 if no license found
            50 if a license file is present but not idenitfiable
            100 if an identifiable license if found
        """
        return self.score

    def get_feedback(self):
        """
        A few sentences describing the outcome, and providing tips if the outcome was not as expected
        :return:
        """
        return self.feedback
