from __future__ import print_function

import logging
import io
import tempfile

from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from clients.generate_auth import get_creds

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


class GoogleDriveClient:
    def __init__(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._tempdir_path = Path(self._tempdir.name)
        logging.info(f'Create temp dir {self._tempdir}')

        self._creds = get_creds(False)
        self._client = build('drive', 'v3', credentials=self._creds)


    def list_files(self, id_):
        items = []

        try:
            results = self._client.files().list(q = "'" + str(id_) + "' in parents", pageSize=10, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])
        except Exception as e:
            logging.error(e)

        return sorted(items, key=lambda x: x['name'])


    def download(self, name, id):
        try:
            # pylint: disable=maybe-no-member
            request = self._client.files().get_media(fileId=id)
            file_path = self._tempdir_path / name
            fh = io.FileIO(file_path, mode='wb')
            downloader = MediaIoBaseDownload(fh, request, chunksize=1024 * 1024)
            done = False
            while not done:
                status, done = downloader.next_chunk(num_retries=5)
                if status:
                    logging.info(f'Download {int(status.progress() * 100)} / 100.')

        except HttpError as error:
            logging.error(F'An error occurred: {error}')
            return None

        return file_path


    def close(self):
        self._tempdir.cleanup()
