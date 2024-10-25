class Placement:
    """ Placement class represents the list of student placements to be assigned """

    def __init__(self, listOfInputs):
        (
            self.id,
            self.student_name,
            self.name,
            self.cohort,
            self.duration,
            self.start,
            self.start_date,
            self.part,
            self.nurse_assoc,
            self.is_driver,
            self.wardhistory,
            self.dephistory,
            self.covid_status,
        ) = listOfInputs
