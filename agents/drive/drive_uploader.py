from pydrive.auth import GoogleAuth
from googleapiclient.http import MediaFileUpload
from pydrive.drive import GoogleDrive



class DriveUploader:

    def __init__(self):  
        GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = 'data/client_secrets.json'

    def auth(self):
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile("data/mycreds.txt")
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.CommandLineAuth() #para remotos
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved creds
            gauth.Authorize()
        # Save the current credentials to a file
        gauth.SaveCredentialsFile("data/mycreds.txt")

        self.drive = GoogleDrive(gauth)

    def set_folder(self, folder_id):
        self.folder_id = folder_id


    def upload_file(self, path = 'data/blep.txt'):
        if not self.folder_id:
            print("Please, first set a folder with driveUploader.setFolder(_)")
            return
        
        options = {"parents": [{"kind": "drive#fileLink", "id": self.folder_id}]}
        file = self.drive.CreateFile(options)
        file.SetContentFile(path)
        file.Upload()
