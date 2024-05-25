import google_drive as gd


if __name__ == "__main__":
    creds = gd.authenticate()
    drive_service = gd.build("drive", "v3", credentials=creds)
    gd.list_files(drive_service)

    gd.download_folder_by_name(drive_service, "Untitled folder", "downloaded_folder")
