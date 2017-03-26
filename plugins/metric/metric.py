import yapsy.IPlugin


class Metric(yapsy.IPlugin.IPlugin):
    """
    Base class for repository metric plugins.
    Metrics should be atomic, measuring one thing and providing a score 0-100.
    For example, the absence of a license file might result in a score of 0,
    If a LICENSE file is present, but not identifiable as known license, a score of 50
    The presence of an identifiable license results in a score of 100.
    """

    NAME = "UNSET"
    # Short, descriptive, human readable name for this metric - e.g. "Vitality", "License", "Freshness"

    IDENTIFIER = "uk.ac.software.saf.metric"
    # A *meaningful* unique identifier for this metric.
    # To avoid collisions, a reverse domain name style notation may be used, or your-nick.metric-name
    # The final part should coincide with the module name

    CATEGORY = "UNSET"
    # "AVAILABILITY", "USABILITY", "MAINTAINABILITY", "PORTABILITY"

    SHORT_DESCRIPTION = "UNSET"
    # A one or two sentence description of the metric, to be displayed to the user
    # If the metric is interactive, this will be presented to the user as the question

    LONG_DESCRIPTION = "UNSET"
    # Longer description of the metric, how it works and explanation of scoring

    SELF_ASSESSMENT = None
    # None / False - Non-interactive - Doesn't require user input beyond the repository URL
    # True - Interactive - Assessment is based solely on user input

    def run(self, software, helper=None, form_data=None):
        """
        The main method to run the metric.
        :param software: An instance of saf.software.Software
        :param helper: (Optional) An instance of plugins.repository.helper.RepositoryHelper, None if interactive
        :param form_input: (Optional) For interactive
        :return:
        """
        raise NotImplementedError("This method must be overridden")

    def get_score(self):
        """Get the results of running the metric.
        :returns:
            This should be an integer between 0 and 100
        """
        raise NotImplementedError("This method must be overridden")

    def get_feedback(self):
        """
        A few sentences describing the outcome, and providing tips if the outcome was not as expected
        :return:
        """
        raise NotImplementedError("This method must be overridden")

    def get_ui_choices(self):
        """
        Optional.  If the metric is interactive, a set of radio buttons is generated based on this.
        :returns: A Dictonary {Option Value: Option label}
        e.g:
         return {
            "100": "Comprehensive documentation covering all aspects of installation and use",
            "50": "Minimal installation documentation only",
            "0": "No Docmentation"
        }
        The selected Value is returned to the run() method above.
        """