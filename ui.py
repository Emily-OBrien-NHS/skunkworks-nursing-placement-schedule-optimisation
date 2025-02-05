import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import yaml
import os
from src.create_inputs import InputTemplate
from src.create_inputs import StudentTab
from src.data_load import DataLoader
from src.GeneticAlgorithm import GeneticAlgorithm
from src.Schedule import Schedule
from fake_data_generation.generate_fake_data import FakeData

################################################################################
                        #Main function to run the alg#
################################################################################
def main(num_schedules: int, pop_size: int):
    """
    Function to run Nursing Placement Optimisation tool end-to-end
    :param num_schedules: the overall integer number of schedules to output
    from the tool. Can be thought of as number of times the tool is run
    :param pop_size: the size of the population to be used for each run. This
    is the integer number of schedules randomly produced for each run of the
    tool, which are used as the base to find the best performing schedule from
    
    :returns: A series of .xlsx files, which contain the schedules, as well as
    a comparison file which shows the scores of each schedule beside each other
    """
    st.subheader("Cycle information")
    st.subheader("Last saved schedule details")
    ui_schedule_results = st.empty()

    num_weeks = int(np.round((pd.to_datetime(
                dataload.student_placements["placement_start_date_raw"].max())
                - pd.to_datetime(
                  dataload.student_placements["placement_start_date_raw"].min()))
                / np.timedelta64(1, "W"), 0))

    # Add maximum placement length so that schedule is large enough to
    # accommodate even the longest placement
    num_weeks = (num_weeks
                 + int(dataload.student_placements["placement_len_weeks"].max())
                 + 1)

    slots, wards, placements = dataload.preprocData(num_weeks)

    num_iter = num_schedules
    scheduleCompare = []
    placeholder = st.empty()
    graph_placeholder = st.empty()
    for schedule in range(num_iter):
        GA = GeneticAlgorithm(slots, wards, placements, pop_size, num_weeks, schedule)
        GA.seed_schedules()
        (continue_eval, chosen_schedule, fitness, iteration,
         schedule_fitnesses, download_files) = GA.evaluate()
        # prev_fitness = 0
        while continue_eval:
            with placeholder.container():
                metric1, metric2, metric3 = st.columns(3)
                metric1.metric("Schedule # being generated", schedule + 1)
                metric2.metric("Current schedule version generating", iteration)
                metric3.metric("Highest schedule fitness score", np.round(fitness, 4))
                with graph_placeholder.container():
                    fig, ax = plt.subplots(figsize=(20, 5))
                    ax.hist(schedule_fitnesses, bins=100, color="#005EB8",
                            edgecolor="#003087")
                    ax.set_title("Distribution of Fitness Scores")
                    ax.set_ylabel("Count of Schedules")
                    ax.set_xlabel("Fitness Score")
                    ax.set_ylim([0, 35])
                    ax.set_xlim([0.3, 1])
                    fig.set_facecolor("#ececec")
                    ax.set_facecolor("#ececec")
                    st.pyplot(fig, clear_figure=True)
                    st.info("The above plot shows a histogram of fitness scores for schedules created by the algorithm. A score of 1 is the best possible score, while a score of 0 is the worst possible")
                (continue_eval, chosen_schedule, fitness, iteration,
                 schedule_fitnesses) = GA.evolve()
        viable = (chosen_schedule.file_name.split("-", maxsplit=10)[-1]
                  .replace(".xlsx", ""))
        schedule_scores = chosen_schedule.schedule_eval_scores
        quality_scores = chosen_schedule.quality_metrics
        scheduleCompare.append([chosen_schedule.file_name,
                                viable,
                                chosen_schedule.non_viable_reason,
                                iteration,
                                np.round(chosen_schedule.fitness, 4),
                                np.round(schedule_scores["mean_ward_util"], 2),
                                np.round(schedule_scores["mean_uniq_deps"], 2),
                                np.round(schedule_scores["mean_uniq_wards"], 2),
                                np.round(quality_scores["num_incorr_num_plac"], 2),
                                np.round(quality_scores["num_incorrect_length"], 2),
                                np.round(quality_scores["num_capacity_exceeded"], 2),
                                np.round(quality_scores["num_double_booked"], 2)])

        scheduleCompareDF = pd.DataFrame(scheduleCompare,
                                         columns=["Schedule file name",
                                                  "Viable schedule?",
                                                  "Non-viable reason",
                                                  "Number of iterations to generate",
                                                  "Schedule Fitness Score",
                                                  "Placement Utilisation score ",
                                                  "Unique Specialities Score",
                                                  "Unique Wards Score",
                                                  "No. students with incorrect no. of placements",
                                                  "No. of placements with the incorrect length",
                                                  "No. of ward-weeks where capacity is exceeded",
                                                  "No. of placements where student is double-booked"])
        scheduleCompareDF["Non-viable reason"] = scheduleCompareDF["Non-viable reason"].fillna("")
        ui_schedule_results.dataframe(scheduleCompareDF.style
                                    .highlight_max(axis=0, color="lightgreen"))
    script_directory = os.path.dirname(os.path.abspath(__file__))
    save_directory = os.path.join(script_directory, "results")
    try:
        os.makedirs(save_directory)
    except OSError:
        pass  # already exists

    now = datetime.now().strftime("%d-%m-%Y %H-%M")
    file_name = f"{now} schedule comparison.csv"
    #Create the comparison dataframe and add it as first in the list of download
    #files
    def convert_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")
    CompareDF = convert_to_csv(scheduleCompareDF)
    download_files = [(CompareDF, file_name)] + download_files

    #Create the download link for each of the created files
    st.header("Download Output Files")
    for file, file_name in download_files:
        download_link = Schedule.create_download_link(file, file_name)
        st.markdown(download_link, unsafe_allow_html=True)

    viableBool = False

    if scheduleCompareDF["Viable schedule?"].astype(bool).sum() > 0:
        viableBool = True
    return viableBool

