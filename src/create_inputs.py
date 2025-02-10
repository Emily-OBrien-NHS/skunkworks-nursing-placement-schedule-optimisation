import pandas as pd
import numpy as np
import datetime
import io

class InputTemplate:
    def create_input_template():
        # Create dataframe with original data fields
        student_columns = ["student_id", "Forename", "Surname",	"university",
                           "qualification", "course_start", "year",
                           "prev_placements", "is_driver",
                           "allowable_covid_status"]
        student_df = pd.DataFrame(columns=student_columns)
        # Create dataframe with original data fields
        ward_columns = ["ward_name", "ward_speciality",	"education_audit_exp",
                        "covid_status", "capacity_num", "p1_cap", "p2_cap",
                        "p3_cap", "nurse_associate_cap",	"need_to_drive",
                        "DYAD"]
        ward_df = pd.DataFrame(columns=ward_columns)
        # Create dataframe with original data fields
        placement_columns = ["university", "qualification",	"course_start",
                             "placement_name", "placement_start_date",
                             "placement_len_weeks"]
        placement_df = pd.DataFrame(columns=placement_columns)
        #create excel file
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        student_df.to_excel(writer, sheet_name="students", index=False)
        ward_df.to_excel(writer, sheet_name="wards", index=False)
        placement_df.to_excel(writer, sheet_name="placements", index=False)
        writer.close()
        input_data = output.getvalue()
        return input_data
    
class StudentTab:
    def student_output_to_excel(self, df):
        """
        Function to create the output UHPT excel file before creating the
        download link.

        Returns:
            processed_data : the excel file ready to create the link
        """
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.close()
        processed_data = output.getvalue()
        return processed_data
    
    def create_student_tab(self, file):
        df = pd.read_excel(file).dropna(subset='Intake')

        cohort_split = df['Intake'].str.split(' ')
        course_start = cohort_split.str[0]
        university = cohort_split.str[1].map({'UOP':'University of Plymouth',
                                            'MJN':'Plymouth Marjon University'})
        qualification = cohort_split.str[1:].str.join(' ').str.strip()
        year = ('Year ' + (datetime.datetime.now().year
                        - ('20' + course_start.str.findall(r'\d+').str[0]
                           ).astype(int) + 1).clip(upper=3).astype(str))
        past_placements = (df[[col for col in df.columns
                            if ('placement' in col.lower())
                            or ('unnamed' in col.lower())]]
                            .replace('X', np.nan).values.tolist())
        past_placements = [[e for e in row if e==e] for row in past_placements]
        is_driver = (df['Driver'].str.lower().fillna('no')
                     .map({'no':False, 'yes':True}).fillna(False).astype(bool))

        students_tab = pd.DataFrame({'student_id':df['Uni Number'],
                                    'Forename':df['Forename'],
                                    'Surname':df['Surname'],
                                    'university':university,
                                    'qualification':qualification,
                                    'course_start':(course_start
                                                    .str.replace('S', 'Sep-')
                                                    .str.replace('J','Jan-')),
                                    'year': year,
                                    'prev_placements':past_placements,
                                    'is_driver':is_driver,
                                    'allowable_covid_status':(['Low/Medium']
                                                              *len(df))})
        return self.student_output_to_excel(students_tab)