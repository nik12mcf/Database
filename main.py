from __future__ import print_function
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from datetime import timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import os
import argparse
from apiclient import errors

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive']

dataFeeds = {}

# Initialization to use google drive api
def get_gdrive_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # return Google Drive API service
    return build('drive', 'v3', credentials=creds)

# print available data feeds in the google drive
def print_available_datafeeds(service, folder_id):
    print("List of Available Data Feeds")

    page_token = None
    while True:
        response = service.files().list(q="'10AwOm21ygT9es7dC2SUyxoVx75INjnDD' in parents",
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()
        for folder in response.get('files', []):
            #print('Found Data Folder: %s (%s)' % (folder.get('name'), folder.get('id')))

            query_tag = "'" + folder.get('id') + "'" + " in parents"

            response_temp = service.files().list(q=query_tag,
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()

            for file in response_temp.get('files', []):
                if file.get('name') == "ReadMe":
                    print('Found Data Folder: %s (%s)' % (folder.get('name'), folder.get('id')))
                    dataFeeds[folder.get('name')] = folder.get('id')

                    content = service.files().export(fileId=file.get('id'), mimeType='text/plain').execute()

                    print(content.decode("utf-8-sig"))

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

# Retrieve files from google drive from specific data_feeds
# taking into account other inpput parameters for particular feed
def retrieve_files_from_folder(service, parametersDict):
    # Standard naming convention for files data_feeds_startDate_endDate_source_version
    # Additional parameters may be applied
    print("\nRetrieving Data Files")

    page_token = None
    query_tag = "'" + dataFeeds[parametersDict['-d']] + "'" + " in parents"

    # IEX data retrieval
    if parametersDict['-d'] == "IEX_TEST":
        print(dataFeeds[parametersDict['-d']])
        response_temp = service.files().list(q=query_tag,
                                             spaces='drive',
                                             fields='nextPageToken, files(id, name)',
                                             pageToken=page_token).execute()

        for file in response_temp.get('files', []):
            print(file)

# Define menu for interaction, receives terminal input to retrieve data
def menu(service):
    print("Please input parameters")

    # Data Feed -d
    # Start Date -s
    # End Date -e
    # Version -v
    # Origin -o
    # Ticker -t
    validParameters = ['-d', '-s', '-e']

    parametersDict = {'-d': None, '-s': None, '-e': None}

    raw_input = input().split()
    parameters = {}

    # Check correct number of arguments from terminal
    if len(raw_input) % 2 != 0:
        print("Incorrect Number of Arguments")
        menu(service)

    # Check if all parameters are valid
    for i in range(0, len(raw_input), 2):
        if raw_input[i] not in validParameters:
            print("Invalid Parameter")
            menu(service)
        else:
            parametersDict[raw_input[i]] = raw_input[i+1]

    #print(parametersDict)

    #if parametersDict['-d'] not in dataFeeds:
    #    print("Data Feed Error")

    retrieve_files_from_folder(service, parametersDict)

    menu(service)



if __name__ == "__main__":
    service = get_gdrive_service()
    dataFolderID = '10AwOm21ygT9es7dC2SUyxoVx75INjnDD'

    print_available_datafeeds(service, dataFolderID)

    menu(service)

    #retrieve_files_from_folder(service)

    exit(1)