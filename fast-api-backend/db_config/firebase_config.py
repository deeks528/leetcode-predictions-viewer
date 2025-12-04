import firebase_admin
from firebase_admin import credentials, db
import os
import logging
from typing import Set, List, Dict, Any

logger = logging.getLogger(__name__)

def initialize_firebase() -> bool:
    """Initialize Firebase with error handling."""
    try:
        # Check if already initialized
        try:
            firebase_admin.get_app()
            logger.info("Firebase already initialized")
            return True
        except ValueError:
            pass  # Not initialized, proceed
        
        # Get credentials path
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 
                              './db_config/discordbot1-fe753-firebase-adminsdk-fbsvc-4cddd84b29.json')
        
        # Check if file exists
        if not os.path.exists(cred_path):
            print("❌ Credentials file missing!")
            print("\n📂 Current directory:", os.getcwd())
            print("\n📄 Files in current folder:")
            print(os.listdir())
            raise FileNotFoundError(f"Firebase credentials file not found: {cred_path}")
        
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://discordbot1-fe753-default-rtdb.firebaseio.com/'
        })
        logger.info("✅ Firebase initialized successfully")
        return True
    except FileNotFoundError as e:
        logger.error(f"❌ Firebase initialization failed: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Firebase initialization failed: {e}")
        raise RuntimeError(f"Failed to initialize Firebase: {str(e)}") from e

# Initialize on module import
initialize_firebase()


def get_users(channel_id: str) -> Set[str]:
    """
    Fetches users associated with a specific channel ID from Firebase.
    Returns a set of usernames.
    """
    ref = db.reference(f'users/{channel_id}')
    users_data = ref.get()
    
    if not users_data:
        return set()
        
    # Handle list (standard case) or dict (if keys are used)
    if isinstance(users_data, list):
        return {str(u) for u in users_data if u}
    elif isinstance(users_data, dict):
        return {str(u) for u in users_data.values() if u}
        
    return set()

def add_new_users(channel_id: str, usernames: List[str] | str) -> str:
    """
    Adds a usernames to the set of users for a given channel ID in Firebase.
    """
    ref = db.reference(f'users/{channel_id}')
    current_users = get_users(channel_id)
    if len(current_users)!=0:
        return "Channel Id already exists"
    if isinstance(usernames, str):
        usernames = [usernames]
    current_users.update(usernames)
    ref.set(list(current_users))
    return "Successfully added usernames"

def add_user(channel_id: str, usernames: List[str] | str) -> str:
    """
    Adds a usernames to the set of users for a given channel ID in Firebase.
    """
    ref = db.reference(f'users/{channel_id}')
    current_users = get_users(channel_id)
    if len(current_users)==0:
        return "Channel Id not found"
    if isinstance(usernames, str):
        usernames = [usernames]
    current_users.update(usernames)
    ref.set(list(current_users))
    return "Successfully added new usernames"

# --- Codeforces specific functions (unchanged, but included for context) ---

def get_cf_users(channel_id: str) -> Dict[str, Any]:
    """Fetches Codeforces user data for a channel from Firebase."""
    ref = db.reference(f'cf_users/{channel_id}')
    users_data = ref.get()
    return users_data if users_data else {}

def add_cf_user(channel_id: str, username: str, user_data: Dict[str, Any]) -> None:
    """Adds a new Codeforces user with initial data to Firebase for a channel."""
    ref = db.reference(f'cf_users/{channel_id}')
    current_users_data = get_cf_users(channel_id)
    current_users_data[username] = user_data
    ref.set(current_users_data)

def update_cf_user_data(channel_id: str, username: str, user_data: Dict[str, Any]) -> None:
    """Updates data for an existing Codeforces user in Firebase for a channel."""
    ref = db.reference(f'cf_users/{channel_id}')
    current_users_data = get_cf_users(channel_id)
    if username in current_users_data:
        current_users_data[username] = user_data
        ref.set(current_users_data)
    else:
        logger.warning(f"Warning: Attempted to update non-existent CF user: {username}")
