import base64
import streamlit as st
import os
import requests

# Function to convert an image file to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Step 1: Specify the path to your image
image_path = str(os.getcwd())+"/app/Back.jpg"  # Ensure the image is in the same folder as this script or provide a full path

# Step 2: Convert the image to base64 format
base64_image = get_base64_image(image_path)

# Step 3: Correctly interpolate the base64 string into the markdown
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@400;700&display=swap');
    
    .stApp {{
        background-image: url("data:image/png;base64,{base64_image}");
        background-size: cover; /* Ensures the image covers the entire background */
        background-position: center; /* Centers the background image */
        background-repeat: no-repeat; /* Prevents repeating the image */
        font-family: 'Poppins', sans-serif; /* Modern font */
        padding-bottom: 100px; /* Ensure there's room for the input at the bottom */
        opacity: 1;
    }}

    .custom-header {{
        font-size: 36px;
        font-weight: bold;
        color: #FFFFFF;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, rgba(255, 94, 98, 1) 0%, rgba(255, 165, 0, 1) 100%);
        border-radius: 0px 0px 15px 15px;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 1000; /* Ensure it stays above other content */
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2); /* Slight shadow */
        font-family: 'Comic Neue', sans-serif;
    }}

    .stApp {{
        padding-top: 120px;
    }}

    .footer-input input {{
        width: 100% !important;
        padding: 12px !important;
        font-size: 16px !important;
        border-radius: 10px;
        border: 2px solid #ccc;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        background-color: #ffffff;
        color: #333333;
        transition: all 0.3s ease;
    }}

    .footer-input input::placeholder {{
        color: #040404 !important;
        opacity: 1 !important;
    }}

    .footer-input input:focus {{
        border-color: rgba(63,94,251,1);
        box-shadow: 0 0 5px rgba(63,94,251,0.5);
    }}

    .user-bubble {{
        background-color: #e6f7ff;
        padding: 12px;
        border-radius: 20px;
        color: #333333;
        max-width: 80%;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        word-wrap: break-word;
        opacity: 1;
    }}

    .bot-bubble {{
        background-color: #6050dc;
        padding: 12px;
        border-radius: 20px;
        color: #ffffff;
        text-align: left;
        max-width: 80%;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        word-wrap: break-word;
        transition: background-color 0.3s ease-in-out;
        opacity: 1;
    }}

    .bot-bubble:hover {{
        background-color: #4a3cb6;
    }}

    footer {{
        visibility: hidden;
    }}

    header {{
        visibility: hidden;
    }}
    </style>
    """, unsafe_allow_html=True)



# Add a custom header
st.markdown("<div class='custom-header'>HokieEATS</div>", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if "messages" not in st.session_state:
    st.session_state.messages = []  # List to store chat messages
if "user_input" not in st.session_state:
    st.session_state.user_input = ""  # To store user input text

# Create a container for the chat interface
chat_container = st.container()

def display_messages():
    with chat_container:
        for msg in st.session_state.messages:
            if msg["sender"] == "user":  # User messages
                col1, col2 = st.columns([4, 5])
                with col1:
                    st.markdown(f"""
                        <div class='user-bubble'>
                        {msg['message']}
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.empty()
            else:  # Bot messages
                col1, col2 = st.columns([5, 4])
                with col2:
                    st.markdown(f"""
                        <div class='bot-bubble'>
                        {msg['message']}
                        </div>
                    """, unsafe_allow_html=True)
                with col1:
                    st.empty()

def call_api(user_input):
    api_url = "https://vthackstomato.azurewebsites.net/api/yourtomato"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Prepare the chat history
    chat_history = [{"sender": msg["sender"], "message": msg["message"]} for msg in st.session_state.messages]
    
    payload = {
        "user_message": user_input,
        "chat_history": chat_history  # Include the chat history in the payload
    }

    try:
        # Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        res = response.json()
        print(res['response'])
        # Check if the response is successful
        if response.status_code == 200:
            return res['response']
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error occurred while calling the API: {e}"


# Function to handle user input and display new messages
def handle_user_input():
    user_input = st.session_state.user_input_text  # Get the user input
    if user_input:  # If there's input
        st.session_state.messages.append({"sender": "user", "message": user_input})  # Add user message

        # Call the API and get the bot response
        bot_response = call_api(user_input)

        # Append bot response to the message list
        st.session_state.messages.append({"sender": "bot", "message": bot_response})
        
        st.session_state.user_input_text = ""  # Clear the user inputs

# Input field and button for the user to type messages
input_placeholder = st.empty()

# Place the input at the footer
st.markdown('<div class="footer-input">', unsafe_allow_html=True)
user_input = input_placeholder.text_input("Type your message here...", value=st.session_state.user_input, key="user_input_text", on_change=handle_user_input)
st.markdown('</div>', unsafe_allow_html=True)

# Display the messages in the chat container
display_messages()