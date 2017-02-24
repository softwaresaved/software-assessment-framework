import logging
import plugins.metric.metric as metric


class VitalityMetric(metric.Metric):
    """
    Get a list of commits and calculate a vitality score based on this
    As a test, use the following.
    Scores:
    0 if no commits found
    50 if one commit found
    100 if more than one commit found
    """

    CATEGORY = "MAINTAINABILITY"
    SHORT_DESCRIPTION = "Actively developed?"
    LONG_DESCRIPTION = "Calculate the vitality of a repository."

    def run(self, software, helper):
        """
        :param software: An Software entity
        :param helper: A Repository Helper
        :return:
        """
        self.score = 0
        list_commits = helper.get_commits()

        number_commits = len(list_commits)

        if number_commits <= 0:
            self.score = 0
            self.feedback = "This is a DEAD repository."
        else:
            if number_commits <= 1:
                self.score = 50
                self.feedback = "Good job! You've dumped your code in a repo!"
            else:
                self.score = 100
                self.feedback = "Excellent!!! You have an active repo!!!"


    def get_score(self):
        """
        Get the results of running the metric.
        :returns:
        0 if no commits found
        50 if one commit found
        100 if more than one commit found
        """
        return self.score

    def get_feedback(self):
        """
        A few sentences describing the outcome, and providing tips if the outcome was not as expected
        :return:
        """
        return self.feedback
