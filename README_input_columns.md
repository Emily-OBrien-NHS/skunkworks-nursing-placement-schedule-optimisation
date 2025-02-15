# Algorithm Input File Information

## Students Sheet

This sheet contains all the information on the students to be placed by the model.  If using the excel file provided by the universities to generate this sheet, please ensure it conforms to the agreed format (ADD INFO ON Create Student Input Sheet page).

#### student_id
The student's id number.  Leave blank if id is not known.

Example: 10777436

#### Forename
The student's forename

Example: Jane

#### Surname
The student's surname

Example: Doe

#### university
The name of the university the student attends. (**Note:** This must **exactly match** the same value in the university column in the placements sheet, and must match across all students at that univeristy)

Example: University of Plymouth

#### qualification
The name of the qualification the student is studying for. (**Note:** This must **exactly match** the same value in the qualification column in the placements sheet, and must match across all students doing that qualification)
(**Note:** If student is on a nurse associate course, this must contain the words 'Nursing Associate' so that the algorithm can ensure it doesn't exceed the nursing associate capacities on the wards)

Example: Nur Adult BSC

#### course_start
The date the student began studying on this course (**Note:** This must **exactly match** the same value in the course_start column in the placements sheet, and must match across all students on that course with that start date)

Example: Sep-24

#### year
The year of study the student is currently.

Example: Year 1

#### prev_placements
A list of all the previous placements a student has done.  (**Note:** These must **exactly match** the same value in the ward_name column on the ward sheet, or the student could be placed on the same ward again.  For any wards in these lists that UHPT don't allocate to, you can add them to the wards sheet with 0 for the capacity columns, so the algorithm will know which specialties the students have been under previously and try not to repeat them. (education_audit_exp column can be left blank, put 'Low/Medium'  for covid_status, and False for the remaining columns))

Example: [] if no previous placements, or ['Ward1', 'ward2', 'ward3']

#### is_driver
Flag if student can drive and therefore could be assigned more remote placements.

Example: TRUE or FALSE

#### allowable_covid_status
A flag to signal if a student is high risk if they get covid, to avoid allocating these students to a ward where there is a higher covid risk. (**Note:** This is no longer in use, but has been left in case it is needed again in the future.  As such, all values are now Low/Medium)

Example: Low/Medium

## Wards Sheet

A sheet containing all the wards you can place students onto (and other wards the student may have been to previously, to capture their specialty).

#### ward_name
The name of the ward (**Note**: These must **exactly match** the same values in the previous_placemtns column on the students sheet, or the student could be placed on the same ward again.  For any wards in the student placement lists that UHPT don't allocate to, you can add them to the wards sheet with 0 for the capacity columns, so the algorithm will know which specialties the students have been under previously and try not to repeat them. (education_audit_exp column can be left blank, put 'Low/Medium'  for covid_status, and False for the remaining columns))

Example:  Ward 1

#### ward_specialty
The specialty of that ward

Example: Medical

#### education_audit_exp
The date that ward's educational audit is due to expire. The algorithm will flag any audits that have already expired, or will expire during the placement. These are of the format dd/mm/yyyy

Example: 20/08/2027

#### covid_status
A flag to signal the covid risk of a ward, to avoid allocating at risk students to a ward where there is a higher covid risk. (**Note:** This is no longer in use, but has been left in case it is needed again in the future.  As such, all values are now Low/Medium)

Example: Low/Medium

#### capacity_num
The overall number of students that ward can take - 0 for wards we don't allocate to.  (**Note:** This must not be lower than any of the Pn_cap or nurse_associate_cap columns)

Example: 5

#### pn_cap
The number of year n students that ward can take - 0 for wards we don't allocate to.  (**Note:** This must be less than or equal to the capacity_num column)

Example: 3

#### nurse_associate_cap
The number of nursing associate students that ward can take - 0 for wards we don't allocate to.  (**Note:** This must be less than or equal to the capacity_num column)

(**Note:** for a student flag as a nursing associate, their qualification must contain the words 'Nursing Associate', and this must match the placements sheet)

Example: 3

#### need_to_drive
A flag of if a ward is remote and would therefore only be able to take students who are able to drive themselves there.

Example: True or False

#### DYAD
A flag if the ward does DYAD and therefore could take a higher capacity of students, providing there is a roughly even distribution across all year groups.

Example: True or False

## Placements Sheet

A sheet detailing the placemetns for each course that you want the algorithm to place.

#### university
The name of the university for this placement. (**Note:** This must **exactly match** the same value in the university column in the students sheet, and must match across all students at that univeristy)

Example: University of Plymouth

#### qualification
The name of the qualification for this placement. (**Note:** This must **exactly match** the same value in the qualification column in the students sheet, and must match across all students doing that qualification)
(**Note:** If the course is a nurse associate course, this must contain the words 'Nursing Associate' so that the algorithm can ensure it doesn't exceed the nursing associate capacities on the wards)

Example: Nur Adult BSC

#### course_start
The date the course began (**Note:** This must **exactly match** the same value in the course_start column in the students sheet, and must match across all students on that course with that start date)

Example: Sep-24

#### placement_name
The placement you want the algorithm to schedule for that course (Note: must contain ':' separator)

Example: Year 1: Placement 2

#### placement_start_date
The date the students will start this placement.  This is of the format dd/mm/yyyy

Example: 22/04/2025

#### placement_len_weeks
The number of weeks this placement will last for.

Example: 10

# Students Sheet Input File

This is the input from the university to allow the Create Student Input Sheet page on the app to run.  This will take the data from the university and put it into the correct format to copy and paste into your input file for the algorithm, avoiding the need to manually do this.  However, in order for this to work, the data from the uni must be consistent and follow the below column names and formats.

#### Intake
This the course the student is on, and when they started.  If this is left blank, that row will be removed from the data so it is important that this is filled in.  This must follow the format of (start month initial)(start year) (univeristy initials) (course name).  Some examples are:

J22 UOP NUR APP ADULT PT
S24 MJN NURS ADULT BSC

The key bits which must follow the same format or this code won't work are:

- the name must begin with the format MonthYearYear (e.g. S24) followd by a space.  The month part could be just the initial (S or J) or a shortened version (Sept or Jan).  The important parts are it is followed by the 2 digit version of the year, and then a space before the next part of the course name.
- the next part of the name must be the univeristy initials, which are UOP for University of Plymouth or MJN for Marjon, again followed by a space.
- Then the rest of the course name.

#### Uni Number
The student's id number.  Leave blank if id is not known.
Example: 10777436

#### Surname
The Student's surname

#### Forename
The Student's forename

#### Driver
Column to indicate if the student is a driver or not.  Should be filled in as Yes or No.  Anything other than Yes (including typos of Yes e.g. Ys, Yse, Y) will be considered a non-driver.

#### Placement n -
These are multiple columns of a student's previous placements.  The important points with these columns are that the word placement is in the column name and that the ward name exactly matches the ward name on the ward sheet (so the algorithm can try to avoid placing the student on the same ward twice).



Once this has created an output, you can download it and copy and past the table into the student sheet in your input file.  You shoud then check that the courses on this page match the placements page before trying to run the algorithm.