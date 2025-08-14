import json
import requests
from io import BytesIO
from PIL import Image
import streamlit as st
import google.generativeai as genai
import base64

from app.services.avatar_service import generate_ai_avatar_by_HFModels, generate_randomuserphotoByGender


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
                    persona_data["name"], persona_data["occupation"], persona_data["gender"])
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


def generate_ai_avatar(name, occupation, gender):
    """Generate professional avatar using Stability AI with gender consistency"""
    try:
        stability_key = st.secrets.get("STABILITY_API_KEY")
        if not stability_key:
            st.error("Missing Stability API key in secrets.toml")
            return None

        # Enhanced prompt with strict gender control
        prompt = f"""
        Professional corporate headshot of {name}, {gender.lower()} {occupation.lower()}.
        Hyper-realistic studio portrait with:
        - Strictly {gender.lower()}-appearing subject
        - {gender}-appropriate business attire
        - Neutral gray background
        - High detail (512x512 resolution)
        - Professional hairstyle
        - Confident expression
        
        Technical requirements:
        - Photorealistic style
        - No artistic filters
        - No visible jewelry (unless culturally appropriate)
        - Crisp focus on facial features
        """

        # Gender-specific negative prompts
        negative_prompt = (
            "woman, female, makeup, dress, earrings" if gender == "Male"
            else "man, male, beard, mustache" if gender == "Female"
            else "gender-stereotypical"
        ) + ", cartoon, anime, blurry, deformed, text, watermark"

        response = requests.post(
            url="https://api.stability.ai/v2beta/stable-image/generate/core",
            headers={"Authorization": f"Bearer {stability_key}",
                     "Accept": "image/*"},
            files={"none": ''},
            data={
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "output_format": "png",
                "width": "512",
                "height": "512",
                "seed": 42,  # For more consistent results
            },
            timeout=10  # Add timeout
        )
        response.raise_for_status()

        # Process image
        img = Image.open(BytesIO(response.content))

        # Convert to square thumbnail
        img = img.resize((256, 256))  # Standardize size
        buffer = BytesIO()
        img.save(buffer, format="PNG", quality=95)

        return buffer.getvalue()

    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
    except Exception as e:
        st.error(f"Generation Failed: {str(e)}")

    st.session_state["user_photo"] = None
    return None
