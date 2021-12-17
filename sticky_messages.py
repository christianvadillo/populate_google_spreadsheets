import dataclasses

from datetime import datetime
from typing import Optional

from db.crud_dynamodb import get_trial_groups


MESSAGES = ["WEEK 1 MESSAGE", "WEEK 2 MESSAGE", "WEEK 3 MESSAGE", "WEEK 4 MESSAGE"]


@dataclasses.dataclass
class Grupo:
    tag: str
    weeks_in_service: Optional[int]
    started_date: str
    name: str
    platform: str

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


def populate_spreadsheet():
    groups = [Grupo(**item) for item in get_trial_groups()]
    # We are interested in the groups that have been in service for less than 5 weeks
    for group in groups:
        if group.weeks_in_service < 4:
            print(group.name)
            print(group.weeks_in_service)
            print(MESSAGES[group.weeks_in_service])
            print("-----------------------------------------------------")

    import pdb

    pdb.set_trace()


if __name__ == "__main__":
    populate_spreadsheet(filename = "DATA_Actividades_AWS"
    sheet = "Cumpleanios")
