import os
import argparse
import urllib.request
from pathlib import Path
import time
from tqdm import tqdm

from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleDriveLoader:
    SCOPES = ['https://www.googleapis.com/auth/drive']

    def __init__(self, token: Path=Path("./token.json")):
        creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        try:
            self.service = build('drive', 'v3', credentials=creds)
        except HttpError as error:
            print(f'An error occurred: {error}')

    def upload(self, file_path: Path, dir_id: str=None, progress: bool=True):
        file_metadata = { 
                'name': file_path.name,
            }
        if dir_id is not None:
            file_metadata['parents'] = [dir_id]

        chunksize = 10 * 1000 * 1024 # 10MB
        media = MediaFileUpload(file_path, chunksize=chunksize, resumable=True)
        try:
            r = self.service.files().create(body=file_metadata, media_body=media, fields='id')

            if progress:
                response = None
                with tqdm(unit='B', 
                          unit_scale=True, 
                          unit_divisor=1024, 
                          ascii=True,
                          desc="Upload to Google Drive") as t:
                    last_progress = 0
                    while response is None:
                        status, response = r.next_chunk()
                        if status:
                            t.total = status.total_size
                            t.update((status.progress() - last_progress) * status.total_size)
                            last_progress = status.progress()
            else:
                r.execute()

        except HttpError as error:
            print(f'An error occurred: {error}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--token",
        default="./token.json",
        type=Path,
        help="Token path [default: ./token.json]")

    parser.add_argument(
        "-f", "--file_path",
        required=True,
        type=Path,
        help="Path to file for upload")

    parser.add_argument(
        "-d", "--dir_id",
        help="Google Driver dir ID")

    args = parser.parse_args()

    google_loader = GoogleDriveLoader(args.token)
    google_loader.upload(args.file_path, args.dir_id)

if __name__ == "__main__":
    main()
    
