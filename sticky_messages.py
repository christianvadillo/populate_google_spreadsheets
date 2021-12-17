import dataclasses

from datetime import datetime
from typing import Optional, List, Dict

from db.crud_dynamodb import get_trial_groups
from gspread_manager.spreadsheet_manager import SpreadSheetManager, Spreadsheet


MESSAGES = ["WEEK 1 MESSAGE", "WEEK 2 MESSAGE", "WEEK 3 MESSAGE", "WEEK 4 MESSAGE"]


@dataclasses.dataclass
class Grupo:
    tag: str
    started_date: str
    name: str
    platform: str
    weeks_in_service: Optional[int]
    message: Optional[str]

    def __init__(self, **kwargs):
        self.tag = kwargs.get("Etiqueta")
        self.started_date = kwargs.get("FechaInicio")
        self.name = kwargs.get("Grupo")
        self.platform = kwargs.get("Plataforma")
        self.weeks_in_service = self._calculate_weeks_in_service()

    def _calculate_weeks_in_service(self) -> int:
        """Get the total weeks that the group has been in service since the start date."""
        days = (datetime.now() - datetime.strptime(self.started_date, "%Y-%m-%d")).days
        return days // 7


def get_groups_to_use() -> List[Grupo]:
    groups = [Grupo(**item) for item in get_trial_groups()]
    to_use = []

    for group in groups:
        if group.weeks_in_service < 4:
            group.message = MESSAGES[group.weeks_in_service]
            to_use.append(group)
    return to_use


if __name__ == "__main__":
    """We are interested in send sticky messages to trial groups in their first 4 weeks.
    - Depending on the week, the message will be different.
    - We are required to store the message in a Google Spreadsheet for later use.
    """

    import os

    filename = os.getenv("GOOGLE_FILE")
    sheet_name = os.getenv("SHEET_NAME")
    to_use = get_groups_to_use()

    sheet_file = Spreadsheet()
    sheet_file.headers = ["grupo", "mensaje", "imagen"]
    sheet_file.rows = [[group.name, group.message, ""] for group in to_use]
    manager = SpreadSheetManager(filename, sheet_name)
    manager.poppulate_sheet(sheet_file, clear_previous=True)
