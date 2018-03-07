import httplib2
import os
import collections

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from sheets import *

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials(args):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 's3-acl-viewer.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, args)
        print('Storing credentials to ' + credential_path)
    return credentials


COLOR_GREEN_BG = { 'red': 0xCC/float(0xFF), 'green': 0xFF/float(0xFF), 'blue': 0xCC/float(0xFF) }
COLOR_RED_BG   = { 'red': 0xFF/float(0xFF), 'green': 0xCC/float(0xFF), 'blue': 0xCC/float(0xFF) }


def gen_header():
    return (
        Field("account", "Account", str, "Account", None),
        Field("bucket", "Bucket", str, "Bucket", None),
        FieldGroup("Public", (
            Field("public_read", "(Public) Read", str, "Read", None),
            Field("public_write", "(Public) Write", str, "Write", None),
            Field("public_read_acl", "(Public) Read ACL", str, "Read ACL", None),
            Field("public_write_acl", "(Public) Write ACL", str, "Write ACL", None),
            Field("public_full_control", "(Public) Full Control", str, "Full Control", None),
        )),
        FieldGroup("Authenticated AWS users", (
            Field("authenticated_aws_users_read", "(Authenticated AWS users) Read", str, "Read", None),
            Field("authenticated_aws_users_write", "(Authenticated AWS users) Write", str, "Write", None),
            Field("authenticated_aws_users_read_acl", "(Authenticated AWS users) Read ACL", str, "Read ACL", None),
            Field("authenticated_aws_users_write_acl", "(Authenticated AWS users) Write ACL", str, "Write ACL", None),
            Field("authenticated_aws_users_full_control", "(Authenticated AWS users) Full Control", str, "Full Control", None),
        )),
    )


def s3_report(buckets):
    
    fields = gen_header()
    conditional_format = (
        ConditionalFormat('CUSTOM_FORMULA', '=(INDIRECT(ADDRESS(ROW(), COLUMN())) = "N")', {
            'backgroundColor': COLOR_GREEN_BG,
        }),
        ConditionalFormat('CUSTOM_FORMULA', '=(INDIRECT(ADDRESS(ROW(), COLUMN())) = "Y")', {
            'backgroundColor': COLOR_RED_BG,
        }),
    )

    sheet = Sheet(
        source=(d.dump_gspread() for d in buckets),
        fields=fields,
        fields_conditional_formats=tuple(
            ColumnConditionalFormat(column, conditional_format)
            for column in field_flatten(FieldRoot(fields))
        ),
        sheet_id=1,
    )
    sheet_data = sheet.to_dict()
    return sheet_data


def build(name, buckets, args):
    credentials = get_credentials(args)
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    
    body = {
        "properties": {
            "title": name,
        },
        "sheets": [
            s3_report(buckets),
        ],
    }

    service.spreadsheets().create(body=body).execute()
