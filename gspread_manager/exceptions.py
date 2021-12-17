class NotAllRowsAddedError(Exception):
    """Exception raised if not all rows are added to the sheet file

    Attributes:
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
