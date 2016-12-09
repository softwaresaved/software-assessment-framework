# Requirements

The overall goals of the Software Assessment Framework pilot are:

1. Create a framework that will enable research software to be assessed
2. Develop a subset of assessment functionality within that framework
3. Pilot the assessment framework on a selection of projects

## The Framework

The framework is expected to consist of  website / application that enables a user
to assess a piece of software, including:
* manual self-assessment via questions
* automated analysis of the software
* aggregate data from both manual and automated assessment to produce scores/levels
* visualisation of the results of the assessment

The requirements for the framework are:

* Access
  * It must be available through a web browser
  * It must allow a user to log in
  * It could allow a user to log in using their ORCID
  * It could allow a user to log in using their GitHub credentials
  * It must allow a user to create an "assessment"
  * It should allow a user to save and return to an assessment
  * It could allow a user to share an assessment
  * It could allow a user to display an open badge based on the assessment
* Measurement
  * It must allow for two basic forms of measurement: self-assessment and automated analysis
    * self assessment e.g. does the software have a short description?
    * automated analysis e.g. what is the frequency of releases?
    * some things may be possible via both mechanisms e.g. does the software have a license?
  * It must allow for new measurement functionality to be added in the future easily as "plugins"
  * It must enable these measures to be grouped and combined in customisable ways, to produce numerical scores or levels
  * It could allow users to create their own custom assessments based on all available measures
* Visualisation
  * It must enable the user to understand the results of each assessment category
  * It should show whether a piece of software has passed a particular assessement "level"
  * It could show results as spider plots or pie segments based on the four categories  
* Assessment Plugins
  * It must provide functionality for checking if the software has a description
  * It must provide functionality for checking if the software has a license
  * It should provide functionality for recording what type of license
  * It must provide functionality for identifying the availability of source code
  * It should provide functionality for identifying if the software provides test data
  * It should provide functionality for identifying if the software includes tests
  * It could provide functionality for measuring the test coverage
  * It should provide functionality for identifying the level of user documentation
  * It should provide functionality for identifying the level of developer documentation
  * It should provide functionality for working out the release frequency
  * It should provide functionality for working out the trend in contributors
  * It should provide functionality for identifying examples of use
  * It could provide functionality for identifying citations based on a DOI (via ImpactStory or Depsy API?)
  * It could provise funtionality for identifying citations based on a URL
* Integration
  * It should be able to interface with the Depsy API (e.g. to identify citations)
  * It could be able to interface to the Libraries.io API (e.g. to pull the Sourcerank info)
  * It must be able to interface to the GitHub API (e.g. to identify number of watchers, contributors, release frequency)
* Programming Language
  * It should be written in either Python or Ruby


# Related work

Original prototype from CW:
* https://github.com/OpenSourceHealthCheck/healthcheck

Other assessment frameworks for data and software
* http://depsy.org/package/python/scipy
* https://libraries.io/pypi/scipy/sourcerank
* https://www.openhub.net/p/scipy
* http://ontosoft.org/ontology/software/
* http://www.ontosoft.org/portal/#browse/Software-mZ8BhPHA5SQq
* https://certificates.theodi.org/en/
* http://www.datasealofapproval.org/en/

Related work on software metadata:
* Software Discovery Dashboard: https://github.com/mozillascience/software-discovery-dashboard
* CodeMeta: https://github.com/codemeta/codemeta
* Code as a Research Object: https://science.mozilla.org/projects/codemeta

Repositories containing software with DOIs / identifiers
* SciCrunch: https://scicrunch.org
* figshare: https://figshare.com/
* OSF: https://osf.io/
* Zenodo: https://zenodo.org/

Dependency analysis:
* Depsy: http://depsy.org/
* Libraries.io: https://libraries.io/

Impact Analysis:
* Lagotto: http://www.lagotto.io
* ContentMine: http://contentmine.org/
* ScholarNinja: https://github.com/ScholarNinja/software_metadata

Automated code analysis:
* http://coala-analyzer.org/
* https://pypi.python.org/pypi/radon
* https://www.openhub.net/

Tools for identifying scientific software:
* https://github.com/ScholarNinja/software_metadata

Models for assessing code:
* https://communitymodel.sharepoint.com/Pages/default.aspx
* https://en.wikipedia.org/wiki/Capability_Maturity_Model_Integration
* http://oss-watch.ac.uk/apps/openness/

Making software more visible:
* http://signposting.org/


## Models of representing success

* Howison, J., Deelman, E., McLennan, M. J., Silva, R. F. da, & Herbsleb, J. D. (2015). [Understanding the scientific software ecosystem and its impact: Current and future measures](http://doi.org/10.1093/reseval/rvv014). Research Evaluation, 24(4), 454–470. http://doi.org/10.1093/reseval/rvv014
* Crowston, K., Howison, J., & Annabi, H. (2006). [Information systems success in free and open source software development: Theory and measures](http://onlinelibrary.wiley.com/doi/10.1002/spip.259/abstract). Software Process: Improvement and Practice, 11(2), 148.
* Delone, W., & Mclean, E. (2003). [The Delone and Mclean model of Information Systems Success: A ten year update](http://dl.acm.org/citation.cfm?id=1289767). Journal of MIS, 19(4), -30.
* Subramaniam, C. et al. 2009. Determinants of open source software project success: A longitudinal study. Decision Support Systems, vol. 46, pp. 576-585.
* English, R., and Schweik, C. 2007. Identifying success and abandonment of FLOSS commons: A classification of Sourceforge.net projects, Upgrade: The European Journal for the Informatics Professional VIII, vol. 6.
* Wiggins, A. and Crowston, K. 2010. Reclassifying success and tragedy in FLOSS projects. Open Source Software: New Horizons, pp. 294-307.
* Piggott, J. and Amrit, C. 2013. How Healthy Is My Project? Open Source Project Attributes as Indicators of Success. In Proceedings of the 9th International Conference on Open Source Systems. DOI: 10.1007/978-3-642-38928-3_3.
* Gary C. Moore, Izak Benbasat. 1991. Development of an Instrument to Measure the Perceptions of Adopting an Information Technology Innovation Information Systems Research 19912:3 , 192-222

## Reusability and Maturity

* Holibaugh, R et al. 1989. Reuse: where to begin and why. Proceedings of the conference on Tri-Ada '89: Ada technology in context: application, development, and deployment. p266-277. DOI: 10.1145/74261.74280.
* Frazier, T.P., and Bailey, J.W. 1996. The Costs and Benefits of Domain-Oriented Software Reuse: Evidence from the STARS Demonstration Projects. Accessed on 21st July 2014 from: http://www.dtic.mil/dtic/tr/fulltext/u2/a312063.pdf
* CMMI Product Team, 2006. CMMI for Development, Version 1.2. SEI Identifier: CMU/SEI-2006-TR-008.
* Gardler, R. 2013. Software Sustainability Maturity Model. Accessed on 21st July 2014 from: http://oss-watch.ac.uk/resources/ssmm
* NASA Earth Science Data Systems Software Reuse Working Group (2010). Reuse Readiness Levels (RRLs), Version 1.0. April 30, 2010. Accessed from: http://www.esdswg.org/softwarereuse/Resources/rrls/
* Marshall, J.J., and Downs, R.R. 2008. Reuse Readiness Levels as a Measure of Software Reusability. In proceedings of Geoscience and Remote Sensing Symposium. Volume 3. P1414-1417. DOI: 10.1109/IGARSS.2008.4779626
* Chue Hong, N. 2013. Five stars of research software. Accessed on 8th July 2016 from: http://www.software.ac.uk/blog/2013-04-09-five-stars-research-software

## Software Quality

* Bourque, P. and Fairley, R.E. eds., (2014) Guide to the Software Engineering Body of Knowledge, Version 3.0, IEEE Computer Society http://www.swebok.org
* ISO/IEC 25010:2011(en) (2011) Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models
* Microsoft Code Analysis Team Blog. 2007. Maintainability Index Range and Meaning. Accessed on 8th July 2016 from: https://blogs.msdn.microsoft.com/codeanalysis/2007/11/20/maintainability-index-range-and-meaning/
* Sjoberg, D.I.K et. al. 2012. Questioning Software Maintenance Metrics: A Comparative Case Study. In proceedings of ESEM’12. P107-110. DOI: 10.1145/2372251.2372269


## Badging

* Blohowiak, B. B., Cohoon, J., de-Wit, L., Eich, E., Farach, F. J., Hasselman, F., … DeHaven, A. C. (2016, October 10). [Badges to Acknowledge Open Practices](http://osf.io/tvyxz). Retrieved from http://osf.io/tvyxz
