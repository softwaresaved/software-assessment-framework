import logging
import plugins.metric.metric as metric


class DocumentationDeveloperMetric(metric.Metric):
    """
    Interactive, self-assessment metric
    Ask submitter about the extent of their developer documentation
    Scores:
    0 if "No documentation"
    50 if "Minimal developer documentation"
    100 if "Comprehensive documentation"
    """

    INTERACTIVE = True
    CATEGORY = "MAINTAINABILITY"
    SHORT_DESCRIPTION = "Developer Documentation?"
    LONG_DESCRIPTION = "Do you provide documentation for developers wanting to contribute to, extend or fix bugs in your project?"

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
            self.feedback = "Without at least basic documentation, developers are unlikely to contribute new code or fix bugs."
        if self.score == 50:
            self.feedback = "Basic developer docs are a great start. Consider providing more comprehensive documentation too."
        if self.score == 100:
            self.feedback = "Great, your software has excellent documentation for developers."

    def get_score(self):
        return self.score

    def get_feedback(self):
        return self.feedback

    def get_ui_choices(self):
        return {
            "100": "Comprehensive developer documentation covering all aspects of architecture, contribution and extension",
            "50": "Minimal developer documentation only. e.g. an architectural overview",
            "0": "No developer docmentation"
        }
