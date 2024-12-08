import streamlit as st
from firebase_admin import auth
import os
import matplotlib.pyplot as plt
import google.generativeai as genai

# access the session state from start_interview.py
from start_interview import st

genai.configure(api_key="GEMINI_API")
text_model= genai.GenerativeModel("gemini-pro")



def getmetrics(interaction, resume):
    text = f"""This is the users resume: {resume}. 
    And here is the interaction of the interview: {interaction}. 
    Please evaluate the interview based on the interaction and the resume. 
    Rate me the following metrics on a scale of 1 to 10. 1 being the lowest and 10 being the highest. 
    Communication skills, Teamwork and collaboration, Problem-solving and critical thinking, 
    Time management and organization, Adaptability and resilience. just give the ratings for the metrics.
    I do not need the feedback.Just the ratings. No other text is required. just the ratings. 
    give me plain text not bold text."""

    response = text_model.generate_content(text)
    response.resolve()
    # st.write(response.text)
    return response.text

def default_metrics():
    return {
        "Communication skills": 0,
        "Teamwork and collaboration": 0,
        "Problem-solving and critical thinking": 0,
        "Time management and organization": 0,
        "Adaptability and resilience": 0
    }
def evaluate_app():
    # check if login
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''

    # if not login then go to login page
    if st.session_state.username == '':
        st.title('Welcome user to your :violet[Evaluation of Interview]')
        st.write('Evaluate your interview skills.')
        st.subheader('Please login to continue')
        st.subheader('You can login from the sidebar')
        return

    else:
        # goto start_interview.py
        st.title('Welcome ' + st.session_state["username"] + ' to your :violet[Evaluation of Interview]')
        # print the metrics from start_interview.py in sesssion state
        # st.write('Your interview has been evaluated')
        st.markdown('---')
        resume = st.session_state.resume

        metric = getmetrics(st.session_state.interaction, resume)
        metrics = {}
        for line in metric.split("\n"):
            key, value = line.split(":")
            metrics[key] = (value.strip())
        
        if not metric:
            return default_metrics()        
        
        for line in metric.split("\n"):
            if ":" in line:  # Check if line contains delimiter
                key, value = line.split(":", 1)  # Split on first occurrence only
                key = key.strip()
                value = value.strip()
                
                # Convert value to integer
                if value == 'N/A' or value == 'nan' or not value or value.isspace():
                    metrics[key] = 0
                else:
                    try:
                        metrics[key] = int(float(value))
                    except (ValueError, TypeError):
                        metrics[key] = 0
        
        # Ensure all required metrics exist
        required_metrics = [
            "Communication skills",
            "Teamwork and collaboration",
            "Problem-solving and critical thinking",
            "Time management and organization",
            "Adaptability and resilience"
        ]
        
        for metric in required_metrics:
            if metric not in metrics:
                metrics[metric] = 0
                
        st.write(metrics)

        # Calculate overall average rating
        average_rating = sum(metrics.values()) / len(metrics)

        # Option 1: Full width containers
        st.header("Hey " + st.session_state.username + ", we have evaluated your interview:")
        # Display metrics and progress bars
        for metric, rating in metrics.items():
            st.subheader(metric)
            st.write(f"Rating: {rating}")
            progress_bar_width = int(200 * rating / 10)
            st.markdown(f"<div style='background-color: lightblue; width: {progress_bar_width}px; height: 10px;'></div>", unsafe_allow_html=True)

        st.header("Stats:")
        if any(metrics.values()):

        # Create and display pie chart
            fig, ax = plt.subplots(figsize=(4, 4))  # Create a figure and axis object
            ax.pie(metrics.values(), labels=metrics.keys(), autopct="%1.1f%%")
            ax.axis("equal")  # Ensure the pie chart is a circle
            # Pass the figure object to st.pyplot()
            st.pyplot(fig, use_container_width=True)
        st.subheader(f"Overall average rating: {average_rating:.2f}")        
        st.markdown(st.session_state.feedback)
        st.markdown("---")
        st.write('You can see the interaction below:')
        st.write(st.session_state.interaction)
        # st.markdown('---')
        # st.success(st.session_state.feedback)