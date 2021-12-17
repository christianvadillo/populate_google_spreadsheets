import gspread
import dataclasses

from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import CellNotFound, SpreadsheetNotFound
from typing import Dict, List, Optional
from pathlib import Path

from .exceptions import NotAllRowsAddedError


@dataclasses.dataclass
class Spreadsheet:
    filename: Optional[str] = dataclasses.field(init=False)
    sheet_name: Optional[str] = dataclasses.field(init=False)
    rows: List[List] = dataclasses.field(default_factory=list, init=False)
    headers: List[str] = dataclasses.field(default_factory=list, init=False)


class SpreadSheetManager:
    SCOPE = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
    ]

    def __init__(self, filename: str, sheet_name: str) -> None:
        self.filename = filename
        self.sheet_name = sheet_name
        self._file = self._connect_to_file(filename)
        self.worksheet = self._file.worksheet(sheet_name)

    def _connect_to_file(self, filename: str):
        # ! You need to provide your own credentials for your service account
        #
        credentials_path = Path("tmp/client_secret.json")
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path, self.SCOPE
        )
        self._client = gspread.authorize(credentials)

        try:
            file_connection = self._client.open(filename)
        except SpreadsheetNotFound:
            print(
                f"File {filename} not found. Verify if the file is shared to the service account"
            )
            raise SpreadsheetNotFound
        return file_connection

    def sheet_data(self) -> List[Dict]:
        """Returns the list of records of the active worksheet
        Returns:
            List[Dict]: Rows of the given sheet
        """
        return self.worksheet.get_all_records()

    def find_edit_cell(self, col_name: str, prev_value: str, new_value: str) -> bool:
        try:
            row = self.worksheet.find(prev_value).row
            col = self.worksheet.find(col_name).col
            self.edit_cell(row, col, new_value)
            return True
        except CellNotFound as e:
            print(e)
            return False

    def edit_cell(self, row, col, value):
        self.worksheet.update_cell(row, col, value)

    def remove_rows(self, start_idx, end_idx):
        self.worksheet.delete_rows(start_idx, end_idx)

    def clear_all_rows(self):
        self.worksheet.clear()

    def add_rows(self, rows: List[List]):
        pass

    def batch_writing(self, rows: List[List], headers: List[str] = None):
        import string

        LETTERS = list(string.ascii_uppercase)  # Up to 26 columns
        end_col = LETTERS[len(headers) - 1]

        range_ = "{start}{row}:{end}{row}"
        batch = [
            {
                "range": range_.format(start="A", end=end_col, row=idx),
                "values": [row],
            }
            for idx, row in enumerate(rows, 2)
        ]
        batch.insert(
            0,
            {
                "range": range_.format(start="A", end=end_col, row=1),
                "values": [headers],
            },
        )

        self.worksheet.batch_update(batch)

    def poppulate_sheet(self, file: Spreadsheet, clear_previous: bool = False):
        """It will add data from a given Spreadsheet object to the active worksheet

        Args:
            file (Spreadsheet): Object that contains the rows, headers and sheet name
            clear_previous (bool, optional): To remove previous data from the sheet.
            Defaults to False.
        """

        if clear_previous:
            self.clear_all_rows()

        self.batch_writing(file.rows, file.headers)
        sheet_data = self.sheet_data()
        if len(sheet_data) != len(file.rows):
            raise NotAllRowsAddedError("Some rows were not added")

    @property
    def worksheets(self):
        worksheets = self._file.worksheets()
        return [sheet.title for sheet in self._file.worksheets()]

    def __repr__(self) -> str:
        return f"Spreadsheet: {self.filename}\nSheetname: {self.sheet_name}"
