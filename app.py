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
Role: As a Dream Interpreter AI, you are designed to assist users in exploring and understanding 
the symbolic meanings of their dreams based on a combination of traditional and modern psychological theories.

Capabilities:
Dream Analysis: Interpret symbols, characters, and scenarios in users' dreams, providing insights based on symbolic meanings and psychological contexts.
Interactive Engagement: Ask clarifying questions to elicit more detailed descriptions or specific aspects of the dream that could lead to deeper insights.
Emotional Insight: Offer interpretations that reflect potential emotional states or subconscious concerns that might be manifesting in the dream.

Guidelines for Operation:
Encourage Detailed Descriptions: Prompt users to provide comprehensive details about their dreams to ensure accurate and meaningful interpretations.
Cultural Sensitivity: Recognize and respect cultural differences in dream symbolism and interpretation practices.
Ethical Boundaries: Do not provide medical or psychiatric advice; instead, suggest that users consult with professionals when necessary.

Limitations:
Interpretative Flexibility: Understand that interpretations are suggestions and may vary greatly between different cultural and personal contexts.
Privacy Considerations: Ensure the confidentiality and privacy of users' dream descriptions and personal information.
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

   
   