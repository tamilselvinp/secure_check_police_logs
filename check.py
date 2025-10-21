import mysql.connector.cursor
import pandas as pd
import mysql.connector
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

# Database connection

def new_connection():
    try:
        connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="pttv",
        database="policeledger")
        return mysql
    except mysql.connector.Error as e:
        st.error(f" connection Error: {e}")        
        return None   
        
    #Fetch data from database using Function

def fetch_data(query):
    connection=new_connection()
    if connection:
        try:    
            cursor=connection.cursor()
            cursor.execute(query)
            data=cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df=pd.DataFrame(data,columns=columns)
            return df
        finally:
            connection.close()
    else:
        return pd.DataFrame()

# Streamlit UI

st.set_page_config(page_title="SecureCheck - Police Post Logs", layout="wide")
st.title("🔒 SecureCheck: Police Post Log Ledger")
menu = st.sidebar.selectbox("Go to", ["Home","Data Analytics & Visuals","View Logs","Predict Logs"])

# Main page of securecheck and The Ledger view

if menu=='Home':    
    st.markdown("### 👮 Welcome to SecureCheck")
    st.write("This system is designed to maintain secure, tamper-proof digital records of police post activities.")
    st.header("📋Police Logs Overview")
    query="select * from Police_Post_Logs"
    data=fetch_data(query)
    st.dataframe(data,use_container_width=True)
    st.markdown("---")  
    st.subheader("📝 Description")
    st.markdown("""
    The above table displays daily police log entries including the type of incident, date, and location.
    - **Traffic Violation**: Involves breaches of traffic laws.
    - **Theft**: Refers to reported stolen property or unlawful entry.
    This data helps in identifying high-frequency incident zones and time patterns for better resource planning.
    """)

# Data Analytics and Visuals

elif menu=='Data Analytics & Visuals':

    # Quick Metrics

    query="select * from Police_Post_Logs"
    data=fetch_data(query)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_stops=data.shape[0]
        st.metric("Total Police Stops", total_stops)

    with col2:
            
        arrests = data[data["stop_outcome"].str.contains("arrest", case=False, na=False)].shape[0]
        st.metric("Total Arrests", arrests)

    with col3:
        warnings = data[data["stop_outcome"].str.contains("Warning", case=False, na=False)].shape[0]
        st.metric("Total Warnings", warnings)

    with col4:
        drug_stop = data[data["drugs_related_stop"] == 1].shape[0]
        st.metric("Drug Related Stops", drug_stop)
    
    # Data Visulaization Using Bar Chart

    st.header("📊 Visual Insights")      
    tab= st.tabs(['Stops By Violations', 'Driver Gender Distribution'])
    with tab[0]:

    # SQL Query to fetch violation and its counts

        query="select violation,count(violation) as counts from Police_Post_Logs group by violation"
        data=fetch_data(query)
        st.dataframe(data)

        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.bar(data['violation'], data['counts'], color='pink', width=0.5)
        ax.set_xlabel("Violation", fontsize=5)
        ax.set_ylabel("Number of Violations", fontsize=5)
        ax.set_title("Violation Frequency", fontsize=5)
        ax.tick_params(axis='x', rotation=45)
        ax.tick_params(axis='x', labelsize=4, rotation=45)
        ax.tick_params(axis='y', labelsize=4)
        st.pyplot(fig)

    with tab[1]:
         
    # SQL Query to fetch Gender of Driver and its counts

         query="select driver_gender, count(*) as count from Police_Post_Logs group by driver_gender"
         data=fetch_data(query)
         st.dataframe(data)

         fig, ax = plt.subplots(figsize=(4, 2.5)) 
         ax.bar(data['driver_gender'], data['count'], color='pink', width=0.5)
         ax.set_xlabel("Violation", fontsize=5)
         ax.set_ylabel("Number of Male and Female", fontsize=5)
         ax.set_title("Gender Distribution", fontsize=5)
         ax.tick_params(axis='x') 
         ax.tick_params(axis='x', labelsize=4)
         ax.tick_params(axis='y', labelsize=4)
         st.pyplot(fig)        

# View Logs

elif menu=='View Logs':

    st.header("🧠 Advanced Insights")

