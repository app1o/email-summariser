import re
import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
# Make sure to import BeautifulSoup at the top of your file
from bs4 import BeautifulSoup
import base64 # you already have this
import google.generativeai as genai
from dotenv import load_dotenv
import json

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify']


# --- Load API Key (as before) ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def process_email_with_gemini(raw_email_body):
    """
    Takes the raw, messy email body, asks Gemini to clean it, summarize it,
    and extract structured information in a single step.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')

    # The new "all-in-one" prompt
    prompt = f"""
    Analyze the following raw email content. Your task is to act as an intelligent email assistant.
    First, mentally clean the content by ignoring quoted replies from previous emails, boilerplate text like unsubscribe links, and email signatures.
    Then, based only on the core message, provide a structured analysis in a valid JSON format.

    The summary should be a clear, easy-to-read paragraph.

    Raw Email Content:
    ---
    {raw_email_body}
    ---

    Provide your response as a single JSON object with the following schema:
    {{
      "summary": "A clear, paragraph-style summary of the email's core message, suitable for a quick read.",
      "action_items": ["A list of specific tasks or actions required from the recipient."],
      "key_dates": ["A list of any important dates, deadlines, or event times mentioned."],
      "sentiment": "Analyze the sentiment of the core message (e.g., 'Positive', 'Neutral', 'Negative', 'Urgent')."
    }}
    """

    try:
        response = model.generate_content(prompt)
        # Clean the response to ensure it's valid JSON
        json_response_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(json_response_text)
    except Exception as e:
        print(f"An error occurred processing with Gemini: {e}")
        # It's helpful to see the raw response when debugging
        if 'response' in locals():
            print(f"Raw Gemini response was: {response.text}")
        return None

# --- Your other imports ---

def clean_email_text(text):
    """
    Cleans common artifacts from email text content.
    """
    # Remove quoted replies
    text = re.sub(r'^>.*$', '', text, flags=re.MULTILINE)
    
    # A simple heuristic to remove signatures
    # This looks for a common signature delimiter and removes everything after it.
    text = text.split('-- \n')[0]
    
    # Remove excessive newlines, keeping paragraphs
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Normalize whitespace (spaces, tabs)
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()

def get_email_body(msg):
    """
    Parses a Gmail message to find the email body.
    It intelligently handles multipart, single-part, HTML, and plain text emails.
    """
    body_plain = None
    body_html = None

    # Handle multipart emails
    if 'parts' in msg['payload']:
        for part in msg['payload']['parts']:
            mime_type = part.get('mimeType')
            body = part.get('body', {})
            data = body.get('data')
            
            if not data:
                continue

            if mime_type == 'text/plain':
                body_plain = base64.urlsafe_b64decode(data).decode('utf-8')
            elif mime_type == 'text/html':
                body_html = base64.urlsafe_b64decode(data).decode('utf-8')

    # Handle single-part emails
    elif 'data' in msg['payload']['body']:
        data = msg['payload']['body'].get('data')
        if msg['payload'].get('mimeType') == 'text/plain':
            body_plain = base64.urlsafe_b64decode(data).decode('utf-8')
        elif msg['payload'].get('mimeType') == 'text/html':
            body_html = base64.urlsafe_b64decode(data).decode('utf-8')
    
    # Prioritize plain text, but fall back to HTML if necessary
    if body_plain:
        return body_plain
    elif body_html:
        # If we only have HTML, use BeautifulSoup to clean it
        soup = BeautifulSoup(body_html, 'html.parser')
        return soup.get_text() # This strips out all HTML tags
    
    return "" # Return empty string if no body is found






def readEmails():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(               
                # your creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
                'my_cred_file.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages',[])
        if not messages:
            print('No new messages.')
        else:
            message_count = 0
            for message in messages:
                # Get the full message object
                msg = service.users().messages().get(userId='me', id=message['id']).execute()      
                
                # Extract headers to get the 'From' field
                from_name = ""
                for header in msg['payload']['headers']:
                    if header['name'] == 'From':
                        from_name = header['value']
                        break # Found it, no need to keep looping
                
                # Use the new function to reliably get the email body
                raw_body = get_email_body(msg)

        if raw_body:
        # 2. Clean the text artifacts
            cleaned_body = clean_email_text(raw_body)
        
        # 3. Extract structured information using Gemini
            email_info = process_email_with_gemini(cleaned_body)
        
            if email_info:
                print("----------------------------------------")
                print(f"Summary: {email_info.get('summary', 'N/A')}")
                print(f"Sentiment: {email_info.get('sentiment', 'N/A')}")
                print(f"Action Items: {', '.join(email_info.get('action_items', [])) or 'None'}")
                print(f"Key Dates: {', '.join(email_info.get('key_dates', [])) or 'None'}")
                print("----------------------------------------\n")
                        
                        # Mark the message as read (optional)
                service.users().messages().modify(userId='me',id=message['id'],body={'removeLabelIds': ['UNREAD']}).execute()                                                     
    except Exception as error:
        print(f'An error occurred: {error}')
readEmails()