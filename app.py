import streamlit as st
import os
from PIL import Image
import tempfile
from llama_cloud_services import LlamaExtract
import requests
from requests.auth import HTTPBasicAuth
import boto3
from botocore.exceptions import ClientError

# LlamaExtract API key (ensure this is set correctly)
aws_access_key_id = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
aws_secret_access_key = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
LLAMA_CLOUD_API_KEY = st.secrets["aws"]["LLAMA_CLOUD_API_KEY"]  # Replace with your LlamaExtract API Key
authentication_pw = st.secrets["aws"]["authentication_pw"]
api_pw = st.secrets["aws"]["api_pw"]

# Initialize LlamaExtract client
extractor = LlamaExtract(api_key=LLAMA_CLOUD_API_KEY)

# Global agent
existing_agent = None

# Access the credentials stored in Streamlit's secrets

# aws_region = st.secrets["aws"]["AWS_REGION"]

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
        if username == "admin" and password == authentication_pw:
            # Set session state to logged in
            st.session_state.logged_in = True
            return True
        else:
            st.error("Incorrect username or password. Please try again.")
            return False
    return False

# Function to get job_id by sending a request to the process file endpoint with basic auth
def get_job_id_from_filename(filename):
    url = f"https://bol.dev.fleetpanda.org/process-file/{filename}"
    try:
        response = requests.get(url, auth=HTTPBasicAuth('admin', api_pw))
        response.raise_for_status()
        data = response.json()
        job_id = data.get("job_id")
        return job_id
    except requests.exceptions.RequestException as e:
        st.error(f"Error while requesting job ID: {e}")
        return None

# Function to get the result by passing the job_id to the result endpoint
def get_ocr_result(job_id):
    url = f"https://bol.dev.fleetpanda.org/result/{job_id}"
    try:
        response = requests.get(url, auth=HTTPBasicAuth('admin', api_pw))
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error while requesting result: {e}")

# --- S3 CONFIG ---
AWS_REGION = "us-east-1"
BUCKET_NAME = "fp-prod-s3"

