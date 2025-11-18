# import streamlit as st
# import requests
# from PIL import Image
# from io import BytesIO
# import time
# import boto3

# # Authentication credentials for URL calls
# USERNAME = 'admin'
# PASSWORD = 'fp_bol_ocr'

# # AWS credentials for generating presigned URL
# AWS_ACCESS_KEY_ID = "AKIARSOL2IZEGPJX4FXL"
# AWS_SECRET_ACCESS_KEY = "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"
# AWS_DEFAULT_REGION = "us-east-1"

# # S3 Bucket name
# BUCKET_NAME = "fp-prod-s3"

# # List of available files (same as before)
# files = [
#     "008B03A3-715A-4490-86E1-9AB07D72DDB8.jpg",
#     "008BB226-E343-4730-BC09-25814BA9B34E.jpg",
#     "008C29A9-281D-4BA0-B0B0-0AA484E9E97C.jpg",
#     "008C2B36-E0D9-4DFD-B259-D9D72BFB9D97.jpg",
#     "008C6A14-58B7-4CC5-8DF8-B236AFD4A81A.jpg",
#     "008D5B95-25C3-4AC0-A801-37661F70A517.jpg",
#     "009066B3-CBEA-4FBC-B643-4B2B11B50B50.jpg",
#     "00910839-52F7-436E-8533-594D7E297461.jpg",
#     "009463BA-9E52-472D-958A-017EBA57E63F.jpg",
#     "0094CAC0-C4FF-46DD-8D39-0AF33B40292C.jpg",
#     "0095B753-361A-446C-87FE-6C5D9810200F.jpg",
#     "0095BA7D-2F7E-4B04-9A4C-923316563E70.jpg",
#     "0095C25D-64E8-4B19-B599-F3FF22A83477.jpg",
#     "0095CB1D-9F87-42CE-A777-5752BC23E63B.jpg",
#     "009793B2-30E1-4EAE-A0F3-4F66B798ABEB.jpg",
#     "0098A284-12CE-4787-8C5A-48B57C73B71E.jpg",
#     "0099DE27-7C12-4F33-9303-F41B9F45696E.jpg",
#     "009B452C-175D-4552-A003-AA5D33B78370.jpg",
#     "009BABBB-D0AA-415F-BDE6-A03A6CB0A200.jpg"
# ]

# # Function to generate a presigned URL for accessing a file from S3
# def get_s3_presigned_url(file_key: str, expiration: int = 3600):
#     s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
#                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#                              region_name=AWS_DEFAULT_REGION)
#     try:
#         # Generate a presigned URL to access the file from S3
#         url = s3_client.generate_presigned_url('get_object',
#                                                Params={'Bucket': BUCKET_NAME, 'Key': file_key},
#                                                ExpiresIn=expiration)  # URL expiration time in seconds
#         return url  # Return the presigned URL
#     except Exception as e:
#         return None  # Return None if there was an error generating the URL

# # Function to get the OCR results from the job ID
# def get_ocr_results(job_id):
#     # Construct the result URL
#     url = f"https://bol.dev.fleetpanda.org/result/{job_id}"
#     # Request OCR data with authentication
#     response = requests.get(url, auth=(USERNAME, PASSWORD))
    
#     # Debugging: log the response to check its structure
#     st.write(f"Response from OCR service: {response.text}")
    
#     if response.status_code == 200:
#         try:
#             result = response.json()
#             # Ensure 'ExtractedData' exists in the response
#             if 'result' in result and 'ExtractedData' in result['result']:
#                 return result['result']['ExtractedData']
#             else:
#                 st.error("OCR result does not contain 'ExtractedData'.")
#                 return None
#         except ValueError:
#             st.error("Failed to parse the response as JSON.")
#             return None
#     else:
#         st.error(f"Failed to get OCR data for job_id: {job_id}. Status code: {response.status_code}")
#         return None

# # Function to fetch the image using the presigned URL
# def fetch_image(selected_file):
#     # Get the presigned URL for the image
#     presigned_url = get_s3_presigned_url(selected_file)
#     if presigned_url:
#         # Fetch the image using the presigned URL
#         img_response = requests.get(presigned_url)
        
#         if img_response.status_code == 200:
#             try:
#                 # Open the image with PIL from the content
#                 img = Image.open(BytesIO(img_response.content))
#                 return img
#             except IOError:
#                 st.error("Failed to open image. The image might be corrupted or unsupported.")
#                 return None
#         else:
#             st.error(f"Failed to fetch image from S3. Status code: {img_response.status_code}")
#             return None
#     else:
#         st.error("Failed to generate presigned URL for the image.")
#         return None

# # Main Function to Build UI
# def main():
#     # Sidebar for Information
#     st.sidebar.header("About This App")
#     st.sidebar.write("""
#     This app allows you to extract important data from Bill of Lading (BOL) images. 
#     By uploading an image of a BOL, the app processes the image using OCR and extracts crucial details like:
    
#     - Truck Number
#     - Carrier Name
#     - Product Data
#     - Transaction times and dates

#     This feature reduces human effort and automates the extraction of key information, which can be used to autofill forms, update records, and much more!
    
#     **How it works**: Select an image file from the dropdown, and click "Extract Data from BOL Image" to view the extracted results.
#     """)

#     # Main Dashboard UI
#     st.title("OCR on Bill of Lading Image(BOL)")

#     # File Selection
#     selected_file = st.selectbox("Select a BOL image file:", files)

#     # Display selected file name
#     st.write(f"You selected: {selected_file}")

#     # Display the image
#     img = fetch_image(selected_file)
#     if img:
#         st.image(img, caption=selected_file, use_container_width=True)

#     # Button to trigger OCR extraction
#     if st.button('Extract Data from BOL Image'):
#         with st.spinner('Processing the BOL image...'):
#             # Step 1: Request to process image
#             process_url = f"https://bol.dev.fleetpanda.org/process-file/{selected_file}"
#             process_response = requests.get(process_url, auth=(USERNAME, PASSWORD))
            
#             if process_response.status_code == 200:
#                 job_id = process_response.json().get('job_id')
#                 st.write(f"Processing job created with job_id: {job_id}")
                
#                 # Step 2: Polling for OCR results
#                 progress = st.progress(0)
#                 for i in range(10):
#                     time.sleep(5)  # wait for the OCR process to complete
#                     result = get_ocr_results(job_id)
#                     if result:
#                         progress.progress((i + 1) * 10)
#                     else:
#                         progress.progress(100)
#                         break
                
#                 # Show the OCR results
#                 if result:
#                     st.write("OCR Results:")
#                     st.json(result)
#             else:
#                 st.error("Failed to process the image.")

# # Run the Streamlit app
# if __name__ == "__main__":
#     main()


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
