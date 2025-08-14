import json
import requests
from io import BytesIO
from PIL import Image
import streamlit as st
import google.generativeai as genai
import base64


def generate_ai_avatar_by_HFModels():
    try:
        HUGGINGFACE_TOKEN = st.secrets.get("HUGGINGFACE_TOKEN")
        # Choose your model
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

        headers = {}
        if HUGGINGFACE_TOKEN:
            headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

        prompt = f"""
            Generate a professional profile photo matching these SPECIFIC characteristics:
            1. PERSON: {st.session_state['name']} ({st.session_state['age']} years old)
            2. GENDER: {st.session_state['gender']} (strictly follow this)
            3. OCCUPATION: {st.session_state['occupation']}

            STYLE REQUIREMENTS:
            - Corporate headshot, hyper-realistic
            - Gender-appropriate professional attire
            - {st.session_state['gender']}-typical facial features
            - Studio lighting, neutral gray background
            - High detail (256x256 resolution)

            RULES:
            - MUST respect specified gender
            - NO gender ambiguity
            - NO artistic interpretations
            - Focus on professional appearance
        """

        payload = {"inputs": prompt}

        with st.spinner("Generating AI avatar..."):
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()

            image_bytes = response.content
            image = Image.open(BytesIO(image_bytes))
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            st.session_state["user_photo"] = buffer.getvalue()
            st.success("AI avatar generated using Hugging Face!")

    except Exception as e:
        st.error(f"Error generating AI avatar with Stable Diffusion: {e}")


def generate_randomuserphotoByGender(gender):
    # Fetch random user photo
    try:
        st.info("Fetching random user photo...")
        random_user_response = requests.get(
            "https://randomuser.me/api/?gender="+gender)
        # print(persona_data["gender"])
        random_user_response.raise_for_status()
        random_user_data = random_user_response.json()

        if 'results' in random_user_data and random_user_data['results']:
            random_user = random_user_data['results'][0]
            if 'picture' in random_user and 'large' in random_user['picture']:
                photo_url = random_user['picture']['large']
                photo_response = requests.get(photo_url)
                photo_response.raise_for_status()
                photo_bytes = photo_response.content
                img = Image.open(BytesIO(photo_bytes))
                # Convert PIL Image to bytes for session state
                buffer = BytesIO()
                img.save(buffer, format="PNG")  # Or "JPEG"
                st.session_state["user_photo"] = buffer.getvalue()
              # Debug
            else:
                st.warning(
                    "Random user data did not contain a large photo URL.")
                st.session_state["user_photo"] = None
        else:
            st.warning("Failed to fetch random user data for photo.")
            st.session_state["user_photo"] = None

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching random user photo: {e}")
        st.session_state["user_photo"] = None
