import pandas as pd
import numpy as np
import datetime

df = pd.read_excel('data/Data sent from University.xlsx').dropna(subset='Cohort  ')

cohort_split = df['Cohort  '].str.split(' ')
course_start = cohort_split.str[0]
university = cohort_split.str[1]
qualification = cohort_split.str[2:].str.join(' ')
year = ('Year ' + (datetime.now().year
                   - ('20' + course_start.str.findall(r'\d+').str[0]).astype(int)
                   + 1).astype('str'))
past_placements = (df[[col for col in df.columns
                       if ('placement' in col.lower())
                       or ('unnamed' in col.lower())]]
                       .replace('X', np.nan).values.tolist())
past_placements = [[e for e in row if e==e] for row in past_placements]

students_tab = pd.DataFrame({'student_id':df['Student Number'],
                             'Forename':df['Forename'],
                             'Surname':df['Surname'],
                             'university':university,
                             'qualification':qualification,
                             'course_start':course_start,
                             'year': year,
                             'prev_placements':past_placements})

students_tab.to_excel('data/Students tab.xlsx', index=False)