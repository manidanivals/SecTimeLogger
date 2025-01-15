# models/userDTO.py
class UserDTO:
    def __init__(self, user_id: int, username: str, email: str,  role: str,  company: str, password: str = None):
        """
        Initialize the UserDTO. Password is optional and should only be used when necessary.
        """
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password  # Only include this when necessary.
        self.role=role
        self.company=company

    def __repr__(self):
        """
        Provide a string representation of the UserDTO.
        Password is intentionally excluded for security reasons.
        """
        return f"UserDTO(user_id={self.user_id}, username='{self.username}', email='{self.email}',role='{self.role}', company='{self.company})"

    @staticmethod
    def from_user(user, include_password=False):
        """
        Factory method to create a UserDTO from a User instance.

        Args:
            user (User): The User instance to convert.
            include_password (bool): Whether to include the password in the DTO.

        Returns:
            UserDTO: A new UserDTO instance.
        """
        return UserDTO(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            password=user.password if include_password else None,
            role=user.role,
            company= user.company
        )

