import yapsy.IPlugin


class Metric(yapsy.IPlugin.IPlugin):
    """
    Base class for repository metric plugins.
    Metrics should be atomic, measuring one thing and providing a score 0-100.
    For example, the absence of a license file might result in a score of 0,
    If a LICENSE file is present, but not identifiable as known license, a score of 50
    The presence of an identifiable license results in a score of 100.
    """
    category = None # AVAILABILITY, USABILITY, MAINTAINABILITY, PORTABILITY

    def run(self, software, helper):
        """
        The main method to run the metric.
        :param software: An instance of saf.software.Software
        :param helper: An instance of plugins.repository.helper.RepositoryHelper
        :return:
        """
        raise NotImplementedError("This method must be overridden")

    def get_score(self):
        """Get the results of running the metric.
        :returns:
            This should be an integer between 0 and 100
        """
        raise NotImplementedError("This method must be overridden")

    def get_short_description(self):
        """A one or two sentence description of the metric"""
        raise NotImplementedError("This method must be overridden")


    def get_long_description(self):
        """ (Optional) A longer descriptions of the metric
        :return:
         description of the metric"""
        raise NotImplementedError("This method must be overridden")

    def get_feedback(self):
        """
        A few sentences describing the outcome, and providing tips if the outcome was not as expected
        :return:
        """
        raise NotImplementedError("This method must be overridden")