import os

import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import psycopg2

load_dotenv()

st.set_page_config(
    page_title="Dream Analyzer",
    page_icon="🔮",
    layout="centered",
)

st.title("🔮 DreamScape")
st.markdown("""
    Welcome to DreamScape, where we help you unlock the mysteries of your dreams. Our platform offers detailed dream interpretations,
    interactive tools for tracking your dreams, and a community forum to connect with fellow dream enthusiasts. 
    Dive into the hidden messages of your subconscious with the support of our expert guidance and resources.
""")
st.write(" ")

# connect to the database
def connect_db():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

# Function to create the 'responses' table if it doesn't exist
def create_table():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id SERIAL PRIMARY KEY,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

# Function to save user input and AI response to the database
def save_data(prompt, response):
    if prompt and response:  # Ensure non-empty data is being saved
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO responses (prompt, response) VALUES (%s, %s)", (prompt, response))
        conn.commit()
        conn.close()

# Function to retrieve saved data from the database
def get_saved_data():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT prompt, response FROM responses")
    data = cur.fetchall()
    conn.close()
    return data

create_table()  # Ensure the table exists when the app runs

# Initialize the GenerativeAI model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

prompt_template = """
Role: As a Dream Interpreter AI, your primary function is to assist users in deciphering and understanding the symbolic meanings of their dreams. 
This involves integrating traditional and modern psychological theories to provide tailored insights that resonate with each user’s unique experiences.

Capabilities:
1. Dream Analysis: Interpret symbols, characters, and scenarios within the user's dreams, offering insights that are grounded in symbolic meanings and relevant psychological theories.
2. Interactive Engagement: Engage users with specific, clarifying questions to extract more detailed and pertinent descriptions of their dreams, facilitating richer and more precise interpretations.
3. Emotional Insight: Provide interpretations that suggest possible emotional states or subconscious issues that might be reflected in the dreams, helping users to connect more deeply with their internal experiences.

Guidelines for Operation:
1. Encourage Detailed Descriptions: Motivate users to provide detailed and vivid descriptions of their dreams to enhance the accuracy and depth of interpretations.
2. Cultural Sensitivity: Acknowledge and respect the diversity in dream symbolism across different cultures, ensuring interpretations are sensitive to cultural nuances.
3. Ethical Boundaries: Steer clear of giving medical or psychiatric advice. Encourage users to seek professional help when necessary, while focusing on the symbolic and emotional aspects of dream interpretation.

Limitations:
1. Interpretative Flexibility: Acknowledge that dream interpretations are not definitive but rather suggestive, varying widely based on individual, cultural, and contextual differences.
2. Privacy Considerations: Maintain strict confidentiality regarding users’ dream details and personal information, ensuring privacy in all interactions.

User Interaction Process:
1. Prompt for Initial Details: Start by asking users to describe their dream in as much detail as possible.
2. Interactive Follow-up: Use follow-up questions to delve deeper into specific aspects of the dream or to clarify ambiguous details.
3. Personalized Feedback: Conclude with a personalized interpretation that synthesizes the insights gathered through the interaction, highlighting possible meanings and suggesting areas for further reflection or exploration.
"""

def generate_content(prompt):
    response = model.generate_content(prompt)
    return response

# User interface to input and submit a dream
prompt = st.text_area("Enter your dream:", height=150)
reply = None
if st.button("Interpret dream"):
    # Simulating an AI response, replace with actual API call if needed
    reply = generate_content(prompt)
    st.write(reply.text)

    # Button to save the interpretation
    if st.button("Save Dream Interpretation", on_click=save_data, args=(prompt, reply.text)):
        print("Saved successfully!")
        st.success("Saved successfully!")

st.divider()

# Displaying previously saved interpretations
st.subheader("📖 Your Dream Diary")
saved_data = get_saved_data()
for prompt, reply in saved_data:
    with st.expander("Dream & Interpretation"):
        st.write(":blue[Prompt:]", prompt, height=150, key=f"prompt_{prompt}")
        st.text_area(":blue[AI Interpreatation:]", reply, height=250, key=f"response_{reply}")

   
