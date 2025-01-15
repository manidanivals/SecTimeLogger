class TimesheetDTO:
    def __init__(self, id: int, user_id: int, date, hours: float, description: str):
        self.id = id
        self.user_id = user_id
        self.date = date
        self.hours = hours
        self.description = description

    @staticmethod
    def from_model(timesheet):
        return TimesheetDTO(
            id=timesheet.id,
            user_id=timesheet.user_id,
            date=timesheet.date,
            hours=timesheet.hours,
            description=timesheet.description
        )