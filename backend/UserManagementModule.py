import json
import re
import logger
from pathlib import Path
import DomainManagementEngine as DME

logger = logger.setup_logger("UserManagementModule")

# -------------------------------------------------
# Paths (FIXED – deterministic & Docker-safe)
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "UsersData"
USERS_CRED_PATH = DATA_PATH / "users.json"

# Ensure UsersData exists
DATA_PATH.mkdir(parents=True, exist_ok=True)

# Ensure users.json exists
if not USERS_CRED_PATH.exists():
    USERS_CRED_PATH.write_text("[]", encoding="utf-8")


class UserManager:
    """
    This class handles everything in relation to users.
    """

    def __init__(self):
        logger.info("Initializing UserManagement module.")
        self.users = self._load_json_to_dict()

    # -------------------------------------------------
    # Internal helpers
    # -------------------------------------------------

    def _load_json_to_dict(self):
        """
        Loads users.json and returns:
        dict[username] = password
        """
        logger.debug("Loading users.json file.")
        try:
            users = {}
            with USERS_CRED_PATH.open("r", encoding="utf-8") as f:
                users_json = json.load(f)

            for user in users_json:
                users[user["username"]] = user["password"]

            logger.debug("users.json loaded successfully.")
            return users

        except Exception as e:
            logger.error(f"users.json could not be loaded! {e}")
            return {}

    def load_users_json_to_memory(self):
        logger.info("Reloading users.json file.")
        self.users = self._load_json_to_dict()

    # -------------------------------------------------
    # Registration
    # -------------------------------------------------

    def register_page_add_user(self, username, password, password_confirmation, dme: DME.DomainManagementEngine):
        """
        Register a new user after validation.
        """
        logger.info("Processing new user's details.")
        try:
            # Username validation
            usr_valid = self.username_validity(username)
            if usr_valid == "FAILED" or not usr_valid[0]:
                return {"error": usr_valid[1]}

            # Password validation
            password_validity = self.register_page_password_validity(password, password_confirmation)
            if password_validity[0] == "FAILED" or not password_validity[0]:
                return {"error": password_validity[1]}

            # Persist user
            self.users[username] = password
            write_status = self.write_user_to_json(username, password)
            if write_status[0] == "FAILED":
                return {"error": write_status[1]}

            # Create domain file
            dme.load_user_domains(username)

            logger.info(f"{username} registered successfully.")
            return {"message": "Registered Successfully."}

        except Exception as e:
            logger.error(f"Unable to register user; Exception: {e}")
            return {"error": "Unable to register user."}

    # -------------------------------------------------
    # Validation
    # -------------------------------------------------

    def username_validity(self, username):
        """
        Validate username.
        """
        try:
            if not username or username.strip() == "":
                return False, "Username invalid."
            if username in self.users:
                return False, "Username already taken."
            return True, "Username is valid."
        except Exception as e:
            logger.error(f"Username validation failed: {e}")
            return "FAILED", "Error: Unable to validate username."

    def register_page_password_validity(self, password, password_confirmation):
        """
        Validate password rules.
        """
        try:
            if password != password_confirmation:
                return False, "Password and Password Confirmation are not the same."
            if len(password) < 8 or len(password) > 12:
                return False, "Password is not between 8 to 12 characters."
            if not re.search("[A-Z]", password):
                return False, "Password does not include at least one uppercase character."
            if not re.search("[a-z]", password):
                return False, "Password does not include at least one lowercase character."
            if not re.search("[0-9]", password):
                return False, "Password does not include at least one digit."
            if not password.isalnum():
                return False, "Password should include only uppercase characters, lowercase characters and digits!"
            return True, "SUCCESS"

        except Exception as e:
            logger.error(f"Password validation failed: {e}")
            return "FAILED", "Error: Unable to validate password."

    # -------------------------------------------------
    # Persistence
    # -------------------------------------------------

    def write_user_to_json(self, username, password):
        """
        Append user to users.json.
        """
        try:
            with USERS_CRED_PATH.open("r", encoding="utf-8") as f:
                users_list = json.load(f)

            users_list.append({
                "username": username,
                "password": password
            })

            with USERS_CRED_PATH.open("w", encoding="utf-8") as f:
                json.dump(users_list, f, indent=4, ensure_ascii=False)

            return "SUCCESS", "Username and password was written successfully."

        except Exception as e:
            logger.error(f"Failed to write user's details to users.json; {e}")
            return "FAILED", "Error: Unable to write user to file."

    def save_users_from_memory_to_json(self):
        """
        Rewrite users.json from memory.
        """
        try:
            users_list = [
                {"username": u, "password": self.users[u]}
                for u in self.users
            ]

            with USERS_CRED_PATH.open("w", encoding="utf-8") as f:
                json.dump(users_list, f, indent=4, ensure_ascii=False)

            return "SUCCESS", "Users written successfully."

        except Exception as e:
            logger.error(f"Failed to save users.json; {e}")
            return "FAILED", "Unable to write users.json."

    # -------------------------------------------------
    # Login
    # -------------------------------------------------

    def validate_login(self, username, password):
        try:
            if username in self.users and self.users[username] == password:
                logger.info(f"Login successful: {username}")
                return True
            logger.warning(f"Login failed: {username}")
            return False
        except Exception as e:
            logger.error(f"Login validation error: {e}")
            return False

    # -------------------------------------------------
    # Deletion
    # -------------------------------------------------

    def remove_user(self, username):
        logger.info(f"Removing user {username}")
        try:
            if username in self.users:
                del self.users[username]
                self.save_users_from_memory_to_json()

            domain_file = DATA_PATH / f"{username}_domains.json"
            domain_file.unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Error deleting user {username}: {e}")