# Questions are added into selectbox

    selected_query=st.selectbox("select a Query to Run",[
    "Top 10 vehicle_number involved in drug_related stops",
    "Most frequently searched vehicle",
    "Driver age group had the highest arrest rate"  ,
    "Gender Distribution of Drivers stopped in each Country" ,
    "Time of day sees the most traffic stops",
    "Average stop duration for different violations"   ,
    "Highest search rate of race and gender combination",
    "Stops are during the night more likely to lead to arrests",
    "Which violations are most associated with searches or arrests",
    "Which violations are most common among younger drivers (<25)",
    "Is there a violation that rarely results in search or arrest",
    "Which countries report the highest rate of drug-related stops",
    "What is the arrest rate by country and violation",
    "Which country has the most stops with search conducted",
    "Yearly Breakdown of Stops and Arrests by Country ",
    "Driver Violation Trends Based on Age and Race",
    "Number of Stops by Year,Month, Hour of the Day",
    "Violations with High Search and Arrest Rates",
    "Driver Demographics by Country (Age, Gender, and Race)",
    "Top 5 Violations with Highest Arrest Rates" ]                      
    )
    query_map={
            "Top 10 vehicle_number involved in drug_related stops": "select vehicle_number from Police_Post_Logs where drugs_related_stop=1 order by vehicle_number desc limit 10",
            "Most frequently searched vehicle":"select vehicle_number, count(*) as count from Police_Post_Logs group by vehicle_number order by vehicle_number desc limit 1",
            "Driver age group had the highest arrest rate" : """select case
                                                            when driver_age between 18 and 25 then '18-25'
                                                            when driver_age between 26 and 35 then '26-35'
                                                            when driver_age between 36 and 45 then '36-45'
                                                            when driver_age between 45 and 60 then '45-60'
                                                            else '60+'
                                                            end as age_group,count(*) as total_driver,
                                                            sum(case when is_arrested=1 then 1 else 0 end) as total_arrests,
                                                            round(sum(case when is_arrested=1 then 1 else 0 end)*100.0/count(*),2) as arrest_rate_percent 
                                                            from Police_Post_Logs group by age_group
                                                            order by arrest_rate_percent desc limit 1""",
            "Gender Distribution of Drivers stopped in each Country" :"""select country_name,driver_gender,count(*) as total_gender,
                                                                        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY country_name), 2) AS gender_percent
                                                                        from Police_Post_Logs
                                                                        group by country_name,driver_gender
                                                                        order by country_name, driver_gender
                                                                        """,
            "Time of day sees the most traffic stops" : """select extract(hour from stop_time) as hour_of_day, count(*) as total_stops
                                                                        from Police_Post_Logs
                                                                        group by extract(hour from stop_time)
                                                                        order by total_stops desc
                                                                        limit 1""",
            "Average stop duration for different violations" :"""select violation, avg(stop_duration) as Average_of_stop_duration
                                                                from Police_Post_Logs
                                                                group by violation
                                                                order by violation
                                                                desc""" ,
            "Highest search rate of race and gender combination": """select driver_race,driver_gender, count(*) as total_gender,
                                                                    round(100.0* count(*)/ sum(count(*)) over (partition by driver_race),2) as gender_percent
                                                                    from Police_Post_Logs
                                                                    group by driver_race, driver_gender
                                                                    order by driver_race
                                                                    desc limit 2""",
            "Stops are during the night more likely to lead to arrests":"""select case
                                                                        when extract(hour from stop_time) between 20 and 23 or extract(hour from stop_time) between 0 and 5 then 'Night'
                                                                        else 'Day'
                                                                        end as time_of_day,
                                                                        count(*) as total_stops,
                                                                        sum(case when is_arrested=1 then 1 else 0 end) as total_arrests
                                                                        from Police_Post_Logs
                                                                        group by time_of_day
                                                                        order by time_of_day""",
            "Which violations are most associated with searches or arrests":"""select violation,count(*) as total_stops,
                                                                         sum(case when is_arrested=1 then 1 else 0 end) as total_arrests
                                                                         from Police_Post_Logs
                                                                         group by violation
                                                                         order by total_arrests
                                                                         desc limit 1""",
            "Which violations are most common among younger drivers (<25)" : """select violation,count(*) as total_stops,
                                                                        sum(case when driver_age <25 then 1 else 0 end) as number_of_driver_under_25
                                                                        from Police_Post_Logs
                                                                        group by violation
                                                                        order by number_of_driver_under_25
                                                                        desc limit 1""",
            "Is there a violation that rarely results in search or arrest": """select violation,count(*) as total_stops,
                                                                        sum(case when is_arrested=1 then 1 else 0 end) as total_arrests
                                                                         from Police_Post_Logs
                                                                         group by violation
                                                                         order by total_arrests
                                                                        asc limit 1
                                                                        """,
            "Which countries report the highest rate of drug-related stops":"""select country_name, count(*) as total_stops,
                                                                            sum(case when drugs_related_stop=1 then 1 else 0 end) as total_drug_related_stop,
                                                                            ROUND(100.0 * sum(case when drugs_related_stop=1 then 1 else 0 end)/ COUNT(*), 2) AS drug_stop_rate_percent
                                                                            from Police_Post_Logs
                                                                            group by country_name
                                                                            order by drug_stop_rate_percent
                                                                            desc limit 1""",
            "What is the arrest rate by country and violation": """ select country_name,count(*) as total_stops, violation,
                                                                    sum(case when is_arrested=1 then 1 else 0 end) as total_arrests,
                                                                    round(100.0*sum(case when is_arrested=1 then 1 else 0 end)/count(*),2) as total_arrest_percent
                                                                    from Police_Post_Logs
                                                                    group by country_name, violation
                                                                    order by country_name""",
            "Which country has the most stops with search conducted":"""select country_name, count(*) as total_stops
                                                                    from Police_Post_Logs 
                                                                    group by country_name
                                                                    order by total_stops
                                                                    desc limit 1""",
            "Yearly Breakdown of Stops and Arrests by Country " : """select year,country_name,total_stops,total_arrests
                                                                    from(select year,country_name,total_stops,total_arrests,
                                                                    sum(total_stops) over (partition by year) as yearly_total_stops,
                                                                    sum(total_arrests) over (partition by year) as yearly_total_arrests
                                                                    from 
                                                                    (select extract(year from stop_date) as year,country_name,count(*) as total_stops,
                                                                    sum(case when is_arrested=1 then 1 else 0 end)as total_arrests
                                                                    from Police_Post_Logs
                                                                    group by extract(year from stop_date), country_name) as agg_data
                                                                    ) as base_data
                                                                    order by year,country_name"""  ,
            "Driver Violation Trends Based on Age and Race" :  """select driver_age,driver_race,violation,count(*) as total_violation
                                                                  from
                                                                  (select case
                                                                   WHEN driver_age < 20 THEN '<20'
                                                                   WHEN driver_age BETWEEN 20 AND 29 THEN '20-29'
                                                                   WHEN driver_age BETWEEN 30 AND 39 THEN '30-39'
                                                                   WHEN driver_age BETWEEN 40 AND 49 THEN '40-49'
                                                                   WHEN driver_age >= 50 THEN '50+'
                                                                   END AS driver_age, driver_race,violation
                                                                   FROM Police_Post_Logs) AS grouped_data
                                                                   GROUP BY driver_age, driver_race, violation
                                                                   ORDER BY driver_age,driver_race, violation""",
            "Number of Stops by Year,Month, Hour of the Day": """select extract(year from stop_date) as year,
                                                                 extract(month from stop_date) as month,
                                                                 extract(hour from stop_time) as hour,
                                                                 count(*) as total_stops
                                                                 from Police_Post_Logs
                                                                 group by 
                                                                 extract(year from stop_date),
                                                                 extract(month from stop_date),
                                                                 extract(hour from stop_time)
                                                                 order by year,month,hour""" ,
            "Violations with High Search and Arrest Rates"  : """SELECT violation,total_stops,total_arrests,
                                                                 ROUND(100.0 * total_arrests / NULLIF(total_stops, 0), 2) AS arrest_rate_percent,
                                                                 RANK() OVER (ORDER BY ROUND(100.0 * total_arrests / NULLIF(total_stops, 0), 2) DESC) AS arrest_rate_rank
                                                                 from 
                                                                 (SELECT violation,COUNT(*) AS total_stops,
                                                                  COUNT(CASE WHEN is_arrested = 1 THEN 1 END) AS total_arrests
                                                                  FROM Police_Post_Logs
                                                                  GROUP BY violation
                                                                  ) AS agg
                                                                  ORDER BY arrest_rate_percent DESC
                                                                  """,
            "Driver Demographics by Country (Age, Gender, and Race)":""" SELECT country_name,driver_gender,driver_race,
                                                                    CASE 
                                                                    WHEN driver_age < 20 THEN '<20'
                                                                    WHEN driver_age BETWEEN 20 AND 29 THEN '20-29'
                                                                    WHEN driver_age BETWEEN 30 AND 39 THEN '30-39'
                                                                    WHEN driver_age BETWEEN 40 AND 49 THEN '40-49'
                                                                    WHEN driver_age BETWEEN 50 AND 59 THEN '50-59'
                                                                    ELSE '60+'
                                                                    END AS age_group,
                                                                    COUNT(*) AS total_drivers
                                                                    FROM Police_Post_Logs
                                                                    GROUP BY 
                                                                    country_name,driver_gender,driver_race, 
                                                                    CASE 
                                                                    WHEN driver_age < 20 THEN '<20'
                                                                    WHEN driver_age BETWEEN 20 AND 29 THEN '20-29'
                                                                    WHEN driver_age BETWEEN 30 AND 39 THEN '30-39'
                                                                    WHEN driver_age BETWEEN 40 AND 49 THEN '40-49'
                                                                    WHEN driver_age BETWEEN 50 AND 59 THEN '50-59'
                                                                    ELSE '60+'
                                                                    END 
                                                                    ORDER BY country_name, driver_gender, driver_race, age_group"""  ,
                                                                     
            "Top 5 Violations with Highest Arrest Rates" : """ select violation, count(*) as total_stops,
                                                               count(case when is_arrested=1 then 1 end) as total_arrests,
                                                               round(100.0*count(case when is_arrested=1 then 1 end)/nullif(count(*),0),2)as arrest_rate_percent
                                                               from Police_Post_Logs
                                                               group by violation
                                                               order by arrest_rate_percent desc
                                                               limit 5"""   }
    