################################################################################
                            #Generic page config#
################################################################################

#Page config, logo and title
st.set_page_config(page_title="Placement Optimisation",
                   page_icon="nhs_logo.png",
                   layout="wide",
                   initial_sidebar_state="auto")
col1, col2, col3 = st.columns([0.43,0.43,0.14])
with col3:
    st.image("docs/Uhp.png")
with col1:
    st.title("Nursing Placement Optimisation")


#Add information about the nurse scheduler and contact details if issues
OG_link = "https://github.com/nhsx/skunkworks-nursing-placement-schedule-optimisation"
UHPT_link = "https://github.com/Emily-OBrien-NHS/skunkworks-nursing-placement-schedule-optimisation"
DOWNLOAD_TEMPLATE_link = Schedule.create_download_link(
                         InputTemplate.create_input_template(),
                         "Input Template.xlsx")
#Add links to the original and UHPT githubs
st.markdown("This nuse placement tool is adapted from the NHS AI (Artificial "
            "Intelligence) Lab Skunkworks team's original scheduler for use at "
            "UHPT.  The original code repo can be [found here](%s). The UHPT "
            "adapted code repo for this app can be [found here](%s)."
            %(OG_link, UHPT_link))
#Add download link for input template.
st.markdown("You can download a blank excel input template here: %s"
            %DOWNLOAD_TEMPLATE_link, unsafe_allow_html=True)
#Add contact details
st.markdown("If you have any issues using this app, please first refer back to "
            "the user instructions and/or warning messages.  If you still have "
            "issues, please contact Emily O'Brien at e.obrien6@nhs.net")

#Add popovers for usage instructions and input file details.
#Use multiple columns to have these sat next to each other
col1, col2, empty = st.columns([0.15, 0.15, 0.7])
with col1:
    with st.popover("Usage Instructions"):
        f = open("README_usage_instructions.md", "r")
        st.markdown(f.read())
