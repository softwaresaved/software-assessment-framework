import logging
from datetime import datetime, date, time, timedelta
import plugins.metric.metric as metric


class VitalityMetric(metric.Metric):
    """
    Get a list of commits and calculate a vitality score based on this

    Scores:
    0 if commiter numbers are decreasing
    50 if commiter numbers are stable
    100 if committer numbers are increasing

    This should be replaced by a score which reflects the actual trends we see.
    """
    NAME = "Vitality"
    IDENTIFIER = "uk.ac.software.saf.vitality"
    SELF_ASSESSMENT = False
    CATEGORY = "MAINTAINABILITY"
    SHORT_DESCRIPTION = "Calculate committer trend"
    LONG_DESCRIPTION = "Calculate the vitality of a repository."
    PERIOD = 180 # Comparison period in days

    def unique_committers_in_date_range(self, helper, start_date, end_date):
        """
        :param helper: A Repository Helper
        :param start_date: datetime for start of range
        :param end_date: datetime for end of range
        :return: number of unique committers to repo during that period
        """
        unique_committers = set([])

        try:
            list_commits = helper.get_commits(since=start_date, until=end_date)
        except Exception as e:
            logging.warning("Exception raised when fetching commits")

        # TODO: the check for a "web-flow" commiter is GitHub specific
        for c in list_commits:
            if c.committer not in unique_committers and str(c.committer) != "web-flow":
                unique_committers.add(c.committer)

        return len(unique_committers)


    def run(self, software, helper):
        """
        :param software: An Software entity
        :param helper: A Repository Helper
        :return:
        """

        self.score = 0

        # Get number of unique committers in this period

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=self.PERIOD)
        current_unique_committers = self.unique_committers_in_date_range(helper, start_date, end_date)

        # Get number of unique committers in the previous period

        end_date = start_date
        start_date = end_date - timedelta(days=self.PERIOD)
        previous_unique_committers = self.unique_committers_in_date_range(helper, start_date, end_date)

        # Calculate a score based on comparing the number of committers
        # For now, use a very simplistic scoring system:
        # Decreasing = bad = 0
        # Level = okay = 50
        # Increasing = good = 100

        if current_unique_committers < previous_unique_committers:
            self.score = 0
            self.feedback = "Number of contributors is declining."
        elif current_unique_committers == previous_unique_committers:
            self.score = 50
            self.feedback = "Number of contributors is stable."
        elif current_unique_committers > previous_unique_committers:
            self.score = 100
            self.feedback = "Number of contributors is growing."
        else:
            logging.warning("Something has gone wrong in comparison")

    def get_score(self):
        """
        Get the results of running the metric.
        :returns:
        0 if commiter numbers are decreasing
        50 if commiter numbers are stable
        100 if committer numbers are increasing
        """
        return self.score

    def get_feedback(self):
        """
        A few sentences describing the outcome, and providing tips if the outcome was not as expected
        :return:
        """
        return self.feedback
