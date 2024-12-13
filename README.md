# PrepGenie-Mock-Interviewer

https://github.com/user-attachments/assets/63f4112e-6acd-424b-adba-8c1805ad9512

Steps to run project-

1. Clone the repository
   Open a terminal and run:
   ```
 bash
   git clone https://github.com/samarth70/PrepGenie-Mock-Interviewer.git
   cd PrepGenie-Mock-Interviewer
   ```

2. Create a virtual environment
   ```	
   bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Firebase
   - Go to the Firebase Console (https://console.firebase.google.com/)
   - Create a new project or select an existing one
   - Enable Email/Password authentication in the Authentication section
   - Create a new web app in your Firebase project
   - Copy the Firebase configuration details

5. Configure Firebase in the app
   - Create a file named `.streamlit/secrets.toml` in the project root
   - Add your Firebase configuration:
 	```toml
 	[firebase]
 	apiKey = "your-api-key"
 	authDomain = "your-auth-domain"
 	projectId = "your-project-id"
 	storageBucket = "your-storage-bucket"
 	messagingSenderId = "your-messaging-sender-id"
 	appId = "your-app-id"
 	```

6. Set up Gemini Pro API
   - Sign up for an account and get your API key
   - Add the API key to `.streamlit/secrets.toml`:
 	```toml
 	[openai]
 	api_key = "GEMINI_API"
 	```

7. Run the Streamlit app
   ```bash
   cd "login module"
   streamlit run main.py
   ```
8. Access the app
   Open a web browser and go to the URL provided by Streamlit (usually http://localhost:8501)

**Remember to keep your API keys and Firebase configuration secure and never share them publicly.**


