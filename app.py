from flask import Flask, render_template, request, jsonify, session
import cohere
import os
from datetime import datetime, timezone
import base64
from gtts import gTTS
import tempfile
# from pydub import AudioSegment  # Commenting out problematic import
import cv2
import time
import numpy as np
import re
import json
import logging
from logging.handlers import RotatingFileHandler
import requests
from xhtml2pdf import pisa
from io import BytesIO


def html_to_pdf(html_content):
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=result)
    if pisa_status.err:
        return None
    return result.getvalue()





app = Flask(__name__)
DJANGO_API_URL = "https://ibot-backend.onrender.com/jobs/interview/" 


# @app.route('/jobs/interview/<token>/')
# def interview(token):
#     try:
#         # Call your Django API to get interview data
#         response = requests.get(f"{DJANGO_API_URL}{token}/")
#         print(f"🔍 Requesting interview data from: {DJANGO_API_URL}{token}/")

#         if response.status_code == 200:
#             data = response.json()
#             print("✅ Data received from Django:", data)  # Debug print
#             jd_text = data.get('jd_text', '')
#             resume_text = data.get('resume_text', '')

#             session['jd_text'] = jd_text
#             session['resume_text'] = resume_text


#             return render_template("index.html", data=data)
#         else:
#             return render_template("error.html", message="Invalid or expired interview link."), 404
#     except Exception as e:
#         print("❌ Error while contacting Django:", str(e))
#         return render_template("error.html", message="Server error while retrieving interview data."), 500





app.secret_key = 'your-secret-key-here'
# app.config['PERMANENT_SESSION_LIFETIME'] = 10600
from flask_session import Session

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'session'
# Set safe path for session file storage
session_dir = os.path.join(os.getcwd(), 'flask_session_data')
os.makedirs(session_dir, exist_ok=True)
app.config['SESSION_FILE_DIR'] = session_dir
Session(app)





# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('interview_app.log', maxBytes=10000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Cohere API Configuration
cohere_api_key = "FQP7SbVZ7Z6G4LwmmO62HfHdpCpHzkmFbHF5PtHW"
co = cohere.Client(cohere_api_key)


# Configuration
MAX_FRAME_SIZE = 500
FRAME_CAPTURE_INTERVAL = 5
MAX_RECORDING_DURATION = 520
PAUSE_THRESHOLD = 40
FOLLOW_UP_PROBABILITY = 0.8
MIN_FOLLOW_UPS = 1
MAX_FOLLOW_UPS = 2  # Exactly 2 follow-ups per question
CONVERSATION_FILE = "interview_conversation.txt"

def init_interview_data():
    logger.debug("Initializing new interview data structure")
    # Clear previous conversation file
    if os.path.exists(CONVERSATION_FILE):
        os.remove(CONVERSATION_FILE)
    return {
        "questions": [],
        "answers": [],
        "ratings": [],
        "current_question": 0,
        "interview_started": False,
        "conversation_history": [],
        "role": "",
        "experience_level": "",
        "years_experience": 0,
        "start_time": None,
        "end_time": None,
        "visual_feedback": [],
        "last_frame_time": 0,
        "last_activity_time": None,
        "follow_up_questions": [],
        "current_topic": None,
        "follow_up_count": 0,
        "current_context": "",
        "question_topics": [],
        "used_questions": [],
        "used_follow_ups": []
    }

def save_conversation_to_file(conversation_data):
    try:
        with open(CONVERSATION_FILE, "a") as f:
            for item in conversation_data:
                if 'speaker' in item:
                    f.write(f"{item['speaker']}: {item['text']}\n")
                elif 'question' in item:
                    f.write(f"Question: {item['question']}\n")
        logger.debug("Conversation saved to file")
    except Exception as e:
        logger.error(f"Error saving conversation to file: {str(e)}", exc_info=True)

def load_conversation_from_file():
    try:
        if not os.path.exists(CONVERSATION_FILE):
            return []
        
        with open(CONVERSATION_FILE, "r") as f:
            lines = f.readlines()
        
        conversation = []
        for line in lines:
            if line.startswith("bot:") or line.startswith("user:"):
                speaker, text = line.split(":", 1)
                conversation.append({"speaker": speaker.strip(), "text": text.strip()})
            elif line.startswith("Question:"):
                question = line.split(":", 1)[1].strip()
                conversation.append({"question": question})
        
        return conversation
    except Exception as e:
        logger.error(f"Error loading conversation from file: {str(e)}", exc_info=True)
        return []




@app.before_request
def before_request():
    logger.debug(f"Before request - path: {request.path}, method: {request.method}")
    if 'interview_data' not in session:
        logger.debug("No interview data in session, initializing new data")
        session['interview_data'] = init_interview_data()
    session.permanent = True


username_extrnal=""
organization_name_extrnal=""

