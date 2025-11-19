import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import uuid
import os
import tempfile
from llama_cloud_services import LlamaExtract

# LlamaExtract API key (ensure this is set correctly)
LLAMA_CLOUD_API_KEY = "llx-iKKU5UkOR9lD7I5I5LczP4gyT7RnBC9vWWyCWKNeLA0iod9g"  # Replace with your LlamaExtract API Key

# Initialize LlamaExtract client
extractor = LlamaExtract(api_key=LLAMA_CLOUD_API_KEY)

# Global agent
existing_agent = None

# Function to get or create the existing LlamaExtract agent
def get_existing_agent():
    global existing_agent
    if not existing_agent:
        existing_agent = extractor.get_agent("OCR_BOL_FLEETPANDA")  # Replace with your agent name
    return existing_agent

# Function to perform OCR using LlamaExtract
def perform_ocr_on_image(image):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
        temp_file_path = temp_file.name
        # Save the image to the temporary file
        image.save(temp_file, format='JPEG')
        
        # Perform OCR extraction
        agent = get_existing_agent()
        result = agent.extract(temp_file_path)

        # Delete the temporary file after OCR
        try:
            os.remove(temp_file_path)
        except Exception as e:
            # st.error(f"Error deleting temporary file: {str(e)}")
            print(f"Error deleting temporary file: {str(e)}")
        
        return result.data

# Basic Authentication
def authenticate():
    """Prompts for username and password to authenticate."""
    st.title("Login")

    # Username and password for basic authentication
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Check if login button is clicked
    if st.button("Login"):
        if username == "admin" and password == "f14c9fff37033c2fd309682ed603f8178a3e30e3a5fb16ea1bc871e6202db":
            # Set session state to logged in
            st.session_state.logged_in = True
            return True
        else:
            st.error("Incorrect username or password. Please try again.")
            return False
    return False

# Main Streamlit UI
def main():
    # Check if the user is logged in, if not, show the login form
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        # Display the login form
        if authenticate():
            st.session_state.logged_in = True
            st.stop()  # Stop execution to prevent the rest of the app from running
        return  # If not logged in, return early

    # Sidebar for information
    st.sidebar.header("About This App")
    st.sidebar.write("""
    This app extracts important data from Bill of Lading (BOL) images using Optical Character Recognition (OCR).
    
    Upload a BOL image to extract data such as:
    - Truck Number
    - Carrier Name
    - Product Data
    - Transaction times and dates

    The extracted data can be used to autofill forms, automate records, and much more.
    """)

    # Main title
    st.title("Structured Data Extraction using OCR on Bill of Lading Image (BOL)")

    # File Upload Section
    uploaded_file = st.file_uploader("Upload a BOL Image", type=["jpg", "jpeg", "png"])

    # Check if file is uploaded
    if uploaded_file is not None:
        # Display the uploaded image
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded BOL Image", use_container_width=True)

        # Perform OCR when the user clicks the button
        if st.button("Extract Data from BOL Image"):
            with st.spinner('Processing the BOL image...'):
                try:
                    # Perform OCR on the uploaded image
                    extracted_data = perform_ocr_on_image(img)

                    # Display the OCR result
                    st.write("OCR Results:")
                    st.json(extracted_data)

                except Exception as e:
                    st.error(f"Error performing OCR: {str(e)}")

    # Logout button to allow users to log out and return to the login page
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.stop()  # Stop execution to prevent the rest of the app from running

# Run the Streamlit app
if __name__ == "__main__":
    main()
