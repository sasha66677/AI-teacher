import google_drive as gd
import os
import subprocess


def run_python_file(file_name, folder_name):
    original_directory = os.getcwd()
    try:
        os.chdir(folder_name)
        result = subprocess.run(['python3', file_name], capture_output=True, text=True, check=True)
        output = result.stdout
        return output
    except subprocess.CalledProcessError as e:
        return f"Error: {e}\n\nError Output: {e.stderr}"
    finally:
        os.chdir(original_directory)


if __name__ == "__main__":
    creds = gd.authenticate()
    drive_service = gd.build("drive", "v3", credentials=creds)

    gd.list_files(drive_service)

    file_name = "python_script.py"
    destination_folder = "downloaded_folder"
    folder_name = "python_script"

    if(not gd.find_file(drive_service, file_name)):
        print(f"You haven't got a '{file_name}' file")
        exit()
    
    gd.download_folder_by_name(drive_service, folder_name, destination_folder)

    output = run_python_file(file_name, destination_folder)

    if output:
        print(output)

    gd.upload_folder(drive_service, destination_folder)