@app.route('/jobs/interview/<token>/')
def interview(token):
    try:
        # Step 1: Get interview data from Django using token
        interview_response = requests.get(f"{DJANGO_API_URL}{token}/", timeout=30)
        logging.debug(f"Requesting interview data from: {DJANGO_API_URL}{token}/")
        logging.debug("Interview response status: %s", interview_response.status_code)

        if interview_response.status_code == 200:
            interview_data = interview_response.json()
            match_id = interview_data.get('id')  # Get ID to use for resume+jd
            session['id'] = match_id

            # Step 2: Get Resume & JD data using ID
            resume_jd_url = f"https://ibot-backend.onrender.com/jobs/resume-jd-by-id/{match_id}/"
            resume_jd_response = requests.get(resume_jd_url, timeout=30)

            if resume_jd_response.status_code == 200:
                resume_jd_data = resume_jd_response.json()

                # ✅ Store Resume & JD info in Flask session
                session['resume_text'] = resume_jd_data.get('resume_text')
                session['jd_text'] = resume_jd_data.get('jd_text')
                session['organization_name'] = resume_jd_data.get('organization_name')
                session['job_title'] = resume_jd_data.get('job_title')
                session['email'] = resume_jd_data.get('email')
                session['candidate_name'] = resume_jd_data.get('candidate_name')
                username_extrnal = resume_jd_data.get('candidate_name', 'Anonymous')
                organization_name_extrnal = resume_jd_data.get('organization_name', 'Unknown')

                logging.debug("Stored Resume & JD in session: %s", session)

                # Optionally combine all data for template
                full_data = {**interview_data, **resume_jd_data}


                return render_template("index.html", data=full_data)
            else:
                logging.warning("Resume+JD not found or error.")
                return render_template("error.html", message="❌ Unable to fetch resume and JD."), 500

        elif interview_response.status_code == 403:
            return render_template("error.html", message="✅ Interview already completed."), 403
        elif interview_response.status_code == 404:
            return render_template("error.html", message="❌ Invalid or expired interview link."), 404
        elif interview_response.status_code == 410:
            return render_template("error.html", message="❌ Interview link has expired."), 410
        else:
            return render_template("error.html", message="❌ Unexpected error. Please try again later."), 500

    except Exception as e:
        logging.error("Exception in interview(): %s", str(e))
        return render_template("error.html", message="⚠ Server error while retrieving interview data."), 500



def generate_initial_questions(role, experience_level, years_experience,jd_text="",resume_text=""):
    
   
    logger.debug("Starting question generation with resume and JD analysis")
    logger.debug(f"Role: {role}, Experience Level: {experience_level}, Years: {years_experience}")

    # Load previous conversation to avoid repetition
    previous_conversation = load_conversation_from_file()
    previous_questions = [item['text'] for item in previous_conversation if 'speaker' in item and item['speaker'] == 'bot']

    # Limit length to avoid token overload
    resume_excerpt = resume_text[:1500] if resume_text else "N/A"
    jd_excerpt = jd_text[:1500] if jd_text else "N/A"

    # Prompt generation
    prompt = f"""
You are an intelligent AI interviewer conducting a real-time voice-based interview.

The candidate has applied for the position of **{role}**
Experience Level: **{experience_level}**, Years of Experience: **{years_experience}**

---  
 **Resume Extract (Use this for 5 questions)**  
{resume_text[:1500] if resume_text else "Not provided"}

 **Job Description Extract (Use this for 5 questions)**  
{jd_text[:1500] if jd_text else "Not provided"}

 **Experience Info**  
Level: {experience_level}  
Years: {years_experience}

 **Target Role**  
{role}
---

 Your task is to generate **15 smart, unique, and personalized questions** broken down as follows:

1. **5 technical questions from Resume**
2. **5 technical questions from Job Description**
3. **2 questions based on Experience**
4. **3 questions based on Role responsibilities & expectations**

 Guidelines:
- Each main question must be followed by 2 intelligent follow-ups (use chain of thought)
- Do NOT repeat or overlap topics
- Avoid any questions from: {previous_questions}
- Each question must add unique value to the interview

 Format exactly like this:
Main Question: [question here]
Follow-ups: [follow-up 1] | [follow-up 2]
---

ONLY use the above format. Do NOT include labels like "Section", "Greeting".
"""




    try:
        logger.debug("Sending prompt to OpenAI for interview question generation")
        response = co.generate(
            model="command-r-plus",
            prompt=prompt,
            temperature=0.7,
            max_tokens=2000
        )
        script = response.generations[0].text
        logger.debug("Received response from OpenAI")
       

        if not script.strip():
           logger.error("Empty response from OpenAI")
           raise ValueError("AI returned no content")
 
        logger.debug("Raw script received from OpenAI:\n" + script)


        questions = []
        question_topics = []
        current_block = {}

        for line in script.split("\n"):
           line = line.strip()
           if line.startswith("Main Question:"):
              if current_block.get("main"):  # only append complete blocks
                questions.append(current_block)
              current_block = {
                "main": line.replace("Main Question:", "").strip(),
                "follow_ups": []
            }
           elif line.startswith("Follow-ups:"):
            follow_ups = line.replace("Follow-ups:", "").strip().split("|")
            current_block["follow_ups"] = [fq.strip() for fq in follow_ups if fq.strip()][:2]
            if "main" in current_block:
                question_topics.append(extract_topic(current_block["main"]))
           elif line == "---":
            if current_block.get("main"):
                questions.append(current_block)
                current_block = {}

        # Final check in case there's one more question left
        if current_block.get("main"):
         questions.append(current_block)





        # Trim the list based on experience level
        if experience_level == "fresher":
            questions = questions[:4]  # Greeting, 2 tech, 1 behavioral
        else:
            questions = questions[:5]  # Greeting, 2 tech, 1 behavioral, 1 achievement

        logger.debug(f"Generated {len(questions)} questions with {len(question_topics)} topics")
        return questions, question_topics[:len(questions)]

    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}", exc_info=True)
        logger.warning("Using fallback question set")

        if experience_level == "fresher":
            questions = [
                {
                    "main": "Welcome to the interview. Could you tell us about your educational background?",
                    "follow_ups": [
                        "What specific courses did you find most valuable?",
                        "How has your education prepared you for this role?"
                    ]
                },
                {
                    "main": "What programming languages are you most comfortable with?",
                    "follow_ups": [
                        "Can you describe a project where you used this language?",
                        "How did you learn it?"
                    ]
                },
                {
                    "main": "Can you explain a technical concept you learned recently?",
                    "follow_ups": [
                        "How have you applied this concept in practice?",
                        "What challenges did you face while learning it?"
                    ]
                },
                {
                    "main": "Describe a time you faced a challenge in a team project.",
                    "follow_ups": [
                        "What was your role in resolving it?",
                        "What did you learn from the experience?"
                    ]
                }
            ]
        else:
            questions = [
                {
                    "main": "Welcome to the interview. Can you summarize your professional experience?",
                    "follow_ups": [
                        "Which part of your experience is most relevant here?",
                        "What projects are you most proud of?"
                    ]
                },
                {
                    "main": "What technical challenges have you faced recently?",
                    "follow_ups": [
                        "How did you overcome them?",
                        "What tools did you use?"
                    ]
                },
                {
                    "main": "Describe a situation where you led a project or a team.",
                    "follow_ups": [
                        "What challenges did you face in leadership?",
                        "What did the team accomplish?"
                    ]
                },
                {
                    "main": "What's a major professional achievement you're proud of?",
                    "follow_ups": [
                        "What impact did it have?",
                        "What did you learn from it?"
                    ]
                }
            ]

        question_topics = [extract_topic(q["main"]) for q in questions]
        return questions, question_topics





