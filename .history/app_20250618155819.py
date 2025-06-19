from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_session import Session
import cohere
import os
from datetime import datetime, timezone, timedelta
import base64
from gtts import gTTS
import tempfile
import cv2
import numpy as np
import re
import json
import logging
from logging.handlers import RotatingFileHandler
import requests
from waitress import serve

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()  # Secure random key
DJANGO_API_URL = "https://ibot-backend.onrender.com/jobs/interview/"

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session_data')
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
Session(app)

# Logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('interview_app.log', maxBytes=10000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Cohere API Configuration
cohere_api_key = "NWOmR4gLCWgzyg43s1UyZI0W3SFyld0H7AFEssWA"
try:
    co = cohere.Client(cohere_api_key)
    logger.info("Cohere client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Cohere client: {str(e)}")
    co = None

# Configuration constants
MAX_FRAME_SIZE = 500
FRAME_CAPTURE_INTERVAL = 5
MAX_RECORDING_DURATION = 520
PAUSE_THRESHOLD = 40
FOLLOW_UP_PROBABILITY = 0.8
MIN_FOLLOW_UPS = 2
MAX_FOLLOW_UPS = 3
CONVERSATION_FILE = "interview_conversation.txt"

def init_interview_data():
    logger.debug("Initializing new interview data structure")
    if os.path.exists(CONVERSATION_FILE):
        try:
            os.remove(CONVERSATION_FILE)
        except Exception as e:
            logger.error(f"Error removing conversation file: {str(e)}")
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
        "used_follow_ups": [],
        "candidate_name": "Candidate"
    }

def save_conversation_to_file(conversation_data):
    try:
        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
            for item in conversation_data:
                if 'speaker' in item:
                    f.write(f"{item['speaker']}: {item['text']}\n")
                    if item.get('feedback'):
                        f.write(f"Feedback: {item['feedback']}\n")
        logger.debug("Conversation saved to file")
    except Exception as e:
        logger.error(f"Error saving conversation to file: {str(e)}")

def load_conversation_from_file():
    try:
        if not os.path.exists(CONVERSATION_FILE):
            return []
        with open(CONVERSATION_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        conversation = []
        for line in lines:
            if line.startswith("bot:") or line.startswith("user:"):
                speaker, text = line.split(":", 1)
                conversation.append({"speaker": speaker.strip(), "text": text.strip()})
            elif line.startswith("Question:"):
                question = line.split(":", 1)[1].strip()
                conversation.append({"question": question})
            elif line.startswith("Feedback:"):
                feedback = line.split(":", 1)[1].strip()
                if conversation and 'text' in conversation[-1]:
                    conversation[-1]['feedback'] = feedback
        return conversation
    except Exception as e:
        logger.error(f"Error loading conversation from file: {str(e)}")
        return []

@app.before_request
def before_request():
    logger.debug(f"Before request - path: {request.path}, method: {request.method}")
    if 'interview_data' not in session:
        session['interview_data'] = init_interview_data()
    session.modified = True

@app.route('/jobs/interview/<token>/')
def interview(token):
    try:
        logger.debug(f"Fetching interview data for token: {token}")
        response = requests.get(f"{DJANGO_API_URL}{token}/", timeout=30)
        logger.debug(f"Django API response: {response.status_code}, {response.text}")

        if response.status_code == 200:
            data = response.json()
            match_id = data.get('id')
            if not match_id:
                logger.error("No match_id in response")
                return render_template("error.html", message="Invalid interview data."), 500

            session['id'] = match_id
            resume_jd_url = f"https://ibot-backend.onrender.com/jobs/resume-jd-by-id/{match_id}/"
            resume_jd_response = requests.get(resume_jd_url, timeout=30)
            logger.debug(f"Resume/JD API response: {resume_jd_response.status_code}, {resume_jd_response.text}")

            if resume_jd_response.status_code == 200:
                resume_jd_data = resume_jd_response.json()
                full_data = {
                    'id': match_id,
                    'resume_text': resume_jd_data.get('resume_text', ''),
                    'jd_text': resume_jd_data.get('jd_text', ''),
                    'organization_name': resume_jd_data.get('organization_name', 'Unknown'),
                    'job_title': resume_jd_data.get('job_title', 'Unknown'),
                    'email': resume_jd_data.get('email', ''),
                    'candidate_name': resume_jd_data.get('candidate_name', 'Anonymous')
                }
                session['resume_text'] = full_data['resume_text']
                session['jd_text'] = full_data['jd_text']
                session['candidate_name'] = full_data['candidate_name']
                session['job_title'] = full_data['job_title']
                session.modified = True
                logger.debug(f"Rendering index.html with data: {json.dumps(full_data, indent=2)}")
                return render_template("index.html", data=full_data)
            else:
                logger.error(f"Resume/JD API failed: {resume_jd_response.status_code}")
                return render_template("error.html", message="Unable to fetch resume and JD."), 500
        else:
            logger.error(f"Django API failed: {response.status_code}")
            messages = {
                403: "Interview already completed.",
                404: "Invalid or expired interview link.",
                410: "Interview link has expired."
            }
            return render_template("error.html", message=messages.get(response.status_code, "Something went wrong.")), response.status_code
    except Exception as e:
        logger.error(f"Error in interview route: {str(e)}")
        return render_template("error.html", message="Server error while retrieving interview data."), 500

def generate_initial_questions(role, experience_level, years_experience, jd_text, resume_text):
    logger.debug(f"Generating questions for role: {role}, experience: {experience_level}, years: {years_experience}")
    if not co:
        logger.error("Cohere client not initialized")
        return get_fallback_questions(experience_level)

    resume_excerpt = resume_text[:1000] if resume_text else "N/A"
    jd_excerpt = jd_text[:1000] if jd_text else "N/A"
    prompt = f"""
You are an AI interviewer for a {role} position.
Candidate:
- Experience Level: {experience_level}
- Years of Experience: {years_experience}
- Resume Excerpt: {resume_excerpt}
- Job Description Excerpt: {jd_excerpt}
Generate 8 unique questions:
- 2 technical from resume
- 2 technical from job description
- 2 based on experience
- 2 based on role responsibilities
Format:
Main Question: [question]
Follow-ups: [follow-up 1] | [follow-up 2]
---
"""
    try:
        response = co.generate(
            model="command-r-plus",
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )
        script = response.generations[0].text.strip()
        logger.debug(f"Raw Cohere response: {script[:200]}...")
        questions = []
        question_topics = []
        current_block = {}
        for line in script.split("\n"):
            line = line.strip()
            if line.startswith("Main Question:"):
                if current_block.get("main"):
                    questions.append(current_block)
                current_block = {"main": line.replace("Main Question:", "").strip(), "follow_ups": []}
            elif line.startswith("Follow-ups:"):
                follow_ups = line.replace("Follow-ups:", "").strip().split("|")
                current_block["follow_ups"] = [fq.strip() for fq in follow_ups if fq.strip()][:2]
                if "main" in current_block:
                    question_topics.append(extract_topic(current_block["main"]))
            elif line == "---":
                if current_block.get("main"):
                    questions.append(current_block)
                    current_block = {}
        if current_block.get("main"):
            questions.append(current_block)
        if not questions:
            logger.warning("No questions generated, using fallback")
            return get_fallback_questions(experience_level)
        questions = questions[:8]
        question_topics = question_topics[:len(questions)]
        logger.debug(f"Generated {len(questions)} questions")
        return questions, question_topics
    except Exception as e:
        logger.error(f"Cohere API error: {str(e)}")
        return get_fallback_questions(experience_level)

def get_fallback_questions(experience_level):
    logger.debug("Using fallback questions")
    if experience_level == "fresher":
        questions = [
            {"main": "Tell us about your educational background.", "follow_ups": ["Which courses were most relevant?", "How did you apply your learning?"]},
            {"main": "What programming languages do you know?", "follow_ups": ["Describe a project using one.", "How did you learn it?"]},
            {"main": "Explain a recent technical concept you learned.", "follow_ups": ["How did you apply it?", "What challenges did you face?"]},
            {"main": "Describe a team project challenge.", "follow_ups": ["How did you resolve it?", "What did you learn?"]}
        ]
    else:
        questions = [
            {"main": "Summarize your professional experience.", "follow_ups": ["What’s most relevant to this role?", "What projects stand out?"]},
            {"main": "Describe a recent technical challenge.", "follow_ups": ["How did you solve it?", "What tools did you use?"]},
            {"main": "Tell us about leading a project.", "follow_ups": ["What challenges arose?", "What was the outcome?"]},
            {"main": "Share a major professional achievement.", "follow_ups": ["What was its impact?", "What did you learn?"]}
        ]
    question_topics = [extract_topic(q["main"]) for q in questions]
    return questions, question_topics

def extract_topic(question):
    question = question.lower()
    if 'tell' in question:
        return question.split('tell')[-1].strip(' ?')
    elif 'describe' in question:
        return question.split('describe')[-1].strip(' ?')
    elif 'explain' in question:
        return question.split('explain')[-1].strip(' ?')
    elif 'what' in question:
        return question.split('what')[-1].strip(' ?')
    return question.split('?')[0].strip()

def text_to_speech(text):
    logger.debug(f"Converting text to speech: {text[:50]}...")
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_filename = temp_file.name
        tts.save(temp_filename)
        with open(temp_filename, 'rb') as f:
            audio_data = f.read()
        os.unlink(temp_filename)
        logger.debug("Successfully converted text to speech")
        return base64.b64encode(audio_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Error in text-to-speech conversion: {str(e)}")
        return None

def analyze_visual_response(frame_base64, conversation_context):
    logger.debug("Analyzing visual response with Cohere")
    try:
        prompt = f"""
Analyze this interview candidate's environment based on the current conversation context.
Context: {conversation_context[-3:] if len(conversation_context) > 3 else conversation_context}
Provide brief professional feedback on:
1. Environment appropriateness
2. Visual distractions
Keep response under 50 words.
"""
        response = co.generate(
            model="command-r",
            prompt=prompt,
            max_tokens=200,
            temperature=0.2
        )
        feedback = response.generations[0].text.strip()
        logger.debug(f"Visual feedback received: {feedback}")
        return feedback
    except Exception as e:
        logger.error(f"Error in visual analysis: {str(e)}")
        return None

def evaluate_response(answer, question, role, experience_level, visual_feedback=None):
    logger.debug(f"Evaluating response for question: {question[:50]}...")
    if len(answer.strip()) < 20:
        logger.debug("Answer too short")
        return {
            "final_rating": 2,
            "feedback": "The answer is too brief. Please provide more details to demonstrate your knowledge."
        }
    elif len(answer.strip()) < 50:
        logger.debug("Short but acceptable answer")
        return {
            "final_rating": 4,
            "feedback": "The answer is brief but acceptable. Adding specific examples would strengthen your response."
        }

    rating_prompt = f"""
You are assessing an interview response for a {role} position from a {experience_level} candidate.
Question: "{question}"
Answer: "{answer}"
Evaluate based on:
- Relevance to Question (20%)
- Depth of Knowledge (30%)
- Clarity of Communication (20%)
- Use of Specific Examples (20%)
- Professionalism (10%)
Provide feedback (2-3 sentences) on the answer's strengths and areas for improvement.
Return JSON:
{{
  "relevance": <score>,
  "knowledge_depth": <score>,
  "clarity": <score>,
  "examples": <score>,
  "professionalism": <score>,
  "final_rating": <weighted_average_score>,
  "feedback": "<feedback_text>"
}}
"""
    try:
        response = co.generate(
            model="command-r-plus",
            prompt=rating_prompt,
            max_tokens=300,
            temperature=0.3
        )
        rating_data = json.loads(response.generations[0].text.strip())
        final_rating = float(rating_data.get('final_rating', 5))
        feedback = rating_data.get('feedback', 'No feedback provided.')
        logger.debug(f"Evaluated response rating: {final_rating}, feedback: {feedback}")
        return {
            "final_rating": max(1, min(10, final_rating)),
            "feedback": feedback
        }
    except Exception as e:
        logger.error(f"Error evaluating response: {str(e)}")
        return {
            "final_rating": 5,
            "feedback": "Unable to evaluate response due to an error."
        }

def generate_interview_report(interview_data):
    try:
        duration = "N/A"
        if interview_data.get('start_time') and interview_data.get('end_time'):
            duration_seconds = (interview_data['end_time'] - interview_data['start_time']).total_seconds()
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            duration = f"{minutes}m {seconds}s"
        
        ratings = interview_data.get('ratings', [])
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        rating_distribution = {
            "High": len([r for r in ratings if r >= 8]),
            "Moderate": len([r for r in ratings if 6 <= r < 8]),
            "Low": len([r for r in ratings if 4 <= r < 6]),
            "Poor": len([r for r in ratings if r < 4])
        }
        
        if avg_rating >= 7:
            status = "Selected"
            status_class = "selected"
        elif avg_rating >= 4:
            status = "On Hold"
            status_class = "onhold"
        else:
            status = "Rejected"
            status_class = "rejected"
        
        conversation_history = interview_data.get('conversation_history', [])
        conversation_lines = []
        question_counter = 1
        i = 0
        while i < len(conversation_history):
            item = conversation_history[i]
            if item.get('speaker') == 'bot':
                question_text = item.get('text', '')
                conversation_lines.append(f"<p><strong>Q{question_counter}: {question_text}</strong></p>")
                if i + 1 < len(conversation_history) and conversation_history[i + 1].get('speaker') == 'user':
                    answer_text = conversation_history[i + 1].get('text', '')
                    feedback = conversation_history[i + 1].get('feedback', 'No feedback available.')
                    conversation_lines.append(f"<p>Response: {answer_text}</p>")
                    conversation_lines.append(f"<p><em>Feedback: {feedback}</em></p>")
                    i += 2
                else:
                    conversation_lines.append("<p>Response: No answer provided.</p>")
                    conversation_lines.append("<p><em>Feedback: No feedback due to missing answer.</em></p>")
                    i += 1
                question_counter += 1
            else:
                i += 1
        conversation_html = "\n".join(conversation_lines)
        
        report_prompt = f"""
You are an expert AI HR assistant generating an interview evaluation report for a {interview_data['role']} position.
Candidate Overview:
- Experience Level: {interview_data['experience_level']}
- Years of Experience: {interview_data['years_experience']}
- Interview Duration: {duration}
- Average Rating: {avg_rating:.1f}/10
Interview Transcript with Feedback:
{conversation_html}
Generate a report in HTML with:
1. Interview Summary (brief overview)
2. Key Strengths (table with 3-5 strengths)
3. Areas for Improvement (table with 3-5 areas)
4. Visual Analysis (skill distribution, brief text)
5. Overall Recommendation (conclusion)
Do not include the transcript in the report; it’s provided for context only.
"""
        response = co.generate(
            model="command-r-plus",
            prompt=report_prompt,
            max_tokens=2000,
            temperature=0.5
        )
        report_content = response.generations[0].text
        
        voice_feedback_prompt = f"""
Extract a 5-6 line voice feedback summary from:
{report_content}
Feedback should be conversational, encouraging, and honest.
"""
        voice_response = co.generate(
            model="command-r-plus",
            prompt=voice_feedback_prompt,
            max_tokens=300,
            temperature=0.5
        )
        voice_feedback = voice_response.generations[0].text.strip()
        voice_audio = text_to_speech(voice_feedback)
        
        chart_html = """
        <div style="width: 300px; margin: 20px auto;">
            <canvas id="ratingPieChart"></canvas>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const ctx = document.getElementById('ratingPieChart').getContext('2d');
                new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: ['High (≥8)', 'Moderate (6-7.9)', 'Low (4-5.9)', 'Poor (<4)'],
                        datasets: [{
                            data: [%s, %s, %s, %s],
                            backgroundColor: ['#36A2EB', '#FFCE56', '#FF6384', '#999999'],
                            borderColor: '#ffffff',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'top',
                                labels: { font: { size: 14 } }
                            },
                            title: {
                                display: true,
                                text: 'Answer Rating Distribution',
                                font: { size: 16 }
                            }
                        }
                    }
                });
            });
        </script>
        """ % (
            rating_distribution['High'],
            rating_distribution['Moderate'],
            rating_distribution['Low'],
            rating_distribution['Poor']
        )
        
        final_report_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: auto; padding: 20px;">
            {report_content}
            <h2>Rating Distribution</h2>
            {chart_html}
        </div>
        """
        
        logger.info("Interview report generated successfully")
        return {
            "status": "success",
            "report": final_report_html,
            "voice_feedback": voice_feedback,
            "voice_audio": voice_audio,
            "status_class": status_class,
            "avg_rating": avg_rating,
            "duration": duration
        }
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "report": "<p>Error generating report.</p>",
            "voice_feedback": "Error generating feedback.",
            "voice_audio": None
        }

def create_text_report_from_interview_data(interview_data):
    candidate = interview_data.get('candidate_name', 'Unknown Candidate')
    role = interview_data.get('role', 'Unknown Role')
    exp_level = interview_data.get('experience_level', 'Unknown')
    years = interview_data.get('years_experience', 0)
    conv_history = interview_data.get("conversation_history", [])
    
    conversation_lines = []
    i = 0
    n = len(conv_history)
    question_counter = 1
    while i < n:
        q_item = conv_history[i]
        if q_item.get("speaker", "").lower() == "bot":
            question_text = q_item.get("text", "")
            conversation_lines.append(f"Q{question_counter}: {question_text}")
        else:
            i += 1
            continue
        if i + 1 < n:
            a_item = conv_history[i + 1]
            if a_item.get("speaker", "").lower() == "user":
                answer_text = a_item.get("text", "")
                feedback = a_item.get("feedback", "No feedback available.")
                conversation_lines.append(f"Response: {answer_text}")
                conversation_lines.append(f"Feedback: {feedback}")
        question_counter += 1
        i += 2
    conversation_text = "\n".join(conversation_lines)
    
    ratings = interview_data.get('ratings', [])
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    performance = "High" if avg_rating >= 8 else "Moderate" if avg_rating >= 6 else "Low" if avg_rating >= 4 else "Poor"
    
    duration = "N/A"
    if interview_data.get('start_time') and interview_data.get('end_time'):
        duration_seconds = (interview_data['end_time'] - interview_data['start_time']).total_seconds()
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        duration = f"{minutes}m {seconds}s"
    
    report_txt = f"""
Interview Report for {candidate}
Role: {role}
Experience Level: {exp_level}
Years of Experience: {years}
Interview Duration: {duration}
Average Rating: {avg_rating:.1f}/10
Overall Performance: {performance}
Conversation Transcript with Feedback:
{conversation_text}
Rating Distribution:
- High (≥8): {len([r for r in ratings if r >= 8])}
- Moderate (6-7.9): {len([r for r in ratings if 6 <= r < 8])}
- Low (4-5.9): {len([r for r in ratings if 4 <= r < 6])}
- Poor (<4): {len([r for r in ratings if r < 4])}
End of Report
"""
    return report_txt

def save_admin_report_txt(interview_data):
    try:
        report_txt = create_text_report_from_interview_data(interview_data)
        candidate = interview_data.get("candidate_name", "unknown").replace(" ", "_")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{candidate}_interview_report_{timestamp}.txt"
        reports_folder = os.path.join(os.getcwd(), "reports")
        os.makedirs(reports_folder, exist_ok=True)
        filepath = os.path.join(reports_folder, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_txt)
        logger.info(f"Admin report saved at {filepath}")
        return filepath, filename
    except Exception as e:
        logger.error(f"Failed to save admin report: {str(e)}")
        raise

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
    data = {
        "user_name": "Guest",
        "email": "",
        "match_score": "",
        "jd_text": "",
        "resume_text": ""
    }
    return render_template('index.html', data=data)

# @app.route('/start_interview', methods=['POST'])
# def start_interview():
#     logger.info("Interview start request received")
#     try:
#         data = request.get_json()
#         if not data:
#             logger.error("No JSON data provided")
#             return jsonify({"status": "error", "message": "No JSON data provided"}), 400
#         role = data.get('role', '').strip()
#         resume_text = data.get('resume_text', '').strip()
#         jd_text = data.get('jd_text', '').strip()
#         if not role:
#             logger.error("Role is required")
#             return jsonify({"status": "error", "message": "Role is required"}), 400
#         if not resume_text or not jd_text:
#             logger.warning("Resume or JD text missing, checking session")
#             resume_text = session.get('resume_text', '')
#             jd_text = session.get('jd_text', '')
#             if not resume_text or not jd_text:
#                 logger.error("Resume or JD text not found in session")
#                 return jsonify({"status": "error", "message": "Resume or JD text missing"}), 400
#         candidate_name = data.get('candidate_name', session.get('candidate_name', 'Candidate'))
#         session['interview_data'] = init_interview_data()
#         interview_data = session['interview_data']
#         interview_data['role'] = role
#         interview_data['experience_level'] = data.get('experience_level', 'fresher')
#         interview_data['years_experience'] = int(data.get('years_experience', 0))
#         interview_data['resume'] = resume_text[:1000]
#         interview_data['jd'] = jd_text[:1000]
#         interview_data['candidate_name'] = candidate_name
#         interview_data['start_time'] = datetime.now(timezone.utc)
#         interview_data['last_activity_time'] = datetime.now(timezone.utc)
#         questions, question_topics = generate_initial_questions(
#             role=interview_data['role'],
#             experience_level=interview_data['experience_level'],
#             years_experience=interview_data['years_experience'],
#             resume_text=resume_text,
#             jd_text=jd_text
#         )
#         interview_data['questions'] = [q["main"] for q in questions]
#         interview_data['follow_up_questions'] = []
#         interview_data['question_topics'] = question_topics
#         for q in questions:
#             interview_data['conversation_history'].append({
#                 "question": q["main"],
#                 "prepared_follow_ups": q["follow_ups"]
#             })
#         interview_data['interview_started'] = True
#         session['interview_data'] = interview_data
#         session.modified = True
#         logger.info("Interview started successfully")
#         return jsonify({
#             "status": "started",
#             "total_questions": len(interview_data['questions']),
#             "welcome_message": f"Welcome to the interview for {interview_data['role']} position."
#         })
#     except Exception as e:
#         logger.error(f"Unexpected error in start_interview: {str(e)}", exc_info=True)
#         return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500
@app.route('/start_interview', methods=['POST'])
def start_interview():
    try:
        logger.debug("Start interview request received")
        data = request.get_json()
        if not data:
            logger.error("No JSON data provided")
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400

        role = data.get('role', '').strip()
        resume_text = data.get('resume_text', '').strip()
        jd_text = data.get('jd_text', '').strip()
        candidate_name = data.get('candidate_name', 'Anonymous').strip()

        if not role:
            logger.error("Role is required")
            return jsonify({"status": "error", "message": "Role is required"}), 400

        # Fallback to session data
        if not resume_text or not jd_text:
            logger.debug("Checking session for resume_text and jd_text")
            resume_text = session.get('resume_text', '')
            jd_text = session.get('jd_text', '')
            if not resume_text or not jd_text:
                logger.error("Resume or JD text missing")
                return jsonify({"status": "error", "message": "Resume or JD text missing"}), 400

        session['interview_data'] = {
            'role': role,
            'candidate_name': candidate_name,
            'resume_text': resume_text,
            'jd_text': jd_text,
            'interview_started': True,
            'questions': [
                "Tell me about yourself.",
                "What are your strengths?",
                "Describe a technical project you worked on."
            ],
            'current_question': 0
        }
        session.modified = True
        logger.debug(f"Interview started with data: {json.dumps(session['interview_data'], indent=2)}")
        return jsonify({
            "status": "started",
            "message": f"Welcome to the interview for {role} position."
        })
    except Exception as e:
        logger.error(f"Error in start_interview: {str(e)}")
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

# @app.route('/get_question', methods=['GET'])
# def get_question():
#     logger.debug("Get question request received")
#     interview_data = session.get('interview_data')
#     if not interview_data or not interview_data.get('interview_started'):
#         logger.warning("Interview not started")
#         return jsonify({"status": "not_started"}), 400
#     elapsed_time = datetime.now(timezone.utc) - interview_data.get('start_time', datetime.now(timezone.utc))
#     max_duration = timedelta(minutes=20)
#     if elapsed_time > max_duration:
#         logger.info("Interview duration exceeded")
#         return jsonify({"status": "time_exceeded", "message": "Interview time has ended."}), 400
#     interview_data.setdefault('used_questions', [])
#     interview_data.setdefault('used_follow_ups', [])
#     interview_data.setdefault('follow_up_questions', [])
#     interview_data.setdefault('follow_up_count', 0)
#     interview_data.setdefault('current_question', 0)
#     interview_data.setdefault('conversation_history', [])
#     is_follow_up = False
#     current_q = None
#     if (
#         interview_data['follow_up_questions'] and
#         interview_data['follow_up_count'] < MAX_FOLLOW_UPS and
#         (interview_data['follow_up_count'] < MIN_FOLLOW_UPS or np.random.random() < FOLLOW_UP_PROBABILITY)
#     ):
#         for follow_up in interview_data['follow_up_questions']:
#             if follow_up not in interview_data['used_follow_ups']:
#                 current_q = follow_up
#                 interview_data['used_follow_ups'].append(current_q)
#                 interview_data['follow_up_count'] += 1
#                 is_follow_up = True
#                 logger.debug(f"Selected follow-up question: {current_q}")
#                 break
#     if not current_q:
#         while interview_data['current_question'] < len(interview_data['questions']):
#             idx = interview_data['current_question']
#             q = interview_data['questions'][idx]
#             if q not in interview_data['used_questions']:
#                 current_q = q
#                 interview_data['used_questions'].append(current_q)
#                 interview_data['current_topic'] = interview_data['question_topics'][idx]
#                 interview_data['follow_up_count'] = 0
#                 interview_data['current_question'] += 1
#                 is_follow_up = False
#                 logger.debug(f"Selected main question: {current_q}")
#                 break
#             else:
#                 interview_data['current_question'] += 1
#     if not current_q:
#         logger.info("All questions exhausted, interview complete")
#         return jsonify({"status": "completed"})
#     interview_data['conversation_history'].append({"speaker": "bot", "text": current_q})
#     save_conversation_to_file([{"speaker": "bot", "text": current_q}])
#     interview_data['last_activity_time'] = datetime.now(timezone.utc)
#     session['interview_data'] = interview_data
#     session.modified = True
#     audio_data = text_to_speech(current_q)
#     return jsonify({
#         "status": "success",
#         "question": current_q,
#         "audio": audio_data,
#         "question_number": interview_data['current_question'],
#         "total_questions": len(interview_data['questions']),
#         "is_follow_up": is_follow_up
#     })
@app.route('/get_question', methods=['GET'])
def get_question():
    try:
        logger.debug("Get question request received")
        interview_data = session.get('interview_data', {})
        if not interview_data.get('interview_started'):
            logger.warning("Interview not started")
            return jsonify({"status": "not_started"}), 400

        current_question = interview_data.get('current_question', 0)
        questions = interview_data.get('questions', [])
        if current_question >= len(questions):
            logger.info("All questions completed")
            return jsonify({"status": "completed"})

        question = questions[current_question]
        interview_data['current_question'] = current_question + 1
        session['interview_data'] = interview_data
        session.modified = True
        logger.debug(f"Returning question: {question}")
        return jsonify({
            "status": "success",
            "question": question,
            "question_number": current_question + 1,
            "total_questions": len(questions)
        })
    except Exception as e:
        logger.error(f"Error in get_question: {str(e)}")
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500
@app.route('/process_answer', methods=['POST'])
def process_answer():
    logger.info("Process answer request received")
    interview_data = session.get('interview_data', init_interview_data())
    if not interview_data.get('interview_started'):
        logger.warning("Interview not started")
        return jsonify({"status": "error", "message": "Interview not started"}), 400
    data = request.get_json()
    answer = data.get('answer', '').strip()
    frame_data = data.get('frame', None)
    if not answer:
        logger.warning("Empty answer received")
        return jsonify({"status": "error", "message": "Empty answer"}), 400
    
    last_entry = interview_data['conversation_history'][-1] if interview_data['conversation_history'] else {}
    current_question = last_entry.get('text') or last_entry.get('question') or ''
    
    evaluation = evaluate_response(
        answer,
        current_question,
        interview_data['role'],
        interview_data['experience_level']
    )
    rating = evaluation['final_rating']
    feedback = evaluation['feedback']
    
    interview_data['answers'].append(answer)
    interview_data['ratings'].append(rating)
    interview_data['conversation_history'].append({
        "speaker": "user",
        "text": answer,
        "feedback": feedback,
        "feedback_label": "Good answer" if len(answer) > 50 else "Needs improvement"
    })
    save_conversation_to_file([{"speaker": "user", "text": answer, "feedback": feedback}])
    interview_data['last_activity_time'] = datetime.now(timezone.utc)
    
    visual_feedback = None
    current_time = datetime.now().timestamp()
    if frame_data and (current_time - interview_data['last_frame_time']) > FRAME_CAPTURE_INTERVAL:
        try:
            frame_bytes = base64.b64decode(frame_data.split(',')[1])
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            if frame is not None:
                frame_base64 = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode('utf-8')
                visual_feedback = analyze_visual_response(
                    frame_base64,
                    interview_data['conversation_history'][-3:]
                )
                if visual_feedback:
                    interview_data['visual_feedback'].append(visual_feedback)
                    interview_data['last_frame_time'] = current_time
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
    
    feedback_audio = text_to_speech(feedback)
    
    if (interview_data['current_topic'] and len(answer.split()) > 15 and
            interview_data['follow_up_count'] < MAX_FOLLOW_UPS):
        current_main_question_index = interview_data['current_question'] - 1
        if (current_main_question_index < len(interview_data['conversation_history']) and
                'prepared_follow_ups' in interview_data['conversation_history'][current_main_question_index]):
            prepared_follow_ups = interview_data['conversation_history'][current_main_question_index]['prepared_follow_ups']
            for follow_up in prepared_follow_ups:
                if follow_up not in interview_data['used_follow_ups'] and follow_up not in interview_data['follow_up_questions']:
                    interview_data['follow_up_questions'].append(follow_up)
    
    interview_complete = interview_data['current_question'] >= len(interview_data['questions']) and not interview_data['follow_up_questions']
    if interview_complete:
        logger.info("Interview complete, generating report")
        user_report = generate_interview_report(interview_data)
        filepath, filename = save_admin_report_txt(interview_data)
        return jsonify({
            "status": "interview_complete",
            "message": "Interview complete, report generated and saved.",
            "report_html": user_report.get('report', ''),
            "admin_report_filename": filename
        })
    
    session['interview_data'] = interview_data
    session.modified = True
    return jsonify({
        "status": "answer_processed",
        "current_question": interview_data['current_question'],
        "total_questions": len(interview_data['questions']),
        "interview_complete": False,
        "has_follow_up": len(interview_data['follow_up_questions']) > 0,
        "feedback_audio": feedback_audio
    })

@app.route('/check_pause', methods=['GET'])
def check_pause():
    logger.debug("Check pause request received")
    interview_data = session.get('interview_data', init_interview_data())
    if not interview_data['interview_started']:
        logger.warning("Interview not started")
        return jsonify({"status": "not_started"}), 400
    current_time = datetime.now(timezone.utc)
    last_activity = interview_data['last_activity_time']
    seconds_since_activity = (current_time - last_activity).total_seconds() if last_activity else 0
    if seconds_since_activity > PAUSE_THRESHOLD:
        logger.info(f"Pause detected ({seconds_since_activity}s)")
        encouragement = "Please continue with your thought."
        audio_data = text_to_speech(encouragement)
        interview_data['last_activity_time'] = current_time
        session['interview_data'] = interview_data
        session.modified = True
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
        logger.warning("Interview not started")
        return jsonify({"status": "error", "message": "Interview not started"}), 400
    if not interview_data['end_time']:
        interview_data['end_time'] = datetime.now(timezone.utc)
        session['interview_data'] = interview_data
        session.modified = True
    try:
        filepath, filename = save_admin_report_txt(interview_data)
        logger.info(f"Admin report saved at {filepath}")
    except Exception as e:
        logger.error(f"Failed to save admin report: {str(e)}")
    report = generate_interview_report(interview_data)
    return jsonify(report)

@app.route('/reset_interview', methods=['POST'])
def reset_interview():
    logger.info("Interview reset request received")
    session.clear()
    session['interview_data'] = init_interview_data()
    session.modified = True
    return jsonify({"status": "success", "message": "Interview reset successfully"})

@app.route('/download_report/<filename>')
def download_report(filename):
    folder = 'reports'
    return send_from_directory(folder, filename, as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    session.modified = True
    return jsonify({"status": "success", "message": "Session cleared, user logged out."})

if __name__ == '__main__':
    app.json_encoder = JSONEncoder
    logger.info("Starting Flask application")
    app.run(debug=True)