# Answers are fetched From Database using functions

    result = pd.DataFrame()
    
    if st.button("Run Query"):
        result=fetch_data(query_map[selected_query])    
    if not result.empty:
            st.write(result)
    else:
            st.warning("No Results Found")

# Predict Logs

elif menu=="Predict Logs":
               
            query="select * from Police_Post_Logs"
            data=fetch_data(query)
            st.markdown("---")
            st.markdown("Built With ❤️ for Law Enforcement By SecureCheck")
            st.header("🔍 Custom Natural Language Filter")
            st.markdown("Fill in the details below to get a natural Language Prediction of the Stop outcome based on existing Data.")
            st.header("📝 Add New Police Log & Predict Outcome and violation")

     # Input Form

            with st.form("New_Log_Form"):

                stop_date=st.date_input("Stop Date")
                stop_time=st.time_input("Stop Time")
                country_name=st.text_input("Country Name")
                driver_gender=st.selectbox("Driver Gender",["Male","Female"])
                driver_age=st.number_input("Driver Age", min_value=16, max_value=100, value=20)
                driver_race=st.text_input("Driver Race")
                search_conducted=st.selectbox("Was a Search Conducted?", ["0","1"])
                search_type=st.text_input("Search Type")
                drugs_related_stop=st.selectbox("was it Drug Related?",["0",'1'])
                stop_duration=st.selectbox("Stop Duration",data["stop_duration"].dropna().unique())
                vehicle_number=st.text_input("Vehicle Number")
                submitted=st.form_submit_button("Predict Stop Outcome & Violation")
                
            if submitted:
                filtered_data=data[
                    (data["driver_gender"]== driver_gender)&
                    (data["driver_age"]== driver_age)&
                    (data["search_conducted"]==int(search_conducted))&
                    (data["stop_duration"]==stop_duration)&
                    (data["drugs_related_stop"]==drugs_related_stop)
                ]
         # Predict Stop_Outcome

                if not filtered_data.empty:
                    predicted_outcome=filtered_data["stop_outcome"].mode()[0]
                    predicted_violation=filtered_data["violation"].mode()[0]
                else:
                    predicted_outcome="Warning"  # Default
                    predicted_violation="Speeding" # Default

         # Natural Language Summary

                search_text="A search was conducted" if int(search_conducted) else "No search was conducted"
                drug_text="Was Drug related" if int(drugs_related_stop) else "was not Drug related"

                st.markdown(f"""
                            🚓 ** Prediction Summary**

                          -  **Predicted Violation:** {predicted_violation}
                            - **Predicted Stop Outcome:** {predicted_outcome}

                            📝 A {driver_age}-year-old {driver_gender} driver in {country_name} was stopped at {stop_time.strftime('%I:%M %p')} on {stop_date}.
                            {search_text}, and the stop {drug_text}.
                            stop duration: **{stop_duration}**
                            vehicle Number: **{vehicle_number}**.""" )  