def download_from_s3(file_key):
    """Download the selected image from S3 and return the local file path."""
    try:
        s3 = boto3.client("s3", region_name=AWS_REGION, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_path = temp_file.name
        temp_file.close()

        s3.download_file(BUCKET_NAME, file_key, temp_path)
        return temp_path

    except ClientError as e:
        st.error(f"S3 Download Error: {e}")
        return None
    except Exception as e:
        st.error(f"S3 Unexpected Error: {e}")
        return None


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

    # Radio button for file selection method
    file_option = st.radio("Select how to upload the BOL image:", ("Upload Image File", "Select from Dropdown"))

    # If the user selects the "Upload Image File" option
    if file_option == "Upload Image File":
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

    # If the user selects the "Select from Dropdown" option
    elif file_option == "Select from Dropdown":
        # Example list of filenames (can be dynamically loaded)
        filenames = [
            "061DF0F8-F4E8-44B1-81AA-1AC209FBBF4A.jpg",
            "061E6AAB-E3F8-4F4F-A31E-89C9459EF813.jpg",
            "061F7C9D-FA3C-4A20-B102-6576A7F766A0.jpg",
            "061F8FB4-2211-4F7F-815A-EC763F1C947A.jpg",
            "06206703-8FF6-41A3-BFF6-3C759FCAAF60.jpg",
            "06223A18-D43B-4C21-BB32-79445D665A06.jpg",
            "06224CFE-B6F0-4216-87CB-2ED086C16FE0.jpg",
            "062442C6-F4B3-47D4-BF51-334621BDFD63.jpg",
            "06288CA0-F88B-4B7E-A5C5-9E00B7D591DD.jpg",
            "0629C21D-E6F5-4706-8E51-DA042CF65165.jpg",
            "0629FD57-C27C-42D9-85BE-8CAA10A81E18.jpg",
            "062AF9E9-775D-4C93-B9D3-6C2747D0F623.jpg",
            "062C34FA-C56A-4F7C-82A7-FCE9DA12080E.jpg",
            "062C998F-FA81-40A0-9CC3-EDF167C5105D.jpg",
            "062DECF6-E58F-4FBD-B709-828BA045D284.jpg",
            "062E1120-B2E9-4686-A0E2-8F06F4F6D417.jpg",
            "062EDD2C-82C9-4938-9C2F-0CF89645BD32.jpg",
            "06303D1D-7847-46C1-BAF7-4199D059B98D.jpg",
            "06304974-849E-424C-86D2-2B893F140990.jpg",
            "06313975-3DB4-4005-BF44-BD9D23D7CE83.jpg",
            "06326A4F-0779-4062-9DBC-955683582F6F.jpg",
            "06326AA5-C9DD-44DF-A1D9-8FE439A698F0.jpg",
            "06327655-21C9-43E6-9927-0C7E73B6F9B8.jpg",
            "06328882-D59E-496F-8595-45EE9EC3E1B3.jpg",
            "06333BF4-9426-4121-87EB-A77DD8EDA6F8.jpg",
            "06335E8A-4A4E-4E33-9A75-6BF2FD7E54FD.jpg",
            "063376C3-697F-4B20-B3A9-13BC24B8B7E9.jpg",
            "06347C06-930D-4A34-B489-00068602455B.jpg",
            "06362912-BEF8-4951-AAF1-DB9B9BCD65C5.jpg",
            "0636BC9F-9C2D-473E-9A4B-AA2F35C078CF.jpg",
            "06378619-2C88-443A-A501-9ED2F80AE0CB.jpg",
            "06383A6E-599C-46BB-8712-06220E8D7D79.jpg",
            "06385067-8AA4-42E7-B896-F60B296CACEE.jpg",
            "0639B609-E787-4E71-91C0-28A7A27D22AA.jpg",
            "0639E48F-2784-455C-AB20-DDD8B48CC82D.jpg",
            "063A21F2-F4FC-4A54-951E-4A5294F7FFBF.jpg",
            "063A3ADA-94BF-448A-B2C4-AB52A9AA86E8.jpg",
            "063BCB23-E576-4699-B8BD-C75933B86912.jpg",
            "063C3E36-3098-4578-B8A4-79F3652E6168.jpg",
            "063C6F9E-83BB-4139-91F5-D0BCD3BDEBB8.jpg",
            "063D3765-6FCA-48DF-A334-CA4FA0021A6D.jpg",
            "063D5288-DCE0-484C-88E1-32EAA5B38165.jpg",
            "063E302E-2CEE-4077-90D7-68AB3B64BE96.jpg",
            "063E9108-172A-49B6-948F-73FEC57A1C01.jpg",
            "063FD1B8-C420-4898-AE44-CCEC1ADDDC0A.jpg",
            "0640B292-4CDD-4419-B4F9-C7CADA96E1C0.jpg"
        ]

        selected_filename = st.selectbox("Select a BOL Image", filenames)

        if selected_filename:
            # Step 1: Download file from S3
            with st.spinner("Downloading image from S3..."):
                downloaded_path = download_from_s3(selected_filename)

            if downloaded_path:
                # Step 2: Display downloaded image
                image = Image.open(downloaded_path)
                st.image(image, caption="Downloaded BOL Image", use_container_width=True)

                # Step 3: Get job_id by hitting the process file URL
                with st.spinner('Processing the BOL image...'):
                    job_id = get_job_id_from_filename(selected_filename)

                if job_id:
                    st.write(f"Job ID: {job_id}")

                    # Step 4: Get the result by passing job_id to the result URL
                    result = None
                    with st.spinner("Processing the OCR..."):
                        # Create a progress bar
                        progress_bar = st.progress(0)
                        # Simulate processing by updating the progress bar
                        for percent_complete in range(0, 101, 20):
                            progress_bar.progress(percent_complete)
                            time.sleep(1)  # Simulate time delay
                        # Get the OCR result after progress bar is filled
                        result = get_ocr_result(job_id)

                    if result:
                        # Step 5: Display the result
                        if result.get("status") == "completed":
                            extracted_data = result.get("result", {}).get("ExtractedData", {})
                            st.write("OCR Extraction Results:")
                            st.json(extracted_data)
                        else:
                            st.error("OCR result is not completed yet.")
            else:
                st.error("Failed to fetch job ID.")

    # # Logout button to allow users to log out and return to the login page
    # if st.button("Logout"):
    #     st.session_state.logged_in = False
    #     st.stop()  # Stop execution to prevent the rest of the app from running

# Run the Streamlit app
if __name__ == "__main__":
    main()
