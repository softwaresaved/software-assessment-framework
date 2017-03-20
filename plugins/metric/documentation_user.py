import logging
import plugins.metric.metric as metric


class DocumentationUserMetric(metric.Metric):
    """
    Interactive, self-assessment metric
    Ask submitter about the extent of their end-user documentation
    Scores:
    0 if "No documentation"
    50 if "Minimal installation documentation"
    100 if "Comprehensive documentation"
    """

    INTERACTIVE = True
    CATEGORY = "USABILITY"
    SHORT_DESCRIPTION = "End user documentation"
    LONG_DESCRIPTION = "Do you provide end-user documentation?  If so, how extensive is it?"

    def run(self, software, helper=None, form_data=None):
        """
        The main method to run the metric.
        :param software: An instance of saf.software.Software
        :param helper: An instance of plugins.repository.helper.RepositoryHelper
        :param form_data: (Optional) For interactive
        :return:
        """
        self.score = int(form_data)
        if self.score == 0:
            self.feedback = "Without at least basic documentation, end users are unlikely to use your software."
        if self.score == 50:
            self.feedback = "Installation instructions are a great start. Consider providing more comprehensive documentation too."
        if self.score == 100:
            self.feedback = "Great, your software is well documented."

    def get_score(self):
        return self.score

    def get_feedback(self):
        return self.feedback

    def get_ui_choices(self):
        return {
            "100": "Comprehensive documentation covering all aspects of installation and use",
            "50": "Minimal installation documentation only",
            "0": "No Docmentation"
        }
