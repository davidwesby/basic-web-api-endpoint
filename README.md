# Description
A simple web API to provide analytics for a pretend e-commerce business.

# Installation
All the project dependencies are listed in the `requirements.txt`.

The code was tested using Python 3.7.

# Documentation
There is documentation in the code in the form of docstrings and comments. The
 important points are:
 - the path to the endpoint is `/api/v1/e-shop_report`;
 - the date must be provided in the form of three query strings: a `y` parameter for
  the year, an `m` parameter for the month and a `d` parameter for the day.