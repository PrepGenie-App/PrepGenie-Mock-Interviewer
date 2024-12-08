import streamlit as st
from firebase_admin import auth
import PyPDF2
import os
import google.generativeai as genai
import tensorflow as tf
from transformers import BertTokenizer, TFBertModel
import numpy as np
import math
import speech_recognition as sr
import evaluate
import pyttsx3
from gtts import gTTS
from io import BytesIO
import pygame
import time

from dotenv import load_dotenv
load_dotenv()
st.session_state.interaction = {}
st.session_state.feedback = []
st.session_state.resume = ""
genai.configure(api_key="GEMINI_API")
text_model= genai.GenerativeModel("gemini-pro")
# Load the pre-trained BERT model
model = TFBertModel.from_pretrained("bert-base-uncased")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


def getallinfo(data):
    text = f"""{data} is given by the user. Make sure you are getting the details like name, experience, 
            education, skills of the user like in a resume. If the details are not provided return: not a resume. 
            If details are provided then please try again and format the whole in a single paragraph covering all the information. """
    response = text_model.generate_content(text)
    # st.write(response)
    response.resolve()
    return response.text

def file_processing(uploaded_file):
    # upload pdf of resume
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to preprocess text and get embeddings
def get_embedding(text):
    encoded_text = tokenizer(text, return_tensors="tf")
    output = model(encoded_text)
    embedding = output.last_hidden_state[:, 0, :]
    return embedding


def generate_feedback(question, answer):
    # Ensure correct variable name (case-sensitive)
    question_embedding = get_embedding(question)
    answer_embedding = get_embedding(answer)

    # Enable NumPy-like behavior for transpose
    tf.experimental.numpy.experimental_enable_numpy_behavior()

    # Calculate similarity score (cosine similarity)
    similarity_score = np.dot(question_embedding, answer_embedding.T) / (np.linalg.norm(question_embedding) * np.linalg.norm(answer_embedding))

    # Generate basic feedback based on similarity score
    corrected_string = f"Feedback: {np.array2string(similarity_score, precision=2)}"
    # print(corrected_string)
    return np.array2string(similarity_score, precision=2)

def generate_questions(roles, data):
    questions = []
    text = f"""If this is not a resume then return text uploaded pdf is not a resume. this is a resume overview of the candidate. 
            The candidate details are in {data}. The candidate has applied for the role of {roles}. 
            Generate questions for the candidate based on the role applied and on the Resume of the candidate. 
            Not always necceassary to ask only technical questions related to the role but the logic of question 
            should include the job applied for because there might be some deep tech questions which the user might not know.
            Ask some personal questions too.Ask no additional questions. Dont categorize the questions. 
            ask 2 questions only. directly ask the questions not anything else. 
            Also ask the questions in a polite way. Ask the questions in a way that the candidate can understand the question. 
            and make sure the questions are related to these metrics: Communication skills, Teamwork and collaboration, 
            Problem-solving and critical thinking, Time management and organization, Adaptability and resilience. dont 
            tell anything else just give me the questions. if there is a limit in no of questions, ask or try questions that covers 
            all need."""
    # if needed ask multiple questions. but ask one question at a time only and note more than 7. 
    response = text_model.generate_content(text)
    response.resolve()
    # slipt the response into questions either by \n or by ? or by . or by !
    questions = response.text.split("\n")
    
    return questions


# def generate_overall_feedback(data, percent, answer, questions):
#     test = f"""Here is the overview of the candidate {data}. Be just like a interviewer you 
#             need to give a feedback about the process. In the interview the questions asked were {questions}. 
#             The candidate has answered the questions as follows: {answer}.If the answer is empty or meaningless to the question, 
#             give it a rating from 0-2.Based on the answers provided,the candidate has scored {percent}. dont tell the percent of the
#             candidate, but rate them on 10 based on their answers. 
#             Make sure the answers are making sense and dont say over good on feedback you are interviewer, but make sure you are 
#             talking point to point. If the logic behind the answer is not provided in a good way, directly tell the candidate the 
#             point to point answer was not provided. then tell the important mistakes candidate made and how to improve it.
#             The candidate has scored {percent} in the interview. If the candidate has answered the questions well and has a good 
#             understanding of the concepts.The candidate has scored well in the interview. If the answers are not good then tell 
#             the candidate has to improve alot with the answers.Give me 2 paragraphs of feedback. 1st para about how was the interview and 2nd para about how the candidate can improve. dont fake. 
#             just write about what answer was given by the candidate. dont write anything else. just the feedback."""
#     # st.write(test)
#     response = text_model.generate_content(test)
#     response.resolve()
#     return response.text

def generate_overall_feedback(data, percent, answer, questions):
    prompt = f"""As an interviewer, provide concise feedback (max 150 words) for candidate {data}.
    Questions asked: {questions}
    Candidate's answers: {answer}
    Score: {percent}

    Feedback should include:
    1. Overall performance assessment (2-3 sentences)
    2. Key strengths (2-3 points)
    3. Areas for improvement (2-3 points)

    Be honest and constructive. Do not mention the exact score, but rate the candidate out of 10 based on their answers."""

    response = text_model.generate_content(prompt)
    response.resolve()
    return response.text


'''def store_audio_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # 2 columns
        col1, col2 = st.columns([10,10])
        with col1:
            time.sleep(15)
            st.error("Speak now")
        # with col2:
        #     st.button("stop recording", on_click=stop_recording)
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            # st.success(f"Your Answer: {text}")
            return text
        except:
            st.error("Sorry could not recognize your voice")
            return " "
'''

def store_audio_text():
    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True
    r.pause_threshold = 3
    with sr.Microphone() as source:
        with st.container():
            interviewer_msg = st.empty()
            status = st.empty()
            
            # Preparation phase
            for remaining in range(3, 0, -1):
                interviewer_msg.info("Please take a moment to gather your thoughts...")
                time.sleep(3)
            
            # Interview phase
            interviewer_msg.info("Please go ahead with your response...")
            
            try:
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source,timeout=380, phrase_time_limit=200)
                interviewer_msg.empty()
                
                with st.spinner("Thank you, let me note that down..."):
                    text = r.recognize_google(audio)
                if text:
                    st.info("Thank you for your response.")
                    return text
                    
            except sr.WaitTimeoutError:
                st.info("I noticed you're taking some time. Would you like to try answering again?")
                return " "
            except sr.RequestError:
                st.info("I apologize, but I couldn't hear that clearly. Could you please repeat your answer?")
                return " "
            except:
                st.info("I'm sorry, but I couldn't catch that.")
                return " "


# import streamlit as st
# from streamlit.components.v1 import html

# def store_audio_text():
#     r = sr.Recognizer()
#     r.energy_threshold = 300
#     r.dynamic_energy_threshold = True
#     r.pause_threshold = 3
#     with sr.Microphone() as source:
#         with st.container():
#             interviewer_msg = st.empty()
#             status = st.empty()

#             # Preparation phase
#             for remaining in range(3, 0, -1):
#                 interviewer_msg.info("Please take a moment to gather your thoughts...")
#                 time.sleep(3)

#             # Display countdown timer
#             countdown_html = """
#                 <div id="timer-container" style="font-size: 20px; font-weight: bold;">
#                     <span id="time">05:00</span>
#                 </div>
                
#                 <script>
#                     function startTimer(duration) {
#                         var display = document.querySelector('#time');
#                         var timer = duration;
#                         var minutes, seconds;
                        
#                         var countdown = setInterval(function () {
#                             minutes = parseInt(timer / 60, 10);
#                             seconds = parseInt(timer % 60, 10);

#                             minutes = minutes < 10 ? "0" + minutes : minutes;
#                             seconds = seconds < 10 ? "0" + seconds : seconds;

#                             display.textContent = minutes + ":" + seconds;

#                             if (--timer < 0) {
#                                 clearInterval(countdown);
#                                 display.parentElement.style.display = 'none';
#                             }
#                         }, 1000);
                        
#                         return countdown;
#                     }
                    
#                     // Start timer immediately without waiting for window.onload
#                     var fiveMinutes = 60 * 5;
#                     var countdownId = startTimer(fiveMinutes);
#                 </script>
#                 """

#             # Create a container for the timer
#             timer_container = st.empty()
#             timer_container.html(countdown_html)
#             # html(countdown_html)

#             # Interview phase
#             interviewer_msg.info("Please go ahead with your response...")

#             try:
#                 r.adjust_for_ambient_noise(source, duration=1)
#                 audio = r.listen(source, timeout=350, phrase_time_limit=200)
#                 interviewer_msg.empty()

#                 with st.spinner("Thank you, let me note that down..."):
#                     text = r.recognize_google(audio)
#                 if text:
#                     timer_container.empty()
#                     st.info("Thank you for your response.")
#                     return text

#             except sr.WaitTimeoutError:
#                 st.info("I noticed you're taking some time. Would you like to try answering again?")
#                 return " "
#             except sr.RequestError:
#                 st.info("I apologize, but I couldn't hear that clearly. Could you please repeat your answer?")
#                 return " "
#             except:
#                 st.info("I'm sorry, but I couldn't catch that.")
#                 return " "
        
# def stop_recording():
#     r = sr.Recognizer()
#     with sr.Microphone() as source:
#         r.adjust_for_ambient_noise(source)
#         st.error("Recording stopped")
#         return    


def speak(text, language='en'):
    mp3_fo = BytesIO()
    tts = gTTS(text=text, lang=language)
    tts.write_to_fp(mp3_fo)
    return mp3_fo

    
        
def generate_metrics(data, answer, question):
    metrics = []
    text = f"""Here is the overview of the candidate {data}. In the interview the question asked was {question}. 
    The candidate has answered the question as follows: {answer}. Based on the answers provided, give me the metrics related to: 
    Communication skills, Teamwork and collaboration, Problem-solving and critical thinking, Time management and organization,
    Adaptability and resilience.
    
    Rules for rating:
    - Rate each skill from 0 to 10
    - If the answer is empty, 'Sorry could not recognize your voice', meaningless, or irrelevant: rate all skills as 0
    - Only provide numeric ratings without any additional text or '/10'
    - Ratings must reflect actual content quality - do not give courtesy points
    - Consider answer relevance to the specific skill being rated
    
    Format:
    Communication skills: [rating]
    Teamwork and collaboration: [rating]  
    Problem-solving and critical thinking: [rating]
    Time management and organization: [rating]
    Adaptability and resilience: [rating]"""

    response = text_model.generate_content(text)
    # response.resolve()
    metrics.append(response.text)
    return metrics
  






def user_interview():
    ttts = pyttsx3.init()
    st.title('Welcome to Mock Interview ' + st.session_state["username"] + '\n :violet[Good luck]')


    st.write("Welcome to the mock interview app. This app will help you prepare for your next interview.You can practice your responses to common interview questions and receive feedback on your responses.")

    # check if login
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''

    # if user is not logged in then go to login page
    if st.session_state.username == '':
        st.title('Welcome to your :violet[Mock Interview]')
        st.write('This is a mock interview app')
        st.write('Here you can give a mock interview and get feedback on your performance.')
        st.subheader('Please login to continue')
        st.subheader('You can login from the sidebar')
        return
    
    else:   
        # logged in
        pygame.init()
        pygame.mixer.init()

        uploaded_file = st.file_uploader("Upload your resume in simple Document Format", type=["pdf"])
        roles_applied = []
        if uploaded_file is not None:
            st.write("File uploaded successfully!")
            data = file_processing(uploaded_file)

            # st.write(data)
            # st.write(getallinfo(data))
            updated_data = getallinfo(data)
            st.session_state.resume = updated_data
            roles = st.multiselect("Select your job role:", ["Data Scientist", "Software Engineer", "Product Manager", "Data Analyst", "Business Analyst"])
            if st.button("Next"):
                if roles:
                    roles_applied.append(roles)
                    st.write(f"Selected roles: {roles}")
                    questions = generate_questions(roles, updated_data)
                    print(questions)
                    feedback = []
                    answers = []
                    ans = ""
                    interaction = {}
                    metrics = []
                    st.write("Please wait for the questions to load (this may take a few seconds)")
                    time.sleep(3)
                    for i in range(len(questions)):
                        st.write(questions[i])
                        ans = store_audio_text()
                        # st.button("stop recording", on_click=stop_recording)
                        # st.success(ans)                        
                        answers.append(ans)
                        percent = 0.0
                        # time.sleep(2)
                        percent = generate_feedback(questions[i], answers[i])
                        print(percent)
                        feedback.append(generate_overall_feedback(data, percent, answers[i], questions[i]))
                        metrics.append(generate_metrics(data, answers[i], questions[i]))
                        # store the interaction into a dictionary
                        interaction["Question "+ questions[i]+":"] = "Answer by user: "+ answers[i]
                        st.session_state.feedback = feedback
                        st.session_state.interaction = interaction
                    print(st.session_state.interaction)
                    print(metrics)
                    # st.markdown(feedback)
                    # print(feedback)
                    st.button("Submit", on_click=evaluate.evaluate_app)
                    st.stop()
                

            else:
                st.write("Please confirm a role to continue")
                return
        else:
            st.write("Please upload your resume to continue")
            return
                    
