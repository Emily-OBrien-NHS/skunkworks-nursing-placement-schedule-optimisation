import logging

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    filename="log/nurse_opt_logging.log", filemode="w", level=logging.INFO
)

import streamlit as st
import pandas as pd
import numpy as np
from src.create_inputs import StudentTab
from src.data_load import DataLoader
from src.GeneticAlgorithm import GeneticAlgorithm
from src.Schedule import Schedule
from fake_data_generation.generate_fake_data import FakeData
import yaml
from datetime import datetime
import os
import matplotlib.pyplot as plt


def main(num_schedules: int, pop_size: int):
    """
    Function to run Nursing Placement Optimisation tool end-to-end
    :param num_schedules: the overall integer number of schedules to output from the tool. Can be otherwise thought of as number of times the tool is run
    :param pop_size: the size of the population to be used for each run. This is the integer number of schedules randomly produced for each run of the tool, which are used as the base to find the best performing schedule from
    
    :returns: A series of .xlsx files, stored in results/ which contain the schedules, as well as a comparison file which shows the scores of each schedule beside each other
    """

    st.info("Some useful information which may be of interest will be printed in the Command Line terminal and stored in log/nurse_opt_logging.log")
    st.subheader("Cycle information")
    st.subheader("Last saved schedule details")
    ui_schedule_results = st.empty()

    num_weeks = int(np.round((pd.to_datetime(
                dataload.student_placements["placement_start_date_raw"].max())
                - pd.to_datetime(
                  dataload.student_placements["placement_start_date_raw"].min()))
                / np.timedelta64(1, "W"), 0))

    #  Add maximum placement length so that schedule is large enough to accommodate even the longest placement
    num_weeks = (num_weeks
                 + int(dataload.student_placements["placement_len_weeks"].max())
                 + 1)

    logging.info(f"Total weeks covered: {num_weeks}")
    slots, wards, placements = dataload.preprocData(num_weeks)

    num_iter = num_schedules
    scheduleCompare = []
    placeholder = st.empty()
    graph_placeholder = st.empty()
    for i in range(num_iter):
        GA = GeneticAlgorithm(slots, wards, placements, pop_size, num_weeks)
        GA.seed_schedules()
        (continue_eval, chosen_schedule, fitness, iteration,
         schedule_fitnesses, download_files) = GA.evaluate()
        # prev_fitness = 0
        while continue_eval:
            with placeholder.container():
                metric1, metric2, metric3 = st.columns(3)
                metric1.metric("Schedule # being generated", i + 1)
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
        viable = (chosen_schedule.file_name.split("_", maxsplit=10)[9]
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
        logging.info(f"{chosen_schedule.file_name} generated")
        logging.info(scheduleCompareDF.dtypes)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    save_directory = os.path.join(script_directory, "results")
    try:
        os.makedirs(save_directory)
    except OSError:
        pass  # already exists

    now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    file_name = f"schedule_comparison_{now}.csv"
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

    logging.info("File download links created")
    viableBool = False
    logging.info(scheduleCompareDF.dtypes)
    if scheduleCompareDF["Viable schedule?"].astype(bool).sum() > 0:
        viableBool = True
    return viableBool

#Page config, logo and title
st.set_page_config(page_title="Placement Optimisation",
                   page_icon="nhs_logo.png",
                   layout="wide",
                   initial_sidebar_state="auto")
st.image("docs/Uhp.png")
st.title("Nursing Placement Optimisation")

link = "https://github.com/nhsx/skunkworks-nursing-placement-schedule-optimisation"
st.markdown("This nuse placement tool is adapted from the NHS AI (Artificial Intelligence) Lab Skunkworks team's original scheduler for use at UHPT.  The original code repo can be [found here](%s)"%link)

#Select box for algorithm/documentaion
page = st.selectbox("Choose your page", ["Run algorithm", "Create student input sheet", "Usage Instructions", "Documentation"])

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
    #If fake data read in that
    if file_source == "Fake data":
        try:
            fake_data = FakeData
            st.markdown(fake_data.fake_data_download_link, unsafe_allow_html=True)
            dataload.readData(fake_data.fake_data_file)
        except FileNotFoundError:
            logging.exception(f"No fake_data.xlsx file found in the data directory")
    #else use the file upload
    elif file_source == "Your own data":
        # From the config file, get the name of the file containing the input data
        uploaded_input_file = st.file_uploader("Choose a file")
        if uploaded_input_file is not None:
            try:
                dataload.readData(uploaded_input_file)
            except FileNotFoundError:
                logging.exception(f"Issue with uploaded file {uploaded_input_file}, is this the correct input file?")

            #Get the student start dates
            student_placement_starts = dataload.student_placements["placement_start_date_raw"]
            student_placement_ends = dataload.student_placements["placement_start_date_raw"] + pd.to_timedelta(dataload.student_placements["placement_len_weeks"], unit='w')
            #get start and end date
            start_date = st.date_input("Start Date",
                                    value=pd.to_datetime(min(student_placement_starts),
                                                            format="%Y-%m-%d"),)
            end_date = st.date_input("End Date",
                                    value=pd.to_datetime(max(student_placement_ends),
                                                        format="%Y-%m-%d"),)
            #show error if start date is before end, else filter placements to between
            #start and end.
            if start_date >= end_date:
                st.error(f"Start date comes after or on the same day as the end date, please correct before proceeding")
                logging.exception("Start date comes after or on the same day as the end date, please correct before proceeding")
            else:
                dataload.student_placements = dataload.student_placements[
                    (pd.to_datetime(dataload.student_placements.placement_start_date_raw
                                    ).dt.date >= start_date)
                    & (pd.to_datetime(dataload.student_placements.placement_start_date_raw
                                    ).dt.date < end_date)]
                #Get user input for number of schedules
                schedule_num = st.empty()
                num_schedules = st.slider("Choose number of schedules to generate",
                                        min_value=1, max_value=10, value=2, step=1,
                                        help="Note that once you click the Run button below, moving this slider again with cancel the program")
                
                #Table to flag if more students than placements
                st.header("Student and Capacity Counts")
                student_counts = dataload.students["year"].value_counts()
                counts = [student_counts.sum()]
                for year in ["Year 1", "Year 2", "Year 3"]:
                    if year in student_counts.index:
                        counts.append(student_counts[year])
                    else:
                        counts.append(0)
                
                ward_capacities = pd.DataFrame((dataload.ward_data[
                                ["capacity","P1_CAP", "P2_CAP", "P3_CAP"]]
                                .rename(columns={"capacity":"Total",
                                                    "P1_CAP":"Year 1",
                                                    "P2_CAP":"Year 2",
                                                    "P3_CAP":"Year 3"})).sum())
                ward_capacities["Student Count"] = counts
                ward_capacities.columns = ["Ward Capacity", "Student Count"]
                st.dataframe(ward_capacities)
                too_many_students = ward_capacities.loc[ward_capacities["Student Count"]
                                            > ward_capacities["Ward Capacity"]].copy()
                if len(too_many_students) > 0:
                    for group, row in too_many_students.iterrows():
                        ward_cap = row["Ward Capacity"]
                        no_stud = row["Student Count"]
                        group = group if group != "Total" else "all"
                        st.error(f"Not enough capacity for {group} students:  there are {no_stud} students and only {ward_cap} placements for {group} students.  Not all students can be placed.")
                else:
                    st.info("Enough capacity for all students")

                #Flag any mismatched courses
                st.header("Mismatched Courses")
                student_cohorts = dataload.students[
                                ["university", "qualification", "course_start",
                                "student_cohort"]].value_counts().reset_index()
                placement_cohorts = dataload.uni_placements[
                                    ["university", "qualification", "course_start",
                                    "student_cohort"]]
                cohorts = student_cohorts.merge(placement_cohorts, on="student_cohort",
                                    how="outer", suffixes=["_student", "_placement"])
                students_no_place = cohorts.loc[cohorts["university_placement"].isna(),
                                    ["university_student", "qualification_student",
                                    "course_start_student", "student_cohort",
                                    "count"]].copy()
                if len(students_no_place) > 0:
                    #If students on a course with no matching placement.
                    no_stud = int(students_no_place["count"].sum())
                    st.error(f"There are {no_stud} students on courses which don't have a matching placement in the placements tab. Please double check for any typos, spelling errors, extra spaces or add their course to the placements tab, otherwise these students cannot be placed.")
                    for idx, row in students_no_place.iterrows():
                        students = dataload.students.loc[
                        dataload.students["student_cohort"] == row["student_cohort"],
                        ["Forename", "Surname"]].agg(" ".join, axis=1)
                        student_names = ", ".join(students.tolist())
                        st.warning(f"The below course is missng from the placemets tab, but has the following students: {student_names}")
                        st.dataframe(pd.DataFrame(
                            {"University":row["university_student"],
                            "Qualification":row["qualification_student"],
                            "Course Start":row["course_start_student"]}, index=[""]))
                
                place_no_stude = cohorts.loc[cohorts["university_student"].isna(),
                                    ["university_placement", "qualification_placement",
                                    "course_start_placement"]].copy()
                if len(place_no_stude):
                    #If there are placements with no students, flag these in case there should be
                    st.error("The below courses are in the placements tab but have no students. Please double check for any typos, spelling errors or extra spaces if you believe there should be students on these courses:")
                    st.dataframe(place_no_stude)

                if (len(students_no_place) == 0) and (len(place_no_stude) == 0):
                    st.info("All courses match between the Student and Placment tabs")

                #Show which wards have expired or soon to expire audits
                st.header("Ward Audit Expiry")
                expire_wards_string = ""
                expire_wards = dataload.ward_data.loc[
                    pd.to_datetime(dataload.ward_data.education_audit_exp).dt.date
                    <= start_date, "Ward"]
                for item in list(expire_wards):
                    expire_wards_string = expire_wards_string + item + ", "

                going_to_expire_wards_string = ""
                going_to_expire_wards = dataload.ward_data.loc[
                    (pd.to_datetime(dataload.ward_data.education_audit_exp).dt.date
                    <= end_date)
                    & (pd.to_datetime(dataload.ward_data.education_audit_exp).dt.date
                    > start_date), "Ward"]
                for item in list(going_to_expire_wards):
                    going_to_expire_wards_string = going_to_expire_wards_string + item + ", "

                if len(expire_wards_string) > 0:
                    st.error(f"Be aware that the following wards have Education Audits which expire on or before the start date of your schedules:\n {expire_wards_string}")
                    logging.warning(f"Be aware that the following wards have Education Audits which expire on or before the start date of your schedules: {expire_wards_string}")
                if len(going_to_expire_wards_string) > 0:
                    st.warning(f"Additionally, be aware that the following wards have Education Audits which expire on or before the end date of your schedules:\n {going_to_expire_wards_string}")
                    logging.warning(f"Additionally, be aware that the following wards have Education Audits which expire on or before the end date of your schedules: {going_to_expire_wards_string}")
                if (len(expire_wards_string) == 0) and (len(going_to_expire_wards_string) == 0):
                    st.info("All ward audits are up to date")

                run_button = st.empty()
                end_message = st.empty()
                if run_button.button("Click here to start running"):
                    viableBool = main(num_schedules, numberOfChromosomes)
                    if viableBool:
                        st.balloons()
                        end_message.success("Schedule production complete!")
                    else:
                        end_message.error("Schedule production complete, no viable schedules found")
                ########################REMOVE FOR STREAMLIT!!!!!!!!!!!!!!!!!!!!!!!!!!!
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                #viableBool = main(num_schedules, numberOfChromosomes)
        else:
            st.warning("you need to upload an excel file.")
        

elif page == "Create student input sheet":
    uploaded_student_file = st.file_uploader("Choose a file")
    if uploaded_student_file is not None:
        try:
            create_inputs = StudentTab()
            student_tab = create_inputs.create_student_tab(uploaded_student_file)
            download_link = Schedule.create_download_link(student_tab, "Student Tab.xlsx")
            st.markdown(download_link, unsafe_allow_html=True)
        except FileNotFoundError:
            st.error("Some issue in input file. Please ensure it follows the correct format.")
            logging.exception(f"No file found by the name {uploaded_student_file} in the data directory")
    else:
        st.warning("you need to upload an excel file.")

elif page == "Usage Instructions":
    f = open("README_usage_instructions.md", "r")
    st.markdown(f.read())

elif page == "Documentation":
    f = open("README_ui.md", "r")
    st.markdown(f.read())
