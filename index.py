import streamlit as st
import google.generativeai as genai
import json
import base64
import requests
import pdfkit

from lib.utils import load_css
from io import BytesIO
from PIL import Image

# Page Title
st.set_page_config(page_title="User Persona Builder",
                   page_icon=":rocket:", layout="wide")

# Load Styles
load_css()

# Safely load API key with error handling
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("🔐 API key missing! Please add it to secrets.toml")
    st.stop()  # Halt the app if key is missing
except Exception as e:
    st.error(f"🚨 API error: {str(e)}")
    st.stop()


# Initialize the form fields


def initialize_fields():
    st.session_state["active_expander"] = "basic"  # Default open expander
    # Track if an expander was clicked
    st.session_state["expander_changed"] = False

    st.session_state["submitted"] = False
    st.session_state["name"] = ""
    st.session_state["age"] = 0
    st.session_state["gender"] = "Male"
    st.session_state["occupation"] = ""
    st.session_state["location"] = ""
    st.session_state["user_photo"] = None

    st.session_state["goals"] = ""
    st.session_state["frustrations"] = ""
    st.session_state["motivations"] = ""
    st.session_state["needs"] = ""
    st.session_state["skills"] = ""
    st.session_state["pain_points"] = ""

    st.session_state["tech_savviness"] = 3
    st.session_state["interests"] = []
    st.session_state["platforms"] = []

    # Template Fields
    st.session_state["selected_template"] = "basic"  # Default template
    st.session_state["templates"] = {
        "basic": "Simple clean layout",
        "modern": "Modern card with icons",
        "professional": "Corporate style",
        "creative": "Colorful creative layout"
    }
    # Default template
    st.session_state["selected_userphoto_modelgeneration"] = "randomuser"
    st.session_state["userphoto_modelgeneration"] = {
        "randomuser": "From Random User Website API",
        "stability": "AI Model",
        "huggingface": "Stable Diffusion XL Base Model"
    }
    st.session_state["initialized"] = False


def is_file_size_valid(photo_file):
    if photo_file is not None:
        if photo_file.size > 1 * 1024 * 1024:  # 1MB in bytes
            st.warning("File size must be under 1MB.")
            st.session_state["user_photo"] = None
        else:
            st.session_state["user_photo"] = photo_file
    else:
        st.session_state["user_photo"] = None


# Initialize session state if not already present
if "submitted" not in st.session_state:
    initialize_fields()
elif not st.session_state.get("initialized", False):  # Add this check
    initialize_fields()
    st.session_state["initialized"] = True

# Define functions


def reset_form():
    initialize_fields()
    st.rerun()


def submit_form():
    required_fields = ["name", "occupation", "goals"]
    missing = [field for field in required_fields if not st.session_state[field]]

    if missing:
        st.error(f"Missing required fields: {', '.join(missing)}")
    else:
        st.session_state["submitted"] = True
        uploaded_file = st.session_state.get("user_photo_file")
        if uploaded_file is not None:
            try:
                image_bytes = uploaded_file.read()
                st.session_state["user_photo"] = image_bytes
                # print(
                #     f"User photo size (bytes) after upload in submit_form: {len(image_bytes)}")
            except Exception as e:
                st.error(f"Error reading uploaded file in submit_form: {e}")
                st.session_state["user_photo"] = None
        else:
            # Explicitly set to None if no upload
            st.session_state["user_photo"] = None
        st.rerun()


def generate_ai_avatar(name, occupation):
    try:
        # model = genai.GenerativeModel("gemini-2.0-flash")
        stability_key = st.secrets.get("STABILITY_API_KEY")
        print(f"Retrieved Stability API Key: '{stability_key}'")
        print(f"Nam: '{name}'")
        print(f"Occ: '{occupation}'")

        if not stability_key:
            st.error("Stability API key is missing. Please add it to secrets.toml")
            return None

        url = "https://api.stability.ai/v2beta/stable-image/generate/core"

        prompt = f"""
        Generate a professional profile photo for:
        Name: {name}
        Occupation: {occupation}

        Style: Corporate headshot, realistic, studio lighting
        Requirements:
        - Neutral background
        - Business professional attire
        - Diverse representation
        - High resolution (256x256)
        """

        headers = {
            "Authorization": f"Bearer {stability_key}",
            # "Content-Type": "application/json"
            "Accept": "image/*"
        }

        files = {"none": ''}  # As per the example

        data = {
            "prompt": prompt,
            "output_format": "png",
            "width": "150",  # Keep as strings for consistency
            "height": "150",  # Keep as strings for consistency
        }

        # response = model.generate_content(prompt)

        try:
            response = requests.post(
                url, headers=headers, files=files, data=data)
            print(f"Status Code: {response.status_code}")
            # print(f"Response Text: {response.text}")
            response.raise_for_status()

            image_bytes = response.content
            img = Image.open(BytesIO(image_bytes))

            # Convert PIL Image to bytes for session state
            buffer = BytesIO()
            img.save(buffer, format="PNG")  # Or "JPEG"

            # Store the image in session state
            st.session_state["user_photo"] = buffer.getvalue()

        except requests.exceptions.RequestException as e:
            st.error(f"Avatar generation failed: {str(e)}")
            st.session_state["user_photo"] = None
            return None
        except Exception as e:
            st.error(f"⚠️ Avatar generation failed: {str(e)}")
            st.session_state["user_photo"] = None
            return None

    except Exception as e:
        st.error(f"⚠️ Avatar generation failed: {str(e)}")
        st.session_state["user_photo"] = None
        return None


