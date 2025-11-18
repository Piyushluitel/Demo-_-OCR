import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import time
import boto3

# Authentication credentials for URL calls
USERNAME = 'admin'
PASSWORD = 'fp_bol_ocr'

# AWS credentials for generating presigned URL
AWS_ACCESS_KEY_ID = "AKIARSOL2IZEGPJX4FXL"
AWS_SECRET_ACCESS_KEY = "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"
AWS_DEFAULT_REGION = "us-east-1"

# S3 Bucket name
BUCKET_NAME = "fp-prod-s3"

# List of available files (same as before)
files = [
    "008B03A3-715A-4490-86E1-9AB07D72DDB8.jpg",
    "008BB226-E343-4730-BC09-25814BA9B34E.jpg",
    "008C29A9-281D-4BA0-B0B0-0AA484E9E97C.jpg",
    "008C2B36-E0D9-4DFD-B259-D9D72BFB9D97.jpg",
    "008C6A14-58B7-4CC5-8DF8-B236AFD4A81A.jpg",
    "008D5B95-25C3-4AC0-A801-37661F70A517.jpg",
    "009066B3-CBEA-4FBC-B643-4B2B11B50B50.jpg",
    "00910839-52F7-436E-8533-594D7E297461.jpg",
    "009463BA-9E52-472D-958A-017EBA57E63F.jpg",
    "0094CAC0-C4FF-46DD-8D39-0AF33B40292C.jpg",
    "0095B753-361A-446C-87FE-6C5D9810200F.jpg",
    "0095BA7D-2F7E-4B04-9A4C-923316563E70.jpg",
    "0095C25D-64E8-4B19-B599-F3FF22A83477.jpg",
    "0095CB1D-9F87-42CE-A777-5752BC23E63B.jpg",
    "009793B2-30E1-4EAE-A0F3-4F66B798ABEB.jpg",
    "0098A284-12CE-4787-8C5A-48B57C73B71E.jpg",
    "0099DE27-7C12-4F33-9303-F41B9F45696E.jpg",
    "009B452C-175D-4552-A003-AA5D33B78370.jpg",
    "009BABBB-D0AA-415F-BDE6-A03A6CB0A200.jpg"
]

# Function to generate a presigned URL for accessing a file from S3
def get_s3_presigned_url(file_key: str, expiration: int = 3600):
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             region_name=AWS_DEFAULT_REGION)
    try:
        # Generate a presigned URL to access the file from S3
        url = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': BUCKET_NAME, 'Key': file_key},
                                               ExpiresIn=expiration)  # URL expiration time in seconds
        return url  # Return the presigned URL
    except Exception as e:
        return None  # Return None if there was an error generating the URL

# Function to get the OCR results from the job ID
def get_ocr_results(job_id):
    # Construct the result URL
    url = f"https://bol.dev.fleetpanda.org/result/{job_id}"
    # Request OCR data with authentication
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    
    if response.status_code == 200:
        result = response.json()
        return result['result']['ExtractedData']
    else:
        st.error(f"Failed to get OCR data for job_id: {job_id}")
        return None

# Function to fetch the image using the presigned URL
def fetch_image(selected_file):
    # Get the presigned URL for the image
    presigned_url = get_s3_presigned_url(selected_file)
    if presigned_url:
        # Fetch the image using the presigned URL
        img_response = requests.get(presigned_url)
        
        if img_response.status_code == 200:
            try:
                # Open the image with PIL from the content
                img = Image.open(BytesIO(img_response.content))
                return img
            except IOError:
                st.error("Failed to open image. The image might be corrupted or unsupported.")
                return None
        else:
            st.error(f"Failed to fetch image from S3. Status code: {img_response.status_code}")
            return None
    else:
        st.error("Failed to generate presigned URL for the image.")
        return None

# Main Function to Build UI
def main():
    st.title("BOL OCR Dashboard")
    
    # File Selection
    selected_file = st.selectbox("Select a BOL image file:", files)

    # Display selected file name
    st.write(f"You selected: {selected_file}")

    # Display the image
    img = fetch_image(selected_file)
    if img:
        st.image(img, caption=selected_file, use_column_width=True)

    # Button to trigger OCR extraction
    if st.button('Extract Data from BOL Image'):
        with st.spinner('Processing the BOL image...'):
            # Step 1: Request to process image
            process_url = f"https://bol.dev.fleetpanda.org/process-file/{selected_file}"
            process_response = requests.get(process_url, auth=(USERNAME, PASSWORD))
            
            if process_response.status_code == 200:
                job_id = process_response.json().get('job_id')
                st.write(f"Processing job created with job_id: {job_id}")
                
                # Step 2: Polling for OCR results
                progress = st.progress(0)
                for i in range(10):
                    time.sleep(5)  # wait for the OCR process to complete
                    result = get_ocr_results(job_id)
                    if result:
                        progress.progress((i + 1) * 10)
                    else:
                        progress.progress(100)
                        break
                
                # Show the OCR results
                if result:
                    st.write("OCR Results:")
                    st.json(result)
            else:
                st.error("Failed to process the image.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
