from Models.Data import SessionLocal
from Models.Timesheet import Timesheet
from Models.TimesheetDTO import TimesheetDTO
from fastapi import HTTPException
from sqlalchemy import func

class TimesheetController:
    def create_timesheet(self, user_id: int, date, hours: float, description: str = None):
        """
        Log hours for a particular user.
        """
        with SessionLocal() as db:
            new_log = Timesheet(
                user_id=user_id,
                date=date,
                hours=hours,
                description=description
            )
            db.add(new_log)
            db.commit()
            db.refresh(new_log)
            return TimesheetDTO.from_model(new_log)

    def get_timesheets_for_user(self, user_id: int):
        """
        Retrieve all timesheet records for one user.
        """
        with SessionLocal() as db:
            logs = db.query(Timesheet).filter(Timesheet.user_id == user_id).all()
            return [TimesheetDTO.from_model(log) for log in logs]

    def get_timesheets_for_company(self, company: str):
        """
        Get all timesheet records for users belonging to a given company.
        """
        with SessionLocal() as db:
            # We'll join Timesheet with User based on user_id
            from Models.User import User  # import here to avoid circular import

            logs = (db.query(Timesheet)
                        .join(User, User.user_id == Timesheet.user_id)
                        .filter(User.company == company)
                        .all())
            return [TimesheetDTO.from_model(log) for log in logs]

    def get_total_hours_for_company(self, company: str):
        """
        Sum all hours for a given company.
        """
        with SessionLocal() as db:
            from Models.User import User
            total_hours = (db.query(func.sum(Timesheet.hours))
                           .join(User, User.user_id == Timesheet.user_id)
                           .filter(User.company == company)
                           .scalar())
            return total_hours or 0.0

    def get_total_hours_for_all(self):
        """
        Only for admin: sum of hours across all companies.
        """
        with SessionLocal() as db:
            total_hours = db.query(func.sum(Timesheet.hours)).scalar()
            return total_hours or 0.0