def generate_ai_avatar_by_HFModels():
    try:
        HUGGINGFACE_TOKEN = st.secrets.get("HUGGINGFACE_TOKEN")
        # Choose your model
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

        headers = {}
        if HUGGINGFACE_TOKEN:
            headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

        prompt = f"""
        Generate a professional profile photo for:
        Name: {st.session_state['name']}
        Age: {st.session_state['age']}
        Gender: {st.session_state['gender']}
        Occupation: {st.session_state['occupation'].lower()}

        Style: Corporate headshot, realistic, studio lighting
        Requirements:
        - Neutral background
        - Business professional attire
        - Diverse representation
        - High resolution (256x256)
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


def generate_ai_persona():
    try:
        # Call the Model
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Define allowed options (must match your form exactly)
        interest_options = ["Technology", "Design", "Music", "Sports",
                            "Reading", "Travel", "Gaming", "Fitness"]
        platform_options = ["Mobile", "Desktop",
                            "Tablet", "Smartwatch", "VR/AR"]
        gender_options = ["Male", "Female", "Non-Binary", "Other"]

        prompt = f"""Generate a realistic user persona with these REQUIREMENTS:
        - Interests MUST be from: {", ".join(interest_options)}
        - Platforms MUST be from: {", ".join(platform_options)}
        - Gender MUST be from: {", ".join(gender_options)}
        - Tech savviness MUST be 1-5
        - Return valid JSON format like this example:
        {{
            "name": "Alex Chen",
            "age": 28,
            "gender": "Non-Binary",
            "occupation": "UX Designer",
            "location": "Berlin",
            "goals": "Improve accessibility in tech products",
            "frustrations": "Slow design approval processes",
            "motivations": "Creating inclusive digital experiences",
            "needs": "Better collaboration tools",
            "skills": "Figma, User Research",
            "pain_points": "Limited budget for user testing",
            "tech_savviness": 4,
            "interests": ["Design", "Technology"],
            "platforms": ["Desktop", "Tablet"]
        }}"""

        response = model.generate_content(prompt)
        response_text = response.text

        # Clean JSON response
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]  # Remove markdown wrappers
        response_text = response_text.strip()

        persona_data = json.loads(response_text)
        # print(f"Generated Persona Data: {persona_data}")  # Add this line
        # print(f"Generated Name: {persona_data.get('name')}")

        # Update name
        if "name" in persona_data:
            st.session_state["name"] = persona_data["name"]
            # print(f"Session State Name updated to: {st.session_state['name']}")

        # Handle user-uploaded photo
        uploaded_file = st.session_state.get("user_photo_file")
        if uploaded_file is not None:
            try:
                st.info("Using uploaded photo...")
                photo_bytes = uploaded_file.read()
                st.session_state["user_photo"] = photo_bytes
                print(
                    f"User photo size (bytes) from upload in generate_ai: {len(photo_bytes)}")
            except Exception as e:
                st.error(f"Error reading uploaded file in generate_ai: {e}")
                st.session_state["user_photo"] = None
        else:
            # Fetch user photo generation model
            if st.session_state["selected_userphoto_modelgeneration"] == "randomuser":
                # Random User Photo By Gender - Generation
                generate_randomuserphotoByGender(persona_data["gender"])
            elif st.session_state["selected_userphoto_modelgeneration"] == "stability":
                # AI Photo Generation
                generate_ai_avatar(
                    persona_data["name"], persona_data["occupation"])
            else:
                # Generate AI Photo using Hugging Face Models
                generate_ai_avatar_by_HFModels()

        # 1. Validate interests
        if "interests" in persona_data:
            if isinstance(persona_data["interests"], str):  # Handle string input
                persona_data["interests"] = [x.strip()
                                             for x in persona_data["interests"].split(",")]
            valid_interests = [
                i for i in persona_data["interests"]
                if i in interest_options
            ]
            st.session_state["interests"] = valid_interests or []

        # 2. Validate platforms
        if "platforms" in persona_data:
            if isinstance(persona_data["platforms"], str):  # Handle string input
                persona_data["platforms"] = [x.strip()
                                             for x in persona_data["platforms"].split(",")]
            valid_platforms = [
                p for p in persona_data["platforms"]
                if p in platform_options
            ]
            st.session_state["platforms"] = valid_platforms or []

        # 3. Validate gender
        if "gender" in persona_data:
            if persona_data["gender"] not in gender_options:
                persona_data["gender"] = "Other"

        # 4. Validate tech savviness
        if "tech_savviness" in persona_data:
            try:
                ts = int(persona_data["tech_savviness"])
                persona_data["tech_savviness"] = max(1, min(5, ts))
            except (ValueError, TypeError):
                persona_data["tech_savviness"] = 3

        # Update all valid fields
        for field in ["name", "age", "gender", "occupation", "location",
                      "goals", "frustrations", "motivations", "needs",
                      "skills", "pain_points", "tech_savviness"]:
            if field in persona_data:
                st.session_state[field] = persona_data[field]

        # Store success state and trigger rerun
        # st.session_state["ai_generation_success"] = True
        # st.session_state.pop("ai_generation_success",
        #                      None)  # Remove the old flag
        st.session_state["submitted"] = True

        st.rerun()  # ← THIS IS THE CRUCIAL LINE TO ADD

    except json.JSONDecodeError:
        st.error("Invalid JSON response from AI. Raw response:")
        st.code(response_text)
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with Random User API: {e}")
    except Exception as e:
        st.error(f"AI generation failed: {str(e)}")


def export_persona(format="pdf"):
    if format == "pdf":
        try:
            template = st.session_state.get('selected_template', 'basic')
            persona_data = {
                k: v for k, v in st.session_state.items() if not k.startswith("_")}
            image_base64 = persona_data.get('user_photo_base64', '')
            image_html = f'<img src="data:image/png;base64,{image_base64}" style="width: 100px; height: auto; border-radius: 50%; object-fit: cover; margin-bottom: 10px;">' if image_base64 else ''

            if template == "basic":
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: sans-serif; }}
                        .persona-card-basic {{ border: 1px solid #ddd; padding: 20px; border-radius: 5px; background-color: #f9f9f9; }}
                        .persona-header {{ text-align: center; margin-bottom: 15px; }}
                        .persona-header h2 {{ margin-bottom: 5px; color: #333; }}
                        .persona-header .subtitle {{ color: #777; font-size: 0.9em; }}
                        .persona-section {{ margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee; }}
                        .persona-section:last-child {{ border-bottom: none; }}
                        .persona-section h3 {{ color: #555; margin-top: 0; margin-bottom: 10px; }}
                        .persona-section p {{ margin-bottom: 5px; color: #444; }}
                        .persona-section p strong {{ font-weight: bold; color: #333; margin-right: 5px; }}
                        .user-photo {{ text-align: center; margin-bottom: 10px; }}
                        .user-photo img {{ width: 100px; height: auto; border-radius: 50%; object-fit: cover; }}
                    </style>
                </head>
                <body>
                    <div class="persona-card-basic">
                        <div class="user-photo">{image_html}</div>
                        <div class="persona-header">
                            <h2>{persona_data.get('name', '')}</h2>
                            <p class="subtitle">{persona_data.get('occupation', '')} • {persona_data.get('location', '')} • {persona_data.get('age', '')} years</p>
                        </div>
                        <div class="persona-section">
                            <h3>📌 Basic Information</h3>
                            <p><strong>Gender:</strong> {persona_data.get('gender', '')}</p>
                            <p><strong>Tech Savviness:</strong> {'⭐' * persona_data.get('tech_savviness', 0)}</p>
                        </div>
                        <div class="persona-section">
                            <h3>🎯 Goals & Motivations</h3>
                            <p><strong>Goals:</strong> {persona_data.get('goals', '')}</p>
                            <p><strong>Motivations:</strong> {persona_data.get('motivations', '')}</p>
                        </div>
                        <div class="persona-section">
                            <h3>⚠️ Pain Points</h3>
                            <p><strong>Frustrations:</strong> {persona_data.get('frustrations', '')}</p>
                            <p><strong>Challenges:</strong> {persona_data.get('pain_points', '')}</p>
                        </div>
                        <div class="persona-section">
                            <h3>🛠 Skills & Needs</h3>
                            <p><strong>Skills:</strong> {persona_data.get('skills', '')}</p>
                            <p><strong>Needs:</strong> {persona_data.get('needs', '')}</p>
                        </div>
                        <div class="persona-section">
                            <h3>🌐 Preferences</h3>
                            <p><strong>Interests:</strong> {', '.join(persona_data.get('interests', []) or [])}</p>
                            <p><strong>Platforms:</strong> {', '.join(persona_data.get('platforms', []) or [])}</p>
                        </div>
                    </div>
                </body>
                </html>
                """.strip()
            elif template == "modern":
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: sans-serif; }}
                        .persona-card-modern-stacked {{ background-color: #fff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); padding: 25px; }}
                        .user-photo-modern-stacked img {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; margin: 0 auto 15px auto; display: block; }}
                        .modern-header {{ text-align: center; margin-bottom: 20px; }}
                        .modern-header h2 {{ color: #2c3e50; margin-bottom: 8px; }}
                        .modern-header .subtitle {{ color: #777; font-size: 0.9em; margin-bottom: 5px; }}
                        .modern-header .tech-savvy {{ color: #3498db; font-size: 0.95em; }}
                        .modern-section {{ margin-bottom: 18px; padding-bottom: 12px; border-bottom: 1px solid #eee; }}
                        .modern-section:last-child {{ border-bottom: none; }}
                        .modern-section h3 {{ color: #2c3e50; margin-top: 0; margin-bottom: 10px; font-size: 1.15em; }}
                        .modern-section p {{ color: #555; margin-bottom: 0; font-size: 0.95em; line-height: 1.6; }}
                    </style>
                </head>
                <body>
                    <div class="persona-card-modern-stacked">
                        <div class="user-photo-modern-stacked">{image_html}</div>
                        <div class="modern-header">
                            <h2>{persona_data.get('name', '')}</h2>
                            <p class="subtitle">{persona_data.get('occupation', '')} • {persona_data.get('location', '')} • {persona_data.get('age', '')} years</p>
                            <div class="tech-savvy"><strong>Tech Savviness:</strong> {'⭐' * persona_data.get('tech_savviness', 0)}</div>
                        </div>
                        <div class="modern-section">
                            <h3>🎯 Goals</h3>
                            <p>{persona_data.get('goals', '')}</p>
                        </div>
                        <div class="modern-section">
                            <h3>💡 Motivations</h3>
                            <p>{persona_data.get('motivations', '')}</p>
                        </div>
                        <div class="modern-section">
                            <h3>⚠️ Frustrations</h3>
                            <p>{persona_data.get('frustrations', '')}</p>
                        </div>
                        <div class="modern-section">
                            <h3>💔 Pain Points</h3>
                            <p>{persona_data.get('pain_points', '')}</p>
                        </div>
                        <div class="modern-section">
                            <h3>🛠 Skills</h3>
                            <p>{persona_data.get('skills', '')}</p>
                        </div>
                        <div class="modern-section">
                            <h3>🌐 Interests</h3>
                            <p>{', '.join(persona_data.get('interests', []) or [])}</p>
                        </div>
                        <div class="modern-section">
                            <h3>📱 Platforms</h3>
                            <p>{', '.join(persona_data.get('platforms', []) or [])}</p>
                        </div>
                        <div class="modern-section">
                            <h3>👤 Gender</h3>
                            <p>{persona_data.get('gender', '')}</p>
                        </div>
                    </div>
                </body>
                </html>
                """.strip()
            elif template == "professional":
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: sans-serif; }}
                        .persona-card-professional {{ border: 1px solid #aaa; padding: 20px; border-radius: 3px; background-color: #f0f0f0; }}
                        .professional-header {{ text-align: center; margin-bottom: 20px; }}
                        .user-photo-professional img {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; margin-bottom: 15px; }}
                        .professional-header h2 {{ color: #222; margin-bottom: 5px; }}
                        .professional-header .title {{ color: #555; font-size: 1em; margin-bottom: 3px; }}
                        .professional-header .location {{ color: #777; font-size: 0.9em; }}
                        .professional-section {{ margin-bottom: 18px; padding-bottom: 12px; border-bottom: 1px solid #ccc; }}
                        .professional-section:last-child {{ border-bottom: none; }}
                        .professional-section h3 {{ color: #333; margin-top: 0; margin-bottom: 10px; font-size: 1.2em; border-bottom: 2px solid #555; padding-bottom: 5px; display: flex; align-items: center; gap: 8px; }}
                        .professional-section p {{ margin-bottom: 8px; color: #444; line-height: 1.5; display: flex; align-items: center; gap: 8px; }}
                        .professional-section p strong {{ font-weight: bold; color: #222; margin-right: 5px; }}
                    </style>
                </head>
                <body>
                    <div class="persona-card-professional">
                        <div class="professional-header">
                            <div class="user-photo-professional">{image_html}</div>
                            <h2>{persona_data.get('name', '')}</h2>
                            <p class="title">{persona_data.get('occupation', '')}</p>
                            <p class="location">📍 {persona_data.get('location', '')} | 🗓️ Age: {persona_data.get('age', '')}</p>
                        </div>
                        <div class="professional-section">
                            <h3>👤 About</h3>
                            <p><strong>Gender:</strong> {persona_data.get('gender', '')}</p>
                            <p><strong>💻 Tech Savviness:</strong> Level {persona_data.get('tech_savviness', 0)}</p>
                        </div>
                        <div class="professional-section">
                            <h3>💼 Professional Profile</h3>
                            <p><strong>🎯 Goals:</strong> {persona_data.get('goals', '')}</p>
                            <p><strong>🚀 Motivations:</strong> {persona_data.get('motivations', '')}</p>
                            <p><strong> skills:</strong> {persona_data.get('skills', '')}</p>
                        </div>
                        <div class="professional-section">
                            <h3>⚠️ Challenges & Needs</h3>
                            <p><strong>😠 Frustrations:</strong> {persona_data.get('frustrations', '')}</p>
                            <p><strong>💔 Pain Points:</strong> {persona_data.get('pain_points', '')}</p>
                            <p><strong>✅ Needs:</strong> {persona_data.get('needs', '')}</p>
                        </div>
                        <div class="professional-section">
                            <h3>🌐 Preferences</h3>
                            <p><strong>❤️ Interests:</strong> {', '.join(persona_data.get('interests', []) or [])}</p>
                            <p><strong>📱 Platforms:</strong> {', '.join(persona_data.get('platforms', []) or [])}</p>
                        </div>
                    </div>
                </body>
                </html>
                """.strip()
            elif template == "creative":
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: sans-serif; }}
                        .persona-card-creative {{ background-color: #e0f7fa; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08); border: 2px solid #b2ebf2; }}
                        .creative-header {{ text-align: center; margin-bottom: 25px; }}
                        .user-photo-creative img {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; margin-bottom: 15px; }}
                        .creative-header h1 {{ color: #00838f; margin-bottom: 5px; font-size: 2.5em; }}
                        .creative-header .tagline {{ color: #26a69a; font-size: 1.1em; }}
                        .creative-section {{ margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px dashed #80cbc4; }}
                        .creative-section:last-child {{ border-bottom: none; }}
                        .creative-section h2 {{ color: #00acc1; margin-top: 0; margin-bottom: 12px; font-size: 1.8em; display: flex; align-items: center; gap: 8px; }}
                        .creative-section p {{ margin-bottom: 10px; color: #333; line-height: 1.6; display: flex; align-items: center; gap: 8px; }}
                        .creative-section p strong {{ font-weight: bold; color: #00695c; margin-right: 5px; }}
                    </style>
                </head>
                <body>
                    <div class="persona-card-creative">
                        <div class="creative-header">
                            <div class="user-photo-creative">{image_html}</div>
                            <h1>✨ {persona_data.get('name', '')} ✨</h1>
                            <p class="tagline">💼 {persona_data.get('occupation', '')} | 🗓️ {persona_data.get('age', '')} | 📍 {persona_data.get('location', '')}</p>
                        </div>
                        <div class="creative-section">
                            <h2>🌍 My World</h2>
                            <p><strong>👤 Gender:</strong> {persona_data.get('gender', '')}</p>
                            <p><strong>💻 Tech Level:</strong> {persona_data.get('tech_savviness', 0)}/5</p>
                            <p><strong>❤️ Passions:</strong> {', '.join(persona_data.get('interests', []) or [])}</p>
                            <p><strong>📱 Platforms I Use:</strong> {', '.join(persona_data.get('platforms', []) or [])}</p>
                        </div>
                        <div class="creative-section">
                            <h2>🚀 What Drives Me</h2>
                            <p><strong>🎯 My Goals:</strong> {persona_data.get('goals', '')}</p>
                            <p><strong>💡 My Motivations:</strong> {persona_data.get('motivations', '')}</p>
                        </div>
                        <div class="creative-section">
                            <h2>🚧 My Challenges</h2>
                            <p><strong>😠 Frustrations:</strong> {persona_data.get('frustrations', '')}</p>
                            <p><strong>💔 Pain Points:</strong> {persona_data.get('pain_points', '')}</p>
                            <p><strong>✅ My Needs:</strong> {persona_data.get('needs', '')}</p>
                            <p><strong> skills:</strong> {persona_data.get('skills', '')}</p>
                        </div>
                    </div>
                </body>
                </html>
                """.strip()
            else:
                html_content = f"""
                <html>
                    <head>
                        <style> body {{ font-family: sans-serif; }} </style>
                    </head>
                    <body>
                        <h1>{persona_data.get('name', 'User Persona')}</h1>
                        <p>Occupation: {persona_data.get('occupation', '')}</p>
                    </body>
                </html>
                """.strip()

            pdf_bytes = pdfkit.from_string(html_content, output_path=False)

            col_rspace1, col_download_btn, col_st_rspace2 = st.columns(
                [0.05, 0.90, 0.05])

            with col_download_btn:
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=f"{persona_data.get('name', 'persona').lower().replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    type="primary",
                    key="pdf_download_button"
                )

        except Exception as e:
            st.error(f"Failed to generate PDF: {str(e)}")

        except Exception as e:
            st.error(f"Failed to generate JSON: {str(e)}")


# Persona Container - Start Section
st.markdown("<div class='persona-container'>", unsafe_allow_html=True)

# Page Heading
st.markdown("<h1 class='persona-header'>User Persona Builder</h1>",
            unsafe_allow_html=True)

# Two Section
col1, col2 = st.columns([0.5, 0.6])

# Left Column
with col1:
    st.subheader("Enter Persona Details")

    # Persona Basic Information
    with st.expander("🔹 Basic Information", expanded=st.session_state.get("active_expander") == "basic"):
        if st.session_state.get("active_expander") != "basic":
            st.session_state["active_expander"] = "basic"
            st.session_state["expander_changed"] = True

        st.session_state["name"] = st.text_input(
            "Name", value=st.session_state["name"])
        st.session_state["age"] = st.number_input(
            "Age", min_value=0, max_value=100, step=1, value=st.session_state["age"])
        st.session_state["gender"] = st.selectbox("Gender", ["Male", "Female", "Non-Binary", "Other"], index=[
                                                  "Male", "Female", "Non-Binary", "Other"].index(st.session_state["gender"]))
        st.session_state["occupation"] = st.text_input(
            "Occupation", value=st.session_state["occupation"])
        st.session_state["location"] = st.text_input(
            "Location", value=st.session_state["location"])
        st.session_state["user_photo_file"] = st.file_uploader(
            "Upload Photo (Optional)", type=['jpg', 'png', 'jpeg'])

    # Persona Insights
    with st.expander("💡 Personal Insights", expanded=st.session_state.get("active_expander") == "insights"):
        if st.session_state.get("active_expander") != "insights":
            st.session_state["active_expander"] = "insights"
            st.session_state["expander_changed"] = True

        st.session_state["goals"] = st.text_area(
            "Goals", value=st.session_state["goals"], placeholder="What does the user want to achieve?")
        st.session_state["frustrations"] = st.text_area(
            "Frustrations", value=st.session_state["frustrations"], placeholder="What challenges does the user face?")
        st.session_state["motivations"] = st.text_area(
            "Motivations", value=st.session_state["motivations"], placeholder="What drives the user?")
        st.session_state["needs"] = st.text_area(
            "Needs", value=st.session_state["needs"], placeholder="Essential requirements for the user?")
        st.session_state["skills"] = st.text_area(
            "Skills", value=st.session_state["skills"], placeholder="User's strengths?")
        st.session_state["pain_points"] = st.text_area(
            "Pain Points", value=st.session_state["pain_points"], placeholder="Specific problems faced?")

    # Persona Additional Information
    with st.expander("⚙️ Additional Information", expanded=st.session_state.get("active_expander") == "additional"):
        if st.session_state.get("active_expander") != "additional":
            st.session_state["active_expander"] = "additional"
            st.session_state["expander_changed"] = True

        st.session_state["tech_savviness"] = st.slider(
            "Tech Savviness (1=Low, 5=High)", min_value=1, max_value=5, value=st.session_state["tech_savviness"])
        # Define allowed options
        interest_options = ["Technology", "Design", "Music", "Sports",
                            "Reading", "Travel", "Gaming", "Fitness"]

        # Get current interests from session state
        current_interests = st.session_state.get("interests", [])

        # Filter out any invalid interests
        valid_interests = [interest for interest in current_interests
                           if interest in interest_options]

        # Create the multiselect with safe defaults
        st.session_state["interests"] = st.multiselect(
            "Select Interests",
            options=interest_options,
            default=valid_interests  # ← Only includes valid options
        )
        st.session_state["platforms"] = st.multiselect("Preferred Platforms", [
                                                       "Mobile", "Desktop", "Tablet", "Smartwatch", "VR/AR"], default=st.session_state["platforms"])

    # Template Options
    with st.expander("🎨 Template Options", expanded=False):
        st.session_state["selected_template"] = st.radio(
            "Select Display Template",
            options=list(st.session_state["templates"].keys()),
            format_func=lambda x: f"{x.capitalize()} - {st.session_state['templates'][x]}",
            index=list(st.session_state["templates"].keys()).index(
                st.session_state["selected_template"])
        )

        st.session_state["selected_userphoto_modelgeneration"] = st.radio(
            "Select Image Generation Type",
            options=list(st.session_state["userphoto_modelgeneration"].keys()),
            format_func=lambda x: f"{x.capitalize()} - {st.session_state['userphoto_modelgeneration'][x]}",
            index=list(st.session_state["userphoto_modelgeneration"].keys()).index(
                st.session_state["selected_userphoto_modelgeneration"])
        )

    col_space1, col_generate_ai, col_space2 = st.columns([
        0.05, 0.990, 0.05])

    with col_generate_ai:
        if st.button("Generate using AI", key="generate_ai", help="Auto-generate persona using AI", type="primary", use_container_width=True):
            with st.spinner("Generating AI Persona and Avatar..."):
                generated_persona = generate_ai_persona()
                if generated_persona and "user_photo" in st.session_state and st.session_state["user_photo"] is not None:
                    st.session_state["submitted"] = True
                    st.rerun()
                elif generated_persona:  # Persona data was likely generated but no avatar
                    st.session_state["submitted"] = True
                    st.rerun()
                else:
                    st.error("Failed to generate AI persona.")
    # Modify this block:
    if st.session_state.get("ai_generation_success", False):
        st.session_state["submitted"] = True
        st.session_state["ai_generation_success"] = False  # Reset it
        st.rerun()
    elif st.session_state.get("generating_avatar", False):
        st.info("Generating avatar...")

    # Buttons
    cols_space_first, col_reset, col_submit, cols_space_last = st.columns([
        0.1, 0.2, 0.3, 0.1])

    with col_reset:
        if st.button("Reset", key="reset", help="Clear form", use_container_width=True):
            reset_form()

    with col_submit:
        if st.button("Submit", key="submit", help="Submit persona", type="primary", use_container_width=True):
            submit_form()

    # Right after your button click handler in the UI section:
    if st.session_state.get("ai_generation_success", False):
        st.success("✅ AI persona generated successfully!")
        st.session_state["ai_generation_success"] = False  # Reset the flag

    if st.session_state.get("submitted", False):
        st.markdown(
            "<div class='full-width-success'><b>✅ User Persona Submitted Successfully</b></div>", unsafe_allow_html=True)

with col2:
    st.markdown("<h3>Persona Preview</h3>", unsafe_allow_html=True)
    # print(f"Submitted state in col2: {st.session_state.get('submitted')}")
    user_photo_bytes = st.session_state.get('user_photo')
    image_html = ""  # Initialize an empty image_html

    if st.session_state.get("submitted", False):
        if user_photo_bytes is not None:
            try:
                base64_image = base64.b64encode(
                    user_photo_bytes).decode("utf-8")
                image_html = f'<img src="data:image/png;base64,{base64_image}" alt="User Photo" style="width: 150px; height: 150px; border-radius: 50%; margin-bottom: 10px;">'
            except Exception as e:
                st.error(f"Error encoding image for preview: {e}")
        else:
            st.info("No photo uploaded or generated.")
        # if st.session_state.get("user_photo") is not None:
        #     from PIL import Image
        #     from io import BytesIO
        #     try:
        #         image_bytes = st.session_state["user_photo"]
        #         image = Image.open(BytesIO(image_bytes))
        #         st.image(image, width=150, caption="Random User Profile")
        #     except Exception as e:
        #         st.error(f"Error displaying image from bytes in col2: {e}")
        # else:
        #     st.info("No photo generated or uploaded yet (in col2).")

        template = st.session_state["selected_template"]

        if template == "basic":
            st.markdown(f"""
            <div class="persona-card-basic">
                <div class="user-photo" style="text-align: center;">{image_html}</div>
                <div class="persona-header">
                    <h2>{st.session_state['name']}</h2>
                    <p class="subtitle">{st.session_state['occupation']} • {st.session_state['location']} • {st.session_state['age']} years</p>
                </div>
                <div class="persona-section">
                    <h3>📌 Basic Information</h3>
                    <p><strong>Gender:</strong> {st.session_state['gender']}</p>
                    <p><strong>Tech Savviness:</strong> {"⭐" * st.session_state['tech_savviness']}</p>
                </div>
                <div class="persona-section">
                    <h3>🎯 Goals & Motivations</h3>
                    <p><strong>Goals:</strong> {st.session_state['goals']}</p>
                    <p><strong>Motivations:</strong> {st.session_state['motivations']}</p>
                </div>
                <div class="persona-section">
                    <h3>⚠️ Pain Points</h3>
                    <p><strong>Frustrations:</strong> {st.session_state['frustrations']}</p>
                    <p><strong>Challenges:</strong> {st.session_state['pain_points']}</p>
                </div>
                <div class="persona-section">
                    <h3>🛠 Skills & Needs</h3>
                    <p><strong>Skills:</strong> {st.session_state['skills']}</p>
                    <p><strong>Needs:</strong> {st.session_state['needs']}</p>
                </div>
                <div class="persona-section">
                    <h3>🌐 Preferences</h3>
                    <p><strong>Interests:</strong> {', '.join(st.session_state['interests']) if st.session_state['interests'] else 'None'}</p>
                    <p><strong>Platforms:</strong> {', '.join(st.session_state['platforms']) if st.session_state['platforms'] else 'None'}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif template == "modern":
            st.markdown(f"""
            <div class="persona-card-modern-stacked">
                <div class="user-photo-modern-stacked" style="text-align: center;">{image_html}</div>
                <div class="modern-header">
                    <h2>{st.session_state['name']}</h2>
                    <p class="subtitle">{st.session_state['occupation']} • {st.session_state['location']} • {st.session_state['age']} years</p>
                    <div class="tech-savvy"><strong>Tech Savviness:</strong> {"⭐" * st.session_state['tech_savviness']}</div>
                </div>
                <div class="modern-section">
                    <h3>🎯 Goals</h3>
                    <p>{st.session_state['goals']}</p>
                </div>
                <div class="modern-section">
                    <h3>💡 Motivations</h3>
                    <p>{st.session_state['motivations']}</p>
                </div>
                <div class="modern-section">
                    <h3>⚠️ Frustrations</h3>
                    <p>{st.session_state['frustrations']}</p>
                </div>
                <div class="modern-section">
                    <h3>💔 Pain Points</h3>
                    <p>{st.session_state['pain_points']}</p>
                </div>
                <div class="modern-section">
                    <h3>🛠 Skills</h3>
                    <p>{st.session_state['skills']}</p>
                </div>
                <div class="modern-section">
                    <h3>🌐 Interests</h3>
                    <p>{', '.join(st.session_state['interests']) if st.session_state['interests'] else 'None'}</p>
                </div>
                <div class="modern-section">
                    <h3>📱 Platforms</h3>
                    <p>{', '.join(st.session_state['platforms']) if st.session_state['platforms'] else 'None'}</p>
                </div>
                <div class="modern-section">
                    <h3>👤 Gender</h3>
                    <p>{st.session_state['gender']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif template == "professional":
            st.markdown(f"""
            <div class="persona-card-professional">
                <div class="professional-header">
                    <div class="user-photo-professional" style="text-align: center;">{image_html}</div>
                    <h2>{st.session_state['name']}</h2>
                    <p class="title">{st.session_state['occupation']}</p>
                    <p class="location">📍 {st.session_state['location']} | d Age: {st.session_state['age']}</p>
                </div>
                <div class="professional-section">
                    <h3>👤 About</h3>
                    <p><strong>Gender:</strong> {st.session_state['gender']}</p>
                    <p><strong>💻 Tech Savviness:</strong> Level {st.session_state['tech_savviness']}</p>
                </div>
                <div class="professional-section">
                    <h3>💼 Professional Profile</h3>
                    <p><strong>🎯 Goals:</strong> {st.session_state['goals']}</p>
                    <p><strong>🚀 Motivations:</strong> {st.session_state['motivations']}</p>
                    <p><strong>🛠 Skills:</strong> {st.session_state['skills']}</p>
                </div>
                <div class="professional-section">
                    <h3>⚠️ Challenges & Needs</h3>
                    <p><strong>😠 Frustrations:</strong> {st.session_state['frustrations']}</p>
                    <p><strong>💔 Pain Points:</strong> {st.session_state['pain_points']}</p>
                    <p><strong>✅ Needs:</strong> {st.session_state['needs']}</p>
                </div>
                <div class="professional-section">
                    <h3>🌐 Preferences</h3>
                    <p><strong>❤️ Interests:</strong> {', '.join(st.session_state['interests']) if st.session_state['interests'] else 'None'}</p>
                    <p><strong>📱 Platforms:</strong> {', '.join(st.session_state['platforms']) if st.session_state['platforms'] else 'None'}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif template == "creative":
            st.markdown(f"""
            <div class="persona-card-creative">
                <div class="creative-header">
                    <div class="user-photo-creative" style="text-align: center;">{image_html}</div>
                    <h1>✨ {st.session_state['name']} ✨</h1>
                    <p class="tagline">💼 {st.session_state['occupation']} | 🗓️ {st.session_state['age']} | 📍 {st.session_state['location']}</p>
                </div>
                <div class="creative-section">
                    <h2>🌍 My World</h2>
                    <p><strong>👤 Gender:</strong> {st.session_state['gender']}</p>
                    <p><strong>💻 Tech Level:</strong> {st.session_state['tech_savviness']}/5</p>
                    <p><strong>❤️ Passions:</strong> {', '.join(st.session_state['interests']) if st.session_state['interests'] else 'None'}</p>
                    <p><strong>📱 Platforms I Use:</strong> {', '.join(st.session_state['platforms']) if st.session_state['platforms'] else 'None'}</p>
                </div>
                <div class="creative-section">
                    <h2>🚀 What Drives Me</h2>
                    <p><strong>🎯 My Goals:</strong> {st.session_state['goals']}</p>
                    <p><strong>💡 My Motivations:</strong> {st.session_state['motivations']}</p>
                </div>
                <div class="creative-section">
                    <h2>🚧 My Challenges</h2>
                    <p><strong>😠 Frustrations:</strong> {st.session_state['frustrations']}</p>
                    <p><strong>💔 Pain Points:</strong> {st.session_state['pain_points']}</p>
                    <p><strong>✅ My Needs:</strong> {st.session_state['needs']}</p>
                    <p><strong>🛠 Skills:</strong> {st.session_state['skills']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # Add more templates as needed...

            # Export buttons
        export_persona("pdf")

        def export_json():
            persona_data = {
                k: v for k, v in st.session_state.items()
                if not k.startswith("_") and k != 'user_photo' and k != 'user_photo_bytes'
            }
            json_string = json.dumps(persona_data, indent=2).encode('utf-8')
            st.session_state['json_download_data'] = json_string
            st.session_state['json_download_filename'] = "persona.json"
            st.session_state['show_download'] = True

        if 'show_download' not in st.session_state:
            st.session_state['show_download'] = False
        if 'json_download_data' not in st.session_state:
            st.session_state['json_download_data'] = None
        if 'json_download_filename' not in st.session_state:
            st.session_state['json_download_filename'] = None

        col_rspace1, col_export_space, col_st_rspace2 = st.columns(
            [0.05, 0.90, 0.05])

        with col_export_space:
            st.button("Export as JSON", key="json_export_button",
                      on_click=export_json)

        if st.session_state['show_download'] and st.session_state['json_download_data'] is not None:
            col_dl1, col_dl2, col_dl3 = st.columns(
                [0.1, 0.8, 0.1])  # Adjust widths as needed
            with col_dl2:
                st.download_button(
                    label="Download Persona Data (JSON)",
                    data=st.session_state['json_download_data'],
                    file_name=st.session_state['json_download_filename'],
                    mime="application/json",
                    key="json_download_button",
                    on_click=lambda: setattr(
                        st.session_state, 'show_download', False),
                    type="primary",
                )
            # Use CSS to hide the button
            st.markdown(
                """
                <style>
                #json_download_button {
                    display: none;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            # Potentially trigger a JavaScript click after a short delay
            st.markdown(
                """
                <script>
                setTimeout(function() {
                    document.getElementById('json_download_button').click();
                }, 10);
                </script>
                """,
                unsafe_allow_html=True,
            )

st.markdown("</div>", unsafe_allow_html=True)