with col2:
    with st.popover("Input File Details"):
        f = open("README_input_columns.md", "r")
        st.markdown(f.read())

#Select box for which page to view - run algorithm, create student input sheet
# #or documentaion
page = st.selectbox("Choose your page",
            ["Run algorithm", "Create Student Input Sheet", "Documentation"])

################################################################################
                                #Run algorithm page#
################################################################################
if page == "Run algorithm":
    dataload = DataLoader()
    # Open the config params file to get some key arguments
    with open("config/params.yml") as f:
        params = yaml.load(f, Loader=yaml.FullLoader)
    # From the config file, read in the number of chromosomes (this is genetic
    # algorithm terminology for the size of the population, or in this case the
    # number of schedules being created to use to find the best solution)
    numberOfChromosomes = params["ui_params"]["numberOfChromosomes"]

    #Select wether using own or fake data
    file_source = st.selectbox("Select your data source",
                               ["Your own data", "Fake data"])
    
    #If fake data, create that data and use it
    if file_source == "Fake data":
        #create fake data
        fake_data = FakeData
        #add fake data download link
        st.markdown(fake_data.fake_data_download_link, unsafe_allow_html=True)
        #use this as the input file
        input_file = fake_data.fake_data_file
    #else use the file upload
    elif file_source == "Your own data":
        #User to upload input file
        input_file = st.file_uploader("Choose a file")
    #Once file hs been added, check file and run.
    if input_file is not None:
        #check the uploaded file has the correct sheets, to check if completely
        #wrong file is uploaded.
        df = pd.read_excel(input_file, sheet_name=None, nrows=0)
        if not {"students", "wards", "placements"}.issubset(set(df.keys())):
            st.error("Please upload the correct input file.")
        else:
            #If another error occurs when trying to read the data, give a
            # warning to the user to check they've uploaded the correct file.
            try:
                dataload.readData(input_file)
            except FileNotFoundError:
                st.error(f"Issue with uploaded file {input_file}, "
                         "is this the correct input file?")
            #Get the student start date
            student_placement_starts = min(
                        dataload.student_placements["placement_start_date_raw"])
            #If this is NaT, set to tomorrow.
            if pd.isnull(student_placement_starts):
                student_placement_starts = pd.to_datetime(datetime.now() + timedelta(days=1))
            #Get the placement end date
            student_placement_ends = max(
                dataload.student_placements["placement_start_date_raw"]
                + pd.to_timedelta(dataload
                          .student_placements["placement_len_weeks"], unit='w'))
            #if NaT, use tomorrow + max course length
            if pd.isnull(student_placement_ends):
                student_placement_ends =  pd.to_datetime(student_placement_starts
                    + timedelta(weeks=
                    int(dataload.uni_placements["placement_len_weeks"]
                    .max())))
            
            #add start and end date inputs
            start_date = st.date_input("Start Date",
                                       value=pd.to_datetime(
                                             student_placement_starts,
                                             format="%Y-%m-%d"))
            end_date = st.date_input("End Date",
                                     value=pd.to_datetime(
                                           student_placement_ends,
                                           format="%Y-%m-%d"))
            #show error if start date is before end
            if start_date >= end_date:
                st.error(f"Start date comes after or on the same day as the end "
                         "date, please correct before proceeding")
            if True:
                #else filter placements to between start and end.
                dataload.student_placements = (dataload.student_placements.loc[
                    (dataload.student_placements.placement_start_date_raw
                     >= pd.to_datetime(start_date))
                    &
                    (dataload.student_placements.placement_start_date_raw
                     < pd.to_datetime(end_date))])

                #Get user input for number of schedules
                schedule_num = st.empty()
                num_schedules = st.slider(
                                "Choose number of schedules to generate",
                                min_value=1, max_value=10, value=2, step=1,
                                help="Note that once you click the Run button "
                                "below, moving this slider again with cancel "
                                "the program")
                    
                #Flag if more students than placements
                st.header("Student and Capacity Counts")
                #Get the total number of students and the number of students in
                #each year group.
                student_counts = dataload.students["year"].value_counts()
                counts = [student_counts.sum()]
                for year in ["Year 1", "Year 2", "Year 3"]:
                    if year in student_counts.index:
                        counts.append(student_counts[year])
                    else:
                        counts.append(0)
                #Add the number of nursing associates
                no_nurs_asoc = len(dataload.students.loc[
                               dataload.students["qualification"].str.title()
                               .str.contains("Nursing Associate")])
                counts.append(no_nurs_asoc)
                #Get a dataframe of the wards overall and year group capacities
                ward_capacities = pd.DataFrame((dataload.ward_data[
                                ["capacity","P1_CAP", "P2_CAP", "P3_CAP",
                                 "Nurse_Assoc_CAP"]]
                                .rename(columns={"capacity":"Total",
                                                 "P1_CAP":"Year 1",
                                                 "P2_CAP":"Year 2",
                                                 "P3_CAP":"Year 3",
                                                 "Nurse_Assoc_CAP"
                                                  :"Nursing Associate"})).sum())
                #Add the student counts onto this table and rename columns.
                #Display table
                ward_capacities["Student Count"] = counts
                ward_capacities.columns = ["Ward Capacity", "Student Count"]
                st.dataframe(ward_capacities)
                #Check if there are too many students for capcity and flag to
                #the user
                too_many_students = (ward_capacities
                                     .loc[ward_capacities["Student Count"]
                                     > ward_capacities["Ward Capacity"]].copy())
                if len(too_many_students) > 0:
                    for group, row in too_many_students.iterrows():
                        ward_cap = row["Ward Capacity"]
                        no_stud = row["Student Count"]
                        group = group if group != "Total" else "all"
                        st.error(f"Not enough capacity for {group} students:  "
                                 f"there are {no_stud} students and only "
                                 f"{ward_cap} placements for {group} students. "
                                 "Not all students can be placed. Please "
                                 "increase ward capacities or remove "
                                 "additional students.")
                else:
                    st.info("Enough capacity for all students")

                #Flag any mismatched courses
                st.header("Mismatched Courses")
                student_cohorts = dataload.students[
                                  ["university",
                                   "qualification",
                                   "course_start",
                                   "student_cohort"]
                                   ].value_counts().reset_index()
                placement_cohorts = dataload.uni_placements[
                                    ["university",
                                     "qualification",
                                     "course_start",
                                     "student_cohort"]]
                cohorts = student_cohorts.merge(placement_cohorts,
                                            on="student_cohort",
                                            how="outer",
                                            suffixes=["_student", "_placement"])
                students_no_place = cohorts.loc[
                                    cohorts["university_placement"].isna(),
                                    ["university_student",
                                     "qualification_student",
                                     "course_start_student",
                                     "student_cohort",
                                     "count"]].copy()
                #Flag if there are students with no matching placement
                if len(students_no_place) > 0:
                    no_stud = int(students_no_place["count"].sum())
                    st.error(f"There are {no_stud} students on courses which "
                             "don't have a matching placement in the "
                             "placements tab. Please double check for any "
                             "typos, spelling errors, extra spaces or add "
                             "their course to the placements tab, otherwise "
                             "these students cannot be placed.")
                    for idx, row in students_no_place.iterrows():
                        students = (dataload.students.loc[
                                    dataload.students["student_cohort"]
                                    == row["student_cohort"],
                                    ["Forename", "Surname"]]
                                    .agg(" ".join, axis=1))
                        student_names = ", ".join(students.tolist())
                        st.warning(f"The below course is missng from the "
                                   "placemets tab, but has the following "
                                   f"students: {student_names}")
                        st.dataframe(pd.DataFrame(
                                {"University":row["university_student"],
                                "Qualification":row["qualification_student"],
                                "Course Start":row["course_start_student"]},
                                index=[""]))
                    
                place_no_stude = cohorts.loc[
                                 cohorts["university_student"].isna(),
                                 ["university_placement",
                                  "qualification_placement",
                                  "course_start_placement"]].copy()
                #Flage if there are any placements with no students (this is 
                #less of an issue)
                if len(place_no_stude):
                    #If there are placements with no students, flag these in
                    # #case there should be
                    st.error("The below courses are in the placements tab but "
                             "have no students. Please double check for any "
                             "typos, spelling errors or extra spaces if you "
                             "think there should be students on these courses. "
                             "otherwise the algorithm will ignore them.")
                    st.dataframe(place_no_stude)

                #If all courses match up, alert the user that its ok.
                if (len(students_no_place) == 0) and (len(place_no_stude) == 0):
                    st.info("All courses match between the Student and "
                            "Placment tabs")

                #Show which wards have expired or soon to expire audits
                st.header("Ward Audit Expiry")
                expire_wards = (dataload.ward_data.loc[
                                pd.to_datetime(
                                dataload.ward_data.education_audit_exp).dt.date
                                <= start_date, "Ward"])
                expire_wards_string = ", ".join(list(expire_wards))
                if len(expire_wards_string) > 0:
                    st.error(f"Be aware that the following wards have "
                             "Education Audits which expire on or before the "
                             "start date of your schedules:\n "
                             f"{expire_wards_string}")

                going_to_expire_wards = (dataload.ward_data.loc[
                                        (pd.to_datetime(
                                        dataload.ward_data.education_audit_exp
                                        ).dt.date <= end_date)
                                        &
                                        (pd.to_datetime(
                                        dataload.ward_data.education_audit_exp
                                        ).dt.date > start_date),
                                        "Ward"])
                going_to_expire_wards_string = ", ".join(
                                               list(going_to_expire_wards))

                if len(going_to_expire_wards_string) > 0:
                    st.warning(f"Additionally, be aware that the following "
                               "wards have Education Audits which expire on or "
                               "before the end date of your schedules:\n "
                               f"{going_to_expire_wards_string}")
                if ((len(expire_wards_string) == 0)
                    and (len(going_to_expire_wards_string) == 0)):
                    st.info("All ward audits are up to date")

                #Run the algorithm with the inputted datal
                run_button = st.empty()
                end_message = st.empty()
                if run_button.button("Click here to start running"):
                    viableBool = main(num_schedules, numberOfChromosomes)
                    if viableBool:
                        st.balloons()
                        end_message.success("Schedule production complete!")
                    else:
                        end_message.error("Schedule production complete, no "
                                          "viable schedules found")
    else:
        #If no file uploaded, prompt user to upload one.
        st.warning("you need to upload an excel file.")

################################################################################
                        #Create student input sheet page#
################################################################################
elif page == "Create Student Input Sheet":
    #Upload file
    uploaded_student_file = st.file_uploader("Choose a file")
    if uploaded_student_file is not None:
        #If a file is uploaded, check if it has the expected columns, if not
        #alert the user to upload the correct file
        df = pd.read_excel(uploaded_student_file)
        if  not ({"Intake", "Uni Number", "Surname", "Forename", "Driver"}
                 .issubset(set(df.columns))):
            st.error("Please upload the correct input file")
        else:
            try:
                #If correct columns, create the students sheet and provide
                #download link.
                create_inputs = StudentTab()
                student_tab = (create_inputs
                               .create_student_tab(uploaded_student_file))
                download_link = Schedule.create_download_link(student_tab,
                                                            "Student Tab.xlsx")
                st.markdown(download_link, unsafe_allow_html=True)
            except FileNotFoundError:
                st.error("Some issue in input file. Please ensure it follows "
                         "the correct format.")
    else:
        #Prompt user to upload a file
        st.warning("you need to upload an excel file.")

################################################################################
                            #Documentation page#
################################################################################
elif page == "Documentation":
    #Display documentation
    f = open("README_ui.md", "r")
    st.markdown(f.read())
