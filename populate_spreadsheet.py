import os

from spreadsheet_manager import SpreadSheetManager
from typing import List, Dict


def populate(filename: str, sheet: str, data: List):
    manager = SpreadSheetManager(filename, sheet)
    sheet_data = manager.sheet_data()
    print(sheet_data)
    manager.edit_cell(2, 2, "hola")


if __name__ == "__main__":

    filename = os.getenv("GOOGLE_FILE")
    sheet = os.getenv("SHEET_NAME")
    manager = SpreadSheetManager(filename, sheet)
    sheet_data = manager.sheet_data()
    sheets = manager.worksheets
    manager.find_edit_cell("fecha (yyyy-mm-dd)", "EDIT THIS", "EDITADO2")