def extract_topic(question):
    logger.debug(f"Extracting topic from question: {question}")
    question = question.lower()
    if 'tell me about' in question:
        return question.split('tell me about')[-1].strip(' ?')
    elif 'describe' in question:
        return question.split('describe')[-1].strip(' ?')
    elif 'explain' in question:
        return question.split('explain')[-1].strip(' ?')
    elif 'what' in question:
        return question.split('what')[-1].strip(' ?')
    elif 'how' in question:
        return question.split('how')[-1].strip(' ?')
    return question.split('?')[0].strip()

def generate_dynamic_follow_up(conversation_history, current_topic):
    logger.debug(f"Generating dynamic follow-up for topic: {current_topic}")
    try:
        prompt = f"""
        Based on the candidate's last response about '{current_topic}', generate a relevant, insightful follow-up question.
        The question should:
        1. Be directly related to specific details in their response
        2. Probe deeper into their experience, knowledge, or thought process
        3. Be professional and appropriate for a job interview
        4. Be concise (one sentence)
        
        Candidate's last response: "{conversation_history[-1]['text']}"
        
        Return ONLY the question, nothing else.
        """
        
        logger.debug("Sending prompt to OpenAI for dynamic follow-up")
        response = co.generate(
        model="command-r-plus",  # Adjust model as necessary
        prompt=prompt,
        max_tokens=200,
        temperature=0.7
        )
        follow_up = response.generations[0].text.strip()

        logger.debug(f"Generated follow-up question: {follow_up}")
        return follow_up if follow_up.endswith('?') else follow_up + '?'
    except Exception as e:
        logger.error(f"Error generating dynamic follow-up: {str(e)}", exc_info=True)
        return None


def generate_encouragement_prompt(conversation_history):
    logger.debug("Generating encouragement prompt for paused candidate")
    try:
        prompt = f"""
        The candidate has paused during their response. Generate a brief, encouraging prompt to:
        - Help them continue their thought
        - Reference specific aspects of their previous answers
        - Be supportive and professional
        - Be concise (one short sentence)
        
        Current conversation context:
        {conversation_history[-2:]}
        
        Return ONLY the prompt, nothing else.
        """

        logger.debug("Sending prompt to Cohere for encouragement generation")
        
        # Using Cohere to generate text
        response = co.generate(
            model="command-r-plus",  # Adjust the model to the one you want to use in Cohere
            prompt=prompt,
            max_tokens=300,
            temperature=0.5
        )


        # Process the response based on Cohere's structure
        encouragement = response.generations[0].text.strip()  # This is the text content from Cohere API

        logger.debug(f"Generated encouragement: {encouragement}")
        return encouragement
    except Exception as e:
        logger.error(f"Error generating encouragement prompt: {str(e)}", exc_info=True)
        return "Please continue with your thought."


