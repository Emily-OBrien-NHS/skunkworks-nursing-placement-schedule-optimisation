## Overview
This is an application taken from [skunkworks nurse scheduler](https://github.com/nhsx/skunkworks-nursing-placement-schedule-optimisation) and has been adapted for use at UHPT.
There are 3 page options from the 'Choose your page' drop down. The documentation page provides a more detailed summary of the intentions behind this app, and how the algorithm works.  The other 2 pages are part of the app functionality, and their usage instructions are detailed below.
                
## Create student input sheet
This page enables you to upload the student data provided by the university.  It will re-format it into the required format on the students tab in the input excel file and provide a file download link for this sheet.  You can then copy and paste this into the full input excel file.  It is important that the data from the universities is provided in the consistent format discussed, WORK OUT WHAT THIS IS AND DETAIL/GIVE DOWNLOAD TEMPLATE HERE.

## Run algorithm
This page will allow you to run the algorithm.  When this page is loaded, there is a drop down option to 'select your data source'.

The 'your own data' option will allow you to upload your own filled in input excel file. You can either drag and drop your input file into the upload box or click browse files and navigate to the input file.Errors will appear if there is an issue with the format of this, so please follow the instructions for what should be in each column in the Input File Details section.

Using the 'fake data' option will create an input file with fake students, wards and placements for testing/training purposes.  You can download the fake data file using the link, or just run the algorihtm and look at the outputs.

Once the data is loaded, more of the page will appear.

There are now start and end date options, these should auto-populate using the earliest placement start date in the input data, and the latest end date.  There will be an error message shown if there is an issue with the selected dates.

Below this is a slider of how many schedule outputs you wish to generate, between 1 and 10.  The default is 2.  Due to the random nature of the algorithm, some outputs may be better than others, so generating multiple allows you to select the optimum one.

Next there are a series of initial checks on the provided input data, to try and prempt any obvious issues before running.  These will show error messages if there are more students than capacity allows, if there are any mismatches between the courses students are on and the placements sheet (and which students/placements are affected), and if any ward audits are expired/due to expire.  Please read the messages and make any necessary fixes to the input file and reupload.
                
If there are no issues, then you can run the algorithm using the 'Click here to start running' button at the bottom of the page.  This will begin running, and will display some live metrics and a histogram of the algorithms fitness as it generates different permutations.  After each run, a summary table will appear above these metrics, and will inform you if any of the outputs were viable or not, and provide various scores and counts of issues.
                
Once the algorithm has finished generating all the schedules, their download links will appear at the bottom of the page for you to download.  The schedule comparison document is a copy of the summary table shown on the page. The schedule output files are a detailed output of the schedule, which include multiple different output sheets.
                
If you encounter any other error messages, please contact Emily O'Brien at e.obrien6@nhs.net with a screenshot of the error, copy and paste the full traceback into the email and attatch the file you tried to upload.
