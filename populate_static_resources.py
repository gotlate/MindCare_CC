import json
import os

# --- Configuration ---
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
STUDENT_RESOURCES_PATH = os.path.join(DATA_DIR, 'student_resources.json')
PROFESSIONAL_RESOURCES_PATH = os.path.join(DATA_DIR, 'professional_resources.json')

# --- Static Data ---
STATIC_ARTICLES_STUDENT = [
    {"title": "The Jed Foundation | Mental Health Resource Center", "url": "https://www.jedfoundation.org/", "description": "Provides resources, support, and guidance for teens and young adults."},
    {"title": "Active Minds | Changing the Conversation About Mental Health", "url": "https://www.activeminds.org/", "description": "A leading nonprofit for young adult mental health advocacy and awareness."},
    {"title": "Mindfulness for Students | Mindful.org", "url": "https://www.mindful.org/mindfulness-for-students/", "description": "Articles and guides on practicing mindfulness to reduce stress and improve focus."},
    {"title": "NAMI | National Alliance on Mental Illness", "url": "https://www.nami.org/Your-Journey/Teens-Young-Adults", "description": "Support and resources for young adults facing mental health challenges."}
]

STATIC_ARTICLES_PROFESSIONAL = [
    {"title": "Harvard Business Review - Mental Health Topic", "url": "https://hbr.org/topic/mental-health", "description": "In-depth articles on mental health, leadership, and workplace culture."},
    {"title": "Mental Health America - Workplace Wellness", "url": "https://www.mhanational.org/workplace-wellness", "description": "Tools, resources, and research on creating mentally healthy workplaces."},
    {"title": "Forbes - Mental Health in the Workplace", "url": "https://www.forbes.com/mental-health-in-the-workplace/", "description": "News and articles on the intersection of business and mental well-being."},
    {"title": "OSHA - Workplace Stress", "url": "https://www.osha.gov/workplace-stress", "description": "Resources from the Occupational Safety and Health Administration on managing workplace stress."}
]

SUGGESTIONS_STUDENT = [
    "Take a 10-minute walk between classes to clear your head.",
    "Prioritize getting 7-9 hours of sleep, especially before an exam.",
    "Join a study group or a club to build a sense of community.",
    "Schedule your study sessions in a planner to reduce anxiety about deadlines.",
    "Practice the 4-7-8 breathing technique before a presentation.",
    "Set small, achievable goals for each study session.",
    "Celebrate your small wins, like finishing a difficult chapter.",
    "Designate a specific area for studying to improve focus.",
    "Limit social media use an hour before bedtime.",
    "Eat a balanced breakfast to fuel your brain for the day.",
    "Stay hydrated by keeping a water bottle with you.",
    "Reach out to a professor or TA during office hours if you're struggling.",
    "Use noise-cancelling headphones to minimize distractions.",
    "Incorporate physical activity into your daily routine.",
    "Explore your campus's counseling and psychological services.",
    "Make time for a hobby that you enjoy and find relaxing.",
    "Learn to say 'no' to extra commitments when you're feeling overwhelmed.",
    "Spend time in nature, even if it's just a park on campus.",
    "Keep your living space organized and clean.",
    "Create a 'worry journal' to write down anxieties before they build up.",
    "Practice positive self-talk and challenge negative thoughts.",
    "Listen to calming music or a podcast while you commute or walk.",
    "Unfollow social media accounts that make you feel inadequate.",
    "Make a list of things you're grateful for at the end of each week.",
    "Connect with friends and talk about something other than school.",
    "Plan a fun, low-stress activity for the weekend.",
    "Break down large assignments into smaller, manageable tasks.",
    "Try a digital detox for a few hours each weekend.",
    "Ask for help when you need it – it's a sign of strength.",
    "Read a book for pleasure, not for a class.",
    "Take a different route to class to change your perspective.",
    "Identify your most productive time of day and schedule tough tasks then.",
    "Organize your notes after each lecture to reinforce learning.",
    "Practice mindfulness while eating your meals.",
    "Set boundaries with friends or family who may be causing stress.",
    "Volunteer for a cause you care about to gain perspective.",
    "Limit your caffeine intake, especially in the afternoon.",
    "Watch a funny movie or TV show to de-stress.",
    "Take a hot shower or bath before bed to relax.",
    "Explore creative outlets like drawing, writing, or playing an instrument.",
    "Learn about imposter syndrome and strategies to combat it.",
    "Do a full body stretch when you wake up in the morning.",
    "Compliment a classmate or friend.",
    "Put your phone in another room while you study.",
    "Make a healthy snack for your next study session.",
    "Plan a visit home or a call with your family.",
    "Forgive yourself for not being perfect.",
    "Create a playlist of uplifting songs.",
    "Sit in a different spot in the library or classroom.",
    "Remind yourself of your long-term goals and why you're in school."
]