def text_to_speech(text):
    logger.debug(f"Converting text to speech: {text[:50]}...")
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_filename = temp_file.name
        
        tts.save(temp_filename)
        
        # Commenting out pydub-related code
        # audio = AudioSegment.from_mp3(temp_filename)
        # wav_filename = temp_filename.replace('.mp3', '.wav')
        # audio.export(wav_filename, format="wav")
        
        # with open(wav_filename, 'rb') as f:
        #     audio_data = f.read()
        
        # Read mp3 file directly instead
        with open(temp_filename, 'rb') as f:
            audio_data = f.read()
        
        os.unlink(temp_filename)
        # os.unlink(wav_filename)  # Commenting out since we're not creating a wav file
        logger.debug("Successfully converted text to speech")
        return base64.b64encode(audio_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Error in text-to-speech: {str(e)}", exc_info=True)
        return None
def analyze_visual_response(frame_base64, conversation_context):
    logger.debug("Analyzing visual response with Cohere")
    try:
        # Construct the prompt for Cohere
        prompt = f"""
        Analyze this interview candidate's appearance and environment.
        Current conversation context: {conversation_context[-3:] if len(conversation_context) > 3 else conversation_context}
        Provide brief professional feedback on:
        1. Professional appearance (if visible)
        2. Body language and posture
        3. Environment appropriateness
        4. Any visual distractions
        Keep response under 50 words.
        """
        
        # Send the prompt to Cohere for text generation
        response = co.generate(
            model="command-r-plus",  # Replace with the appropriate Cohere model ID
            prompt=prompt,
            max_tokens=200,
            temperature=0.5
        )
        
        feedback = response.generations[0].text.strip()  # Access the generated feedback from Cohere
        logger.debug(f"Visual feedback received: {feedback}")
        return feedback
    except Exception as e:
        logger.error(f"Error in visual analysis: {str(e)}", exc_info=True)
        return None

def evaluate_response(answer, question, role, experience_level, visual_feedback=None):
    logger.debug(f"Evaluating response for question: {question[:50]}...")
    
    # Simple answer length evaluation
    if len(answer.strip()) < 20:
        logger.debug("Answer too short, returning 2")
        return 2
    elif len(answer.strip()) < 50:
        logger.debug("Short but acceptable answer, returning 4")
        return 4

    # Construct the evaluation prompt for Cohere
    rating_prompt = f"""
    Analyze this interview response for a {role} position ({experience_level} candidate).
    Question: "{question}"
    Answer: "{answer}"

    Provide ONLY a numeric rating from 1-10 based on:
    - Relevance to question (55%)
    - Depth of knowledge (20%)
    - Clarity of communication (10%)
    - Specific examples provided (5%)
    - Professionalism (10%)
    """

    try:
        response = co.generate(
            model="command-r-plus",  # Replace with the appropriate Cohere model ID
            prompt=rating_prompt,
            max_tokens=100,
            temperature=0.5
        )
        
        # Extract rating from Cohere's response
        rating_text = response.generations[0].text.strip()
        
        try:
            rating = float(rating_text)
            final_rating = max(1, min(10, rating))  # Ensure the rating is between 1 and 10
            logger.debug(f"Evaluated response rating: {final_rating}")
            return final_rating
        except:
            logger.warning(f"Could not parse rating: {rating_text}, returning default rating")
            return 5  # Default rating in case of an error
    except Exception as e:
        logger.error(f"Error evaluating response: {str(e)}", exc_info=True)
        return 5  # Default rating in case of an error


# Function to generate the interview report
def generate_interview_report(interview_data):
    try:
        # Calculate interview duration
        duration = "N/A"
        if interview_data['start_time'] and interview_data['end_time']:
            duration_seconds = (interview_data['end_time'] - interview_data['start_time']).total_seconds()
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            duration = f"{minutes}m {seconds}s"
        
        # Calculate average rating
        avg_rating = sum(interview_data['ratings']) / len(interview_data['ratings']) if interview_data['ratings'] else 0
        
        # Determine status based on average rating
        if avg_rating >= 6:
            status = "Selected"
            status_class = "selected"
        elif avg_rating >= 3 and avg_rating < 6:
            status = "On Hold"
            status_class = "onhold"
        else:
            status = "Rejected"
            status_class = "rejected"
        
        # Prepare conversation history for analysis
        conversation_history_text = "\n".join([f"{item['speaker']}: {item['text']}" for item in interview_data['conversation_history'] if 'speaker' in item])
        
        # Generate comprehensive report using Cohere
        report_prompt = f"""
        Analyze this interview transcript and generate a detailed report for a {interview_data['role']} position candidate.
        
        Candidate Background:
        - Experience Level: {interview_data['experience_level']}
        - Years of Experience: {interview_data['years_experience']}
        - Interview Duration: {duration}
        - Average Rating: {avg_rating:.1f}/10
        
        Interview Transcript:
        {conversation_history_text}
        
        Please provide a comprehensive report with the following sections:
        1. Interview Summary (brief overview)
        2. Key Strengths (3 specific strengths with examples from answers)
        3. Areas for Improvement (3 specific areas with actionable suggestions)
        4. Overall Recommendation (Selected/On Hold/Rejected)
        5. Voice Feedback Script (a concise 5-6 line summary in conversational tone)
        
        Format the report in HTML with appropriate headings and styling.
        Include tables for strengths and improvements with two columns (Aspect, Evidence/Suggestion).
        """
        
        logger.debug("Sending report generation request to Cohere")

      # Send the report prompt to Cohere for report generation
        response = co.generate(
            model="command-r-plus",  # Replace with the appropriate model for your task
            prompt=report_prompt,
            max_tokens=2000,
            temperature=0.5
        )
        
        report_content = response.generations[0].text  # Access the generated report content from Cohere
        logger.debug("Received report content from Cohere")

        
        # Generate voice feedback from the report using Cohere
        voice_feedback_prompt = f"""
        Extract or create a concise 5-6 line voice feedback summary from this interview report:
        {report_content}
        
        The feedback should:
        - Be spoken in a natural, conversational tone
        - Highlight the key conclusions
        - Be encouraging but honest
        - Be exactly 5-6 lines long
        """
        
        # Log the request to Cohere for voice feedback generation
        logger.debug("Sending voice feedback generation request to Cohere")
        
        # Send the voice feedback prompt to Cohere for generation
        voice_response = co.generate(
            model="command-r-plus",  # Replace with the appropriate model for your task
            prompt=voice_feedback_prompt,
            max_tokens=300,
            temperature=0.5
        )
        
        voice_feedback = voice_response.generations[0].text.strip()  # Get the voice feedback text from Cohere
        logger.debug(f"Generated voice feedback: {voice_feedback}")
        
        # Convert voice feedback to audio
        logger.debug("Converting voice feedback to audio")
        voice_audio = text_to_speech(voice_feedback)
        
        session['interview_data'] = interview_data  # Save updated interview data to session
        return {
            "status": "success",
            "report": report_content,
            "voice_feedback": voice_feedback,
            "voice_audio": voice_audio,
            "status_class": status_class,
            "avg_rating": avg_rating,
            "duration": duration
        }
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "report": "<p>Error generating report. Please try again.</p>",
            "voice_feedback": "We encountered an error generating your feedback.",
            "voice_audio": None
        }




