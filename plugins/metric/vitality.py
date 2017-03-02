import logging
import plugins.metric.metric as metric


class VitalityMetric(metric.Metric):
    """
    Get a list of commits and calculate a vitality score based on this
    As a test, use the following.
    Scores:
    0 if no commits found
    50 if one committer found
    100 if more than one committer found
    """

    INTERACTIVE = False
    CATEGORY = "MAINTAINABILITY"
    SHORT_DESCRIPTION = "Calculate number of committers"
    LONG_DESCRIPTION = "Calculate the vitality of a repository."

    def run(self, software, helper):
        """
        :param software: An Software entity
        :param helper: A Repository Helper
        :return:
        """
        self.score = 0
        list_commits = helper.get_commits()

        seen = set([])
        unique_committers = []

        for c in list_commits:
            if c not in seen:
                seen.add(c)
                unique_committers.append(c.committer)

        number_committers = len(unique_committers)

        if number_committers <= 0:
            self.score = 0
            self.feedback = "This is a DEAD repository."
        else:
            if number_committers <= 1:
                self.score = 50
                self.feedback = "You would do well to improve your bus factor"
            else:
                self.score = 100
                self.feedback = "Excellent!!! You have more than one committer!!!"


    def get_score(self):
        """
        Get the results of running the metric.
        :returns:
        0 if no committers found
        50 if one committer found
        100 if more than one committer found
        """
        return self.score

    def get_feedback(self):
        """
        A few sentences describing the outcome, and providing tips if the outcome was not as expected
        :return:
        """
        return self.feedback
