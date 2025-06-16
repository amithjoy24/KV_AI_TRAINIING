from googleapiclient.discovery import build
from .drive_utils import get_credentials

def extract_from_gsheet(spreadsheet_id, range_name="Sheet1"):
    service = build("sheets", "v4", credentials=get_credentials())
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get("values", [])

    return "\n".join([", ".join(row) for row in values])