class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, np.integer)):
            return str(obj)
        return json.JSONEncoder.default(self, obj)




@app.route('/')
def home():
    logger.info("Home page accessed")
    session.clear()
    session['interview_data'] = init_interview_data()
        # Provide fallback if data not available
    data = {
        "candidate_name": "Guest",
        "email": "",
        "match_score": "",
        "jd_text": "",
        "resume_text": ""
    }

    return render_template('index.html', data=data)


from datetime import datetime, timezone

@app.route('/start_interview', methods=['POST'])
def start_interview():
    logger.info("Interview start request received")
    
    data = request.get_json()
    resume_text = data.get('resume_text', '')
    jd_text = data.get('jd_text', '')

    jd_text = session.get("jd_text", "")
    resume_text = session.get("resume_text", "")


    print("Extracted Resume Text:", resume_text[:300])
    print("Extracted JD Text:", jd_text[:300])
    
    logger.debug(f"Received resume text (first 300 chars): {resume_text[:300]}")
    logger.debug(f"Received JD text (first 300 chars): {jd_text[:300]}")

    candidate_name = data.get('fileName', 'Candidate')  # match the key sent from JS
    candidate_name = candidate_name.split('.')[0].replace('_', ' ').replace('-', ' ')
    print("Candidate Name:----------------------------------------------------------", candidate_name)
    
    # Initialize interview session
    session['interview_data'] = init_interview_data()
    interview_data = session['interview_data']
    
    


    interview_data['role'] = session.get('job_title', 'Software Engineer')
    interview_data['experience_level'] = session.get('experience_level', 'fresher')
    interview_data['years_experience'] = int(session.get('years_experience', 0))
    interview_data['resume'] = session.get('resume_text')
    interview_data['jd'] = session.get('jd_text')
    interview_data['candidate_name'] = session.get('candidate_name', 'Anonymous')
    interview_data['email'] = session.get('email')
    interview_data['organization_name'] = session.get('organization_name')


    # Timestamps
    interview_data['start_time'] = datetime.now(timezone.utc)
    interview_data['last_activity_time'] = datetime.now(timezone.utc)




    logger.debug(f"Interview parameters set - Role: {interview_data['role']}, "
                 f"Experience: {interview_data['experience_level']}, "
                 f"Years: {interview_data['years_experience']}")

    try:
        questions, question_topics = generate_initial_questions(
            interview_data['role'],
            interview_data['experience_level'],
            interview_data['years_experience'],
            resume_text=resume_text,
            jd_text=jd_text
        )
        
        interview_data['questions'] = [q["main"] for q in questions]
        interview_data['follow_up_questions'] = []
        interview_data['question_topics'] = question_topics

        for q in questions:
            interview_data['conversation_history'].append({
                "question": q["main"],
                "prepared_follow_ups": q["follow_ups"]
            })
        
        interview_data['interview_started'] = True
        session['interview_data'] = interview_data
        logger.info("Interview started successfully")
        
        return jsonify({
            "status": "started",
            "total_questions": len(interview_data['questions']),
            "welcome_message": f"Welcome to the interview for {interview_data['role']} position."
        })

    except Exception as e:
        logger.error(f"Error starting interview: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500
 

from datetime import datetime, timezone, timedelta

@app.route('/get_question', methods=['GET'])
def get_question():
    logger.debug("Get question request received")

    interview_data = session.get('interview_data')
    if not interview_data:
        logger.warning("Interview data not found in session.")
        return jsonify({"status": "not_started"})

    if not interview_data.get('interview_started'):
        logger.warning("Attempt to get question before interview started")
        return jsonify({"status": "not_started"})

    # === Timer Logic (e.g., interview for 15 minutes max) ===
    elapsed_time = datetime.now(timezone.utc) - interview_data.get('start_time', datetime.now(timezone.utc))
    max_duration = timedelta(minutes=20)  # Change as needed
    if elapsed_time > max_duration:
        logger.info("Interview duration exceeded.")
        return jsonify({"status": "time_exceeded", "message": "Interview time has ended."})

    # Ensure necessary keys exist
    interview_data.setdefault('used_questions', [])
    interview_data.setdefault('used_follow_ups', [])
    interview_data.setdefault('follow_up_questions', [])
    interview_data.setdefault('follow_up_count', 0)
    interview_data.setdefault('current_question', 0)
    interview_data.setdefault('conversation_history', [])

    is_follow_up = False
    current_q = None

    # --- Select follow-up question if available ---
    if (
        interview_data['follow_up_questions'] and
        interview_data['follow_up_count'] < MAX_FOLLOW_UPS and
        (interview_data['follow_up_count'] < MIN_FOLLOW_UPS or np.random.random() < FOLLOW_UP_PROBABILITY)
    ):
        for follow_up in interview_data['follow_up_questions']:
            if follow_up not in interview_data['used_follow_ups']:
                current_q = follow_up
                interview_data['used_follow_ups'].append(current_q)
                interview_data['follow_up_count'] += 1
                is_follow_up = True
                logger.debug(f"Selected follow-up question: {current_q}")
                break

    # --- Select main question if no follow-up was selected ---
    if not current_q:
        while interview_data['current_question'] < len(interview_data['questions']):
            idx = interview_data['current_question']
            q = interview_data['questions'][idx]
            if q not in interview_data['used_questions']:
                current_q = q
                interview_data['used_questions'].append(current_q)
                interview_data['current_topic'] = interview_data['question_topics'][idx]
                interview_data['follow_up_count'] = 0
                interview_data['current_question'] += 1
                is_follow_up = False
                logger.debug(f"Selected main question: {current_q}")
                break
            else:
                interview_data['current_question'] += 1

    if not current_q:
        logger.info("All questions exhausted, interview complete")
        return jsonify({"status": "completed"})

    # Log and convert question to speech
    interview_data['conversation_history'].append({"speaker": "bot", "text": current_q})
    save_conversation_to_file([{"speaker": "bot", "text": current_q}])
    interview_data['last_activity_time'] = datetime.now(timezone.utc)
    session['interview_data'] = interview_data

    logger.debug("Converting question to speech")
    try:
        audio_data = text_to_speech(current_q)
    except Exception as e:
        logger.error(f"Text-to-speech failed: {str(e)}")
        audio_data = None

    return jsonify({
        "status": "success",
        "question": current_q,
        "audio": audio_data,
        "question_number": interview_data['current_question'],
        "total_questions": len(interview_data['questions']),
        "is_follow_up": is_follow_up
    })


import re

def parse_questions(raw):
    questions = []
    topics = []

    question_blocks = re.split(r'\n\d+\.\s+Question:\s+', raw)
    for block in question_blocks[1:]:
        parts = block.strip().split("Follow-ups:")
        main_question = parts[0].strip()

        follow_ups = []
        if len(parts) > 1:
            follow_up_lines = parts[1].strip().split("\n")
            for line in follow_up_lines:
                line = line.strip()
                match = re.match(r'\d+\.\s*\|\s*(.+)', line)
                if match:
                    follow_ups.append(match.group(1))

        questions.append({
            "main": main_question,
            "follow_ups": follow_ups
        })
        topics.append("general")  # Or customize topic logic if needed

    return questions, topics

 

@app.route('/process_answer', methods=['POST'])
def process_answer():
    logger.info("Process answer request received")
    interview_data = session.get('interview_data', init_interview_data())
    
    if not interview_data['interview_started']:
        logger.warning("Attempt to process answer before interview started")
        return jsonify({"status": "error", "message": "Interview not started"}), 400
    
    data = request.get_json()
    answer = data.get('answer', '').strip()
    frame_data = data.get('frame', None)
    logger.debug(f"Received answer length: {len(answer)} characters")
    
    if not answer:
        logger.warning("Empty answer received")
        return jsonify({"status": "error", "message": "Empty answer"}), 400

    # Safely get the last question asked
    last_entry = interview_data['conversation_history'][-1] if interview_data['conversation_history'] else {}
    current_question = last_entry.get('text') or last_entry.get('question') or ''
    
    interview_data['answers'].append(answer)
    interview_data['conversation_history'].append({"speaker": "user", "text": answer})
    save_conversation_to_file([{"speaker": "user", "text": answer}])
    interview_data['last_activity_time'] = datetime.now(timezone.utc)
    
    visual_feedback = None
    current_time = datetime.now().timestamp()
    if frame_data and (current_time - interview_data['last_frame_time']) > FRAME_CAPTURE_INTERVAL:
        try:
            logger.debug("Processing frame data")
            frame_bytes = base64.b64decode(frame_data.split(',')[1])
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame is not None:
                frame_base64 = process_frame_for_gpt4v(frame)
                visual_feedback = analyze_visual_response(
                    frame_base64,
                    interview_data['conversation_history'][-3:]
                )
                if visual_feedback:
                    interview_data['visual_feedback'].append(visual_feedback)
                    interview_data['last_frame_time'] = current_time
                    logger.debug("Visual feedback processed and stored")
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}", exc_info=True)
    
    logger.debug("Evaluating response quality")
    rating = evaluate_response(
        answer, 
        current_question, 
        interview_data['role'],
        interview_data['experience_level'],
        visual_feedback
    )
    interview_data['ratings'].append(rating)
    for entry in reversed(interview_data['conversation_history']):
     if entry.get('speaker') == 'user' and 'evaluation' not in entry:
        entry['evaluation'] = rating
        break
    logger.debug(f"Response rated: {rating}/10")
    
    if (interview_data['current_topic'] and len(answer.split()) > 15 and 
        interview_data['follow_up_count'] < MAX_FOLLOW_UPS):
        
        current_main_question_index = interview_data['current_question'] - 1
        if (current_main_question_index < len(interview_data['conversation_history']) and 
            'prepared_follow_ups' in interview_data['conversation_history'][current_main_question_index]):
            
            prepared_follow_ups = interview_data['conversation_history'][current_main_question_index]['prepared_follow_ups']
            for follow_up in prepared_follow_ups:
                if follow_up not in interview_data['used_follow_ups'] and follow_up not in interview_data['follow_up_questions']:
                    interview_data['follow_up_questions'].append(follow_up)
                    logger.debug(f"Added prepared follow-up: {follow_up}")
        
        if len(interview_data['follow_up_questions']) < MAX_FOLLOW_UPS:
            logger.debug("Generating dynamic follow-up question")
            dynamic_follow_up = generate_dynamic_follow_up(
                interview_data['conversation_history'],
                interview_data['current_topic']
            )
            if dynamic_follow_up and dynamic_follow_up not in interview_data['used_follow_ups'] and dynamic_follow_up not in interview_data['follow_up_questions']:
                interview_data['follow_up_questions'].append(dynamic_follow_up)
                logger.debug(f"Added dynamic follow-up: {dynamic_follow_up}")
    
    # Check if interview is completed
    if not interview_data['follow_up_questions']:
     interview_data['current_question'] += 1

# Now check if interview is completed
    interview_complete = interview_data['current_question'] >= len(interview_data['questions'])
    session['interview_data'] = interview_data
    if interview_complete:
     logger.info("Interview complete")
     return jsonify({
        "status": "interview_complete",
        "message": "Interview complete. Report will be generated soon."
    })
    
   
    
    return jsonify({
        "status": "answer_processed",
        "current_question": interview_data['current_question'],
        "total_questions": len(interview_data['questions']),
        "interview_complete": False,
        "has_follow_up": len(interview_data['follow_up_questions']) > 0
    })




from flask import send_from_directory




@app.route('/check_pause', methods=['GET'])
def check_pause():
    logger.debug("Check pause request received")
    interview_data = session.get('interview_data', init_interview_data())
    
    if not interview_data['interview_started']:
        logger.warning("Attempt to check pause before interview started")
        return jsonify({"status": "not_started"})
    
    current_time = datetime.now(timezone.utc)
    last_activity = interview_data['last_activity_time']
    seconds_since_activity = (current_time - last_activity).total_seconds() if last_activity else 0
    logger.debug(f"Seconds since last activity: {seconds_since_activity}")
    
    if seconds_since_activity > PAUSE_THRESHOLD:
        logger.info(f"Pause detected ({seconds_since_activity}s), generating encouragement")
        encouragement = generate_encouragement_prompt(interview_data['conversation_history'])
        audio_data = text_to_speech(encouragement)
        interview_data['last_activity_time'] = current_time
        session['interview_data'] = interview_data
        
        return jsonify({
            "status": "pause_detected",
            "prompt": encouragement,
            "audio": audio_data
        })
    
    return jsonify({"status": "active"})




@app.route('/generate_report', methods=['GET'])
def generate_report():
    logger.info("Generate report request received")
    interview_data = session.get('interview_data', init_interview_data())

    if not interview_data['interview_started']:
        logger.warning("Attempt to generate report before interview started")
        return jsonify({"status": "error", "message": "Interview not started"}), 400

    if not interview_data['end_time']:
        interview_data['end_time'] = datetime.now(timezone.utc)
        session['interview_data'] = interview_data
        logger.debug("Set end time for interview")

    interview_data["candidate_name"] = session.get("candidate_name", "Anonymous")
    interview_data["organization_name"] = session.get("organization_name", "N/A")
    interview_data["email"] = session.get("email", "Not Provided")
    interview_data["job_title"] = session.get("job_title", "Unknown")
    interview_data["resume_text"] = session.get("resume_text", "")
    interview_data["jd_text"] = session.get("jd_text", "")

    if not interview_data.get('end_time'):
        interview_data['end_time'] = datetime.now(timezone.utc)

    session['interview_data'] = interview_data 

    # ✅ Generate user report for frontend
    report = generate_interview_report(interview_data)
    logger.info("Interview report generated")
    
   
    
    # ✅ Step 2: Convert HTML report to PDF
    html_report = report.get("report", "")
    if report["status"] == "error":
        return jsonify(report), 500
    

    pdf_binary = html_to_pdf(html_report)
    if not pdf_binary:
        logger.error("PDF generation failed")
        return jsonify({"status": "error", "message": "PDF generation failed"}), 500
    


    # ✅ Step 3: Prepare JSON + Base64 PDF for Django
    django_payload = {
        "candidate_name": interview_data["candidate_name"],
        "role": interview_data["job_title"],
        "organization_name": interview_data["organization_name"],
        "years_experience": interview_data["years_experience"],
        "start_time": interview_data["start_time"].isoformat(),
        "end_time": interview_data["end_time"].isoformat(),
        "average_rating": report["avg_rating"],
        "status": report["status_class"].capitalize(),  # "Selected", "On Hold", etc.
        "report_text": html_report,
        "pdf_file": base64.b64encode(pdf_binary).decode("utf-8")
    }

    # ✅ Step 4: Send to Django backend
    try:
        django_url = "https://ibot-backend.onrender.com/jobs/save-interview-report/"
        django_response = requests.post(django_url, json=django_payload, headers={"Content-Type": "application/json"})

        if django_response.status_code == 201:
            logger.info("Report successfully sent to Django backend")
        else:
            logger.warning(f"Failed to save report in Django: {django_response.text}")

    except Exception as e:
        logger.error(f"Failed to send data to Django: {e}")

    return jsonify(report)



@app.route('/reset_interview', methods=['POST'])
def reset_interview():
    logger.info("Interview reset request received")
    session.clear()
    session['interview_data'] = init_interview_data()
    return jsonify({"status": "success", "message": "Interview reset successfully"})

from datetime import datetime, timezone

# def create_text_report_from_interview_data(interview_data):
#     from datetime import datetime

#     # Extract main fields
#     role = interview_data.get('role', 'Unknown Role')
#     username_extrnal = interview_data.get('candidate_name', 'Anonymous')

#     answered_questions = [
#     item for item in interview_data.get("conversation_history", [])
#     if item.get("answer") and item.get("evaluation") and isinstance(item.get("evaluation"), (int, float))
# ]

#     ratings = [item["evaluation"] for item in answered_questions]
#     avg_rating = sum(ratings) / len(ratings) if ratings else 0



#     # Calculate interview duration
#     duration = "N/A"
#     if interview_data.get('start_time') and interview_data.get('end_time'):
#         start = interview_data['start_time']
#         end = interview_data['end_time']
#         if isinstance(start, str):  # Parse from string if needed
#             start = datetime.fromisoformat(start.replace("Z", "+00:00"))
#         if isinstance(end, str):
#             end = datetime.fromisoformat(end.replace("Z", "+00:00"))
#         duration_seconds = (end - start).total_seconds()
#         minutes = int(duration_seconds // 60)
#         seconds = int(duration_seconds % 60)
#         duration = f"{minutes}m {seconds}s"

#     # Build conversation with answered Q&A only
#     conversation_history = interview_data.get('conversation_history', [])
#     transcript = ""
#     for idx, item in enumerate(conversation_history, 1):
#         question = item.get('question', '').strip()
#         answer = item.get('answer', '').strip()
#         evaluation = item.get('evaluation', 'Not Evaluated')
#         if answer and answer.upper() != "N/A":
#             transcript += f"""


# Q{idx}: {question}
# A{idx}: {answer}
# ✅ Evaluation: {evaluation}
# """

#     # Determine candidate suitability
#     suitability = "suitable" if avg_rating >= 6 else "not suitable"

#     # Final report text
#     report_txt = f"""
# Interview Report for {username_extrnal}

# Interview Duration: {duration}
# Average Rating: {avg_rating:.1f}/10

# Conversation Transcript:
# {transcript.strip()}

# Summary: Based on the interview performance, the candidate is **{suitability}** for the role.

# End of Report
# """.strip()

#     return report_txt

def create_text_report_from_interview_data(interview_data):
    from datetime import datetime

    # Extract key fields
    role = interview_data.get('role', 'Unknown Role')
    username_external = interview_data.get('candidate_name', 'Anonymous')

    # Filter only answered & evaluated questions
    answered_questions = [
        item for item in interview_data.get("conversation_history", [])
        if item.get("answer") and item.get("evaluation") and isinstance(item.get("evaluation"), (int, float))
    ]
    ratings = [item["evaluation"] for item in answered_questions]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    # Calculate interview duration
    duration = "N/A"
    if interview_data.get('start_time') and interview_data.get('end_time'):
        start = interview_data['start_time']
        end = interview_data['end_time']
        if isinstance(start, str):
            start = datetime.fromisoformat(start.replace("Z", "+00:00"))
        if isinstance(end, str):
            end = datetime.fromisoformat(end.replace("Z", "+00:00"))
        duration_seconds = (end - start).total_seconds()
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        duration = f"{minutes}m {seconds}s"

    # Build transcript only for answered questions
    transcript = ""
    idx = 1
    for item in interview_data.get("conversation_history", []):
        question = item.get('question') or item.get('text', '') if item.get('speaker') == 'bot' else ''
        answer = item.get('answer') or item.get('text', '') if item.get('speaker') == 'user' else ''

        evaluation = item.get('evaluation', 'Not Evaluated')

        if answer and answer.upper() != "N/A":
            transcript += f"""
Q{idx}: {question}
A{idx}: {answer}
✅ Evaluation: {evaluation}
"""
            idx += 1

    # Determine candidate suitability
    suitability = "suitable" if avg_rating >= 6 else "not suitable"

    # Final formatted report
    report_txt = f"""
Interview Report for {username_external}

Role: {role}
Interview Duration: {duration}
Average Rating: {avg_rating:.1f}/10

Conversation Transcript:
{transcript.strip()}

Summary:
The candidate answered {len(answered_questions)} questions.
Based on the interview performance, the candidate is **{suitability}** for the role.

End of Report
""".strip()

    return report_txt


import requests

# def save_report_to_django(interview_data):
#     report_txt = create_text_report_from_interview_data(interview_data)

#     candidate_name = username_extrnal
#     organization_name = organization_name_extrnal

#     payload = {
#         "candidate_name": candidate_name,
#         "role": interview_data.get("role"),
#         "organization_name": organization_name,
#         "start_time": interview_data['start_time'].isoformat(),
#         "end_time": interview_data['end_time'].isoformat(),
#         "average_rating": average_rating,,
#         "status": "Completed",
#         "report_text": report_txt
#     }

#     try:
#         response = requests.post("https://ibot-backend.onrender.com/jobs/save-report/", json=payload)
#         print("✅ Django API response:", response.status_code, response.text)
#         return response.status_code, response.json()
#     except Exception as e:
#         print("❌ Error sending report to Django:", str(e))
#         return 500, {"error": str(e)}


import requests

def save_report_to_django(interview_data):
    # ✅ Create proper report text
    report_txt = create_text_report_from_interview_data(interview_data)

    # ✅ Safely calculate average rating from evaluated answers
    answered_questions = [
        item for item in interview_data.get("conversation_history", [])
        if item.get("answer") and item.get("evaluation") and isinstance(item.get("evaluation"), (int, float))
    ]
    ratings = [item["evaluation"] for item in answered_questions]
    average_rating = sum(ratings) / len(ratings) if ratings else 0

    # ✅ Extract other required fields
    candidate_name = interview_data.get("candidate_name", "Anonymous")
    organization_name = interview_data.get("organization_name", "N/A")

    payload = {
        "candidate_name": candidate_name,
        "role": interview_data.get("role"),
        "organization_name": organization_name,
        "start_time": interview_data['start_time'].isoformat(),
        "end_time": interview_data['end_time'].isoformat(),
        "average_rating": average_rating,
        "status": "Completed",
        "report_text": report_txt
    }

    try:
        response = requests.post("https://ibot-backend.onrender.com/jobs/save-report/", json=payload)
        print("✅ Django API response:", response.status_code, response.text)
        return response.status_code, response.json()
    except Exception as e:
        print("❌ Error sending report to Django:", str(e))
        return 500, {"error": str(e)}





@app.route('/logout')
def logout():
    session.clear()  # Clears all session data
    return "Session cleared, user logged out."




if __name__ == '__main__':
    app.json_encoder = JSONEncoder
    logger.info("Starting Flask application")
    app.run(debug=True)