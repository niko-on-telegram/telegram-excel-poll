import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydantic import BaseModel

from categories import categories


class DataToPut(BaseModel):
    category_id: int
    name: str
    url: str
    reason: str


def put_data_to_excel(data: DataToPut):
    creds_json = "scheetaccesser-ac674548f73b.json"

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open("Braiders Competition")

    sheet = spreadsheet.get_worksheet(0)

    ids_sheet = spreadsheet.get_worksheet(1)
    last_row = ids_sheet.acell('A1').value

    if isinstance(last_row, str):
        last_row = int(last_row)

    if not last_row:
        last_row = 0
    last_row += 1

    sheet.update_cell(last_row, 1, categories[data.category_id])
    sheet.update_cell(last_row, 2, data.name)
    sheet.update_cell(last_row, 3, data.url)
    sheet.update_cell(last_row, 4, data.reason)

    ids_sheet.update_cell(1, 1, last_row)