SUGGESTIONS_PROFESSIONAL = [
    "Set clear boundaries between your work and personal life.",
    "Use your paid time off to fully disconnect and recharge.",
    "Practice mindfulness or meditation for 5-10 minutes each day.",
    "Schedule short breaks throughout your workday to stretch and walk around.",
    "Define your 'end of day' with a consistent ritual, like a walk or closing your laptop.",
    "Turn off work notifications on your phone after hours.",
    "Prioritize tasks for the day and focus on one thing at a time.",
    "Delegate tasks when possible to manage your workload.",
    "Take a full lunch break away from your desk.",
    "Say 'no' to non-essential requests when your plate is full.",
    "Invest in an ergonomic chair and desk setup.",
    "Communicate your workload and capacity to your manager.",
    "Build a 'shutdown' routine at the end of your workday.",
    "Celebrate professional wins, no matter how small.",
    "Seek feedback regularly to avoid uncertainty and stress.",
    "Block out 'focus time' on your calendar for deep work.",
    "Identify and limit time spent with draining colleagues.",
    "Use your commute to listen to an engaging podcast or audiobook instead of checking emails.",
    "Plan something to look forward to after work.",
    "Stay hydrated throughout the day at your desk.",
    "Avoid eating lunch at your desk.",
    "Connect with a mentor for guidance and support.",
    "Organize your digital workspace and close unnecessary tabs.",
    "Practice the 'Pomodoro Technique' for focused work sprints.",
    "Learn to identify the signs of burnout in yourself and others.",
    "Advocate for mental health resources in your workplace.",
    "Take a 'micro-break' to look out the window and rest your eyes.",
    "Write down your accomplishments at the end of each week.",
    "Set realistic expectations for yourself and your projects.",
    "Find a work-best-friend to share challenges and successes with.",
    "Disconnect from work-related social media on weekends.",
    "Invest time in a hobby completely unrelated to your job.",
    "Go for a walk during one-on-one meetings if possible.",
    "Prepare for the next day the evening before to reduce morning stress.",
    "Practice active listening in meetings to stay present.",
    "Leave work on time as a rule, not an exception.",
    "Negotiate for flexible working hours if it suits your lifestyle.",
    "Improve your financial literacy to reduce money-related stress.",
    "Declutter your physical workspace regularly.",
    "Plan a vacation or staycation well in advance.",
   "Create a 'kudos' folder in your email to save positive feedback.",
    "Practice detaching your identity from your job title.",
    "Limit checking your email to specific times of the day.",
    "Learn a new skill that is not related to your career path.",
    "Make time for regular physical exercise.",
    "Ensure you are eating a nutritious lunch.",
    "Reflect on what aspects of your job you find most fulfilling.",
    "Schedule your annual physical and other health check-ups.",
    "End your day by creating a to-do list for tomorrow, then forget about it."
]

# --- Helper Functions ---
def load_resources(file_path):
    if not os.path.exists(file_path):
        return {"Latest Articles": [], "Research & Studies": [], "Suggestions": []}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"Latest Articles": [], "Research & Studies": [], "Suggestions": []}

def save_resources(file_path, resources):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(resources, f, indent=4, ensure_ascii=False)

def populate_files():
    # Student resources
    student_resources = load_resources(STUDENT_RESOURCES_PATH)
    student_resources["Latest Articles"] = STATIC_ARTICLES_STUDENT
    student_resources["Suggestions"] = SUGGESTIONS_STUDENT
    save_resources(STUDENT_RESOURCES_PATH, student_resources)
    print("Populated student resources with static articles and a large pool of suggestions.")

    # Professional resources
    professional_resources = load_resources(PROFESSIONAL_RESOURCES_PATH)
    professional_resources["Latest Articles"] = STATIC_ARTICLES_PROFESSIONAL
    professional_resources["Suggestions"] = SUGGESTIONS_PROFESSIONAL
    save_resources(PROFESSIONAL_RESOURCES_PATH, professional_resources)
    print("Populated professional resources with static articles and a large pool of suggestions.")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    populate_files()
    print("Static resource population complete.")
