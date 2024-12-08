import tempfile
import streamlit as st
from firebase_admin import auth
import PyPDF2
import google.generativeai as genai
import os
import base64

import start_interview as i, evaluate

genai.configure(api_key="GEMINI_API")
text_model= genai.GenerativeModel("gemini-pro")

# if 'history' not in st.session_state:
#     st.session_state.history['Question'] = 'Answer'

st.session_state.history = {}
print(st.session_state.history)


def display_PDF(file):
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)


def get_answer(question, input_text):
    text=f"""You are a Great Resume Checker, you are given the details about the user and the user 
            needs some changes about their resume and you are the one to guide them. 
            There are queries which user wants to be solved about their resume. You are asked a question which is: " + {question} + " and 
            you have to generate suggestions to improve the resume based on thr text: " + {input_text} + ". Answer in a way that the user 
            can understand and make the changes in their resume. and In paragraph form. maximum of 2 paragraphs. dont tell over the top. 
            it should be less and precise. dont tell the user to change the whole resume. just give them some suggestions. dont give 
            bullet points. Be point to point with user."""
    # text="""You are an exceptional Resume Advisor tasked with helping users refine their resumes. 
            # The user has a specific query: {question}, and has provided the following resume content for review: {input_text}.
            # Your role is to analyze the content and provide precise, actionable suggestions in paragraph form (maximum of 2 paragraphs).
            #  Focus on areas that directly address the user's query, suggesting small but impactful improvements. Avoid suggesting complete
            #  rewrites or overly elaborate changes. Respond in a way that is clear and easy for the user to understand, enabling them to 
            # make the adjustments effectively"""
    response = text_model.generate_content(text)
    response.resolve()
    return response.text

# text2="""You are a professional resume counselor. When a user presents you with a resume-related question and the current text of their resume, your role is to provide thoughtful, constructive feedback to help the user improve their resume.
# The key principles you should follow are:

# Provide suggestions in a helpful, encouraging tone. Avoid sounding overly critical or demanding that the user completely overhaul their resume.
# Focus on 2-3 specific areas for improvement based on the user's question and the resume text provided. Do not try to address every possible issue.
# Explain your suggestions in paragraph form, using clear language that the user can easily understand and implement. Bullet points should be avoided.
# Be mindful not to overwhelm the user. Keep your feedback concise, with a maximum of 2 paragraphs.
# Tailor your advice to directly address the user's stated question or concerns. Do not provide generic, one-size-fits-all resume tips.
# If the user's resume is generally strong and only requires minor tweaks, say so. Do not insist on major changes unless they are truly necessary.
# Overall, position yourself as a collaborative partner who wants to help the user elevate their resume, not as an authoritative judge critiquing their work. When a user asks: "+ question +" and provides the resume text: "+ input_text +", respond with thoughtful, constructive feedback formatted as described above."""

def chat_app():
    # check if login
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''
    if 'history' not in st.session_state:
        st.session_state.history = {}

    # if user is not logged in then go to login page
    if st.session_state.username == '':
        st.title('Welcome to your :violet[Chat with PDF]')
        st.write('This is a chat app')
        st.write('Here you can upload your PDF and get to know about changes in your resume (if required).')
        st.write('You can also chat with our AI for any queries.')
        st.subheader('Please login to continue')
        st.subheader('You can login from the sidebar')
        return
    
    else:   
        # st.write('You are logged in as: '+st.session_state['username'])
        st.title('Welcome ' + st.session_state["username"] + ' to your :violet[Chat with Resume]')
        st.write('This is a chat app')
        st.write('Here you can upload your PDF and get to know about changes in your resume (if required).')
        # st.write('You can also chat with our AI for any queries.')
        uploaded_file = st.file_uploader("Choose a file", type=['pdf'])
        if uploaded_file is not None:
            file_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
            # st.write(uploaded_file)
            ##Save the uploaded file to the defined path 
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            text = i.file_processing(uploaded_file)
            # st.write(text)
            # st.write(i.getallinfo(text))
            text = i.getallinfo(text)
            st.write('Your resume has been processed')
            st.write('You can chat with our AI for any queries')
            st.markdown('---')
            # print(text)
            # print('---')
            # print(file_path)
            display_PDF(file_path)
            query = st.text_area('Chat with AI', placeholder='Type here', height=50, max_chars=None, key=None) 
            # value to label  
            if st.button('Send'):
                answer = get_answer(question=query, input_text=text)
                st.write('AI: ' + answer)
                if 'history' not in st.session_state:
                    st.session_state.history = {}
                st.session_state.history["Question: " + query] = "Answer: " + answer
            st.markdown('---')
            st.write('History of chat with AI')
            st.write(st.session_state.history)
            print(st.session_state.history)

            

        else:
            st.write('Please upload a file')
        return