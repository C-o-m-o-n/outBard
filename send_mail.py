import base64
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText

credentials = Credentials.from_service_account_file('gmail_secret.json',
    scopes=['https://www.googleapis.com/auth/gmail.send'])

service = build('gmail', 'v1', credentials=credentials)

message_body = "Hello, this is a test email from a Python script :)"
message = MIMEText(message_body)
message['to'] = "comon87@yahoo.com"
message['subject'] = "test send mail"
message['from'] = "out-bard-mailer@outbard.iam.gserviceaccount.com"

raw = base64.b64encode(message.as_bytes()).decode()
body = {'raw': raw}

# print(body)

service.users().messages().send(userId='out-bard-mailer@outbard.iam.gserviceaccount.com', body=body).execute()







# import googleapiclient.discovery
# from google.oauth2 import service_account

# SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']

# SERVICE_ACCOUNT_FILE = 'gmail_secret.json'

# credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# delegated_credentials = credentials.with_subject('comon928@gmail.com')

# sqladmin = googleapiclient.discovery.build('sqladmin', 'v1', credentials=credentials)
# response = sqladmin.instances().list(project='outbard').execute()