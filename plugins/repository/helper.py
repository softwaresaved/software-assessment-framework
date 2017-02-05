import yapsy.IPlugin


class RepositoryHelper(yapsy.IPlugin.IPlugin):
    """
    Base class for repository helper plugins
    """

    def can_process(self, url):
        """Parse URL string to determine if implementation can work with corresponding repository"""
        raise NotImplementedError("This method must be overridden")

    # TODO - Change this to just fetch_file(name)

    def get_license(self):
        """Identify and return license file
            :returns
                The contents of the license file as a (something - Weakly typed ftw)
        """
        raise NotImplementedError("This method must be overridden")

    def get_readme(self):
        """Identify and return README file
            :returns
                The contents of the README file as a (something - Weakly typed ftw)
        """
        raise NotImplementedError("This method must be overridden")
