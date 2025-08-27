Gmail Email Processor with Gemini AI
An intelligent email processing tool that automatically reads unread Gmail messages, cleans the content, and uses Google's Gemini AI to extract structured information including summaries, action items, key dates, and sentiment analysis.

Features
Automated Email Reading: Connects to Gmail API to fetch unread emails
Smart Content Cleaning: Removes quoted replies, signatures, and email artifacts
AI-Powered Analysis: Uses Gemini AI to extract structured information
Comprehensive Processing: Generates summaries, action items, key dates, and sentiment analysis
Auto-Mark as Read: Automatically marks processed emails as read
HTML/Plain Text Support: Handles both HTML and plain text email formats
Prerequisites
Python 3.7+
Gmail API credentials
Google Gemini API key
Required Python packages (see Installation)
Installation
Clone the repository
bash
git clone <your-repo-url>
cd gmail-gemini-processor
Install required packages
bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
pip install google-api-python-client beautifulsoup4
pip install google-generativeai python-dotenv
Set up Gmail API credentials
Go to the Google Cloud Console
Create a new project or select an existing one
Enable the Gmail API
Create OAuth 2.0 credentials
Download the credentials file and rename it to my_cred_file.json
Place it in your project directory
Set up Gemini API
Get your Gemini API key from Google AI Studio
Create a .env file in your project directory
Add your API key:
GEMINI_API_KEY=your_gemini_api_key_here
Project Structure
gmail-gemini-processor/
│
├── main.py                 # Main application file
├── my_cred_file.json       # Gmail API credentials (you provide)
├── .env                    # Environment variables (you create)
├── token.json             # OAuth token (auto-generated)
├── requirements.txt       # Python dependencies
└── README.md              # This file
Usage
Run the application
bash
python main.py
First-time setup
The application will open a browser window for Gmail authentication
Grant the necessary permissions
The token will be saved for future use
Output format For each unread email, the tool will display:
----------------------------------------
Summary: [AI-generated summary of the email]
Sentiment: [Positive/Neutral/Negative/Urgent]
Action Items: [List of tasks or actions required]
Key Dates: [Important dates or deadlines]
----------------------------------------
Configuration
Gmail API Scopes
The application uses these Gmail API scopes:

https://www.googleapis.com/auth/gmail.readonly - Read emails
https://www.googleapis.com/auth/gmail.modify - Mark emails as read
Gemini Model
Currently uses gemini-1.5-flash for fast processing. You can modify this in the process_email_with_gemini() function.

Key Functions
readEmails()
Main function that handles Gmail authentication and processes unread emails.

get_email_body(msg)
Intelligently extracts email body content from both multipart and single-part messages, handling HTML and plain text formats.

clean_email_text(text)
Removes common email artifacts:

Quoted replies (lines starting with >)
Email signatures
Excessive whitespace and newlines
process_email_with_gemini(raw_email_body)
Sends cleaned email content to Gemini AI for analysis and returns structured JSON with:

Summary
Action items
Key dates
Sentiment analysis
Security Considerations
Keep your my_cred_file.json and .env files secure and never commit them to version control
Add these files to your .gitignore:
my_cred_file.json
.env
token.json
__pycache__/
*.pyc
Error Handling
The application includes error handling for:

Gmail API connection issues
Gemini AI processing errors
Email parsing problems
Authentication failures
Limitations
Processes only unread emails in the INBOX
Requires active internet connection
Subject to Gmail API and Gemini API rate limits
Basic signature detection (may need customization for different email formats)
Customization
Modify AI Analysis
Edit the prompt in process_email_with_gemini() to change what information is extracted or how it's formatted.

Change Email Query
Modify the query parameter in readEmails():

python
results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="your_custom_query").execute()
Add More Email Processing
Extend the clean_email_text() function to handle additional email artifacts specific to your use case.

Dependencies
txt
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.108.0
beautifulsoup4==4.12.2
google-generativeai==0.3.2
python-dotenv==1.0.0
Contributing
Fork the repository
Create a feature branch
Make your changes
Add tests if applicable
Submit a pull request
License
This project is licensed under the MIT License - see the LICENSE file for details.

Support
If you encounter issues:

Check that all dependencies are installed correctly
Verify your Gmail API credentials are valid
Ensure your Gemini API key is correct
Check the console output for specific error messages
For bugs or feature requests, please create an issue in the repository.

Acknowledgments
Google Gmail API for email access
Google Gemini AI for intelligent content processing
BeautifulSoup for HTML parsing
