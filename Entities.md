# Entities
Notes on entities and their relationships.  All of these will likely end up as Python classes, most will also be database tables.

![Entities](SAF_ER.png)

## Software
Represents a piece of software submitted for appraisal.

## Metric
Represents the property being measured. E.g. 'Has a license file', 'Percentage test coverage'.  Can be grouped according to category (e.g.  Availability, Usability, Maintainability, Portability).  The Python class will be a plugin with a execute() method which performs the appraisal and records the outcome as Score.

## Score
The outcome of running the metric for a particular piece of software.

## Appraisal
A set of of metrics, weighted according to user choice, along with there scores.

