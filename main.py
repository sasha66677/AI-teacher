import googleapiclient.http
import httplib2
import oauth2client.client
import six
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


OAUTH2_SCOPE = "https://www.googleapis.com/auth/drive"

CLIENT_SECRETS = "client_secrets.json"

FILENAME = "document.txt"

# Metadata about the file.
MIMETYPE = "text/plain"
TITLE = "My New Text Document"
DESCRIPTION = "A shiny new text document about hello world."



flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
authorize_url = flow.step1_get_authorize_url()
print("Go to the following link in your browser: " + authorize_url)


code = six.moves.input("Enter verification code: ").strip()
credentials = flow.step2_exchange(code)


http = httplib2.Http()
credentials.authorize(http)
drive_service = build("drive", "v2", http=http)



media_body = googleapiclient.http.MediaFileUpload(
    FILENAME, mimetype=MIMETYPE, resumable=True
)


body = {
    "title": TITLE,
    "description": DESCRIPTION,
}


try:
  new_file = (
      drive_service.files().insert(body=body, media_body=media_body).execute()
  )
  file_title = new_file.get("title")
  file_desc = new_file.get("description")
  if file_title == TITLE and file_desc == DESCRIPTION:
    print(
        f"File is uploaded \nTitle : {file_title}  \nDescription : {file_desc}"
    )

except HttpError as error:
  # TODO(developer) - Handle errors from drive API.
  print(f"An error occurred: {error}")