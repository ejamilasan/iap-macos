import subprocess
import sqlite3
import os
import sys
import logging
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup argument parser
parser = argparse.ArgumentParser(description="GCE VM password management script.")
parser.add_argument('--vm', required=True, help="GCE VM name")
parser.add_argument('--zone', required=True, help="GCE zone")
parser.add_argument('--project', required=True, help="GCE project ID")

# Parse the arguments
args = parser.parse_args()

# SQLite database file
DB_FILE = 'passwords.db'

# Function to create the database if it doesn't exist
def create_db():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS passwords (vm_name TEXT PRIMARY KEY, password TEXT)''')
            conn.commit()
            logger.info("Database created (or exists already).")
    except sqlite3.DatabaseError as e:
        logger.error(f"Failed to create database: {e}")
        sys.exit(1)

# Function to retrieve the password from the database
def get_password_from_db(vm_name):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('SELECT password FROM passwords WHERE vm_name = ?', (vm_name,))
            result = c.fetchone()
        return result[0] if result else None
    except sqlite3.DatabaseError as e:
        logger.error(f"Failed to retrieve password from DB: {e}")
        sys.exit(1)

# Function to save the password to the database
def save_password_to_db(vm_name, password):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('REPLACE INTO passwords (vm_name, password) VALUES (?, ?)', (vm_name, password))
            conn.commit()
        logger.info(f"Password for VM '{vm_name}' saved to database.")
    except sqlite3.DatabaseError as e:
        logger.error(f"Failed to save password to DB: {e}")
        sys.exit(1)

# Cleanup function to remove temporary files
def cleanup(*files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)
            logger.info(f"Removed file: {file}")

# Function to get the current username from gcloud
def get_username():
    try:
        result = subprocess.run(
            ['gcloud', 'config', 'list', 'account', '--format', 'value(core.account)'],
            check=True, capture_output=True, text=True
        )
        username = result.stdout.split('@')[0].strip()
        if not username:
            raise ValueError("Username is empty.")
        return username
    except (subprocess.CalledProcessError, ValueError) as e:
        logger.error(f"Error getting username: {e}")
        sys.exit(1)

# Function to reset the Windows password for the VM
def reset_windows_password(vm, zone, project, username):
    try:
        result = subprocess.run(
            ['gcloud', 'compute', 'reset-windows-password', vm, '--user', username, '--zone', zone, '--project', project],
            input="Y\n", check=True, capture_output=True, text=True
        )
        password_line = next(line for line in result.stdout.splitlines() if "password" in line.lower())
        password = password_line.split(":")[-1].strip()
        logger.info("Windows password reset successfully.")
        return password
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reset Windows password: {e}")
        sys.exit(1)

# Function to create the GCP compute client
def create_compute_client():
    try:
        credentials, project = google.auth.default()
        service = build('compute', 'v1', credentials=credentials)
        return service, project
    except Exception as e:
        logger.error(f"Failed to initialize GCP client: {e}")
        sys.exit(1)

# Main logic
def main():
    # Initialize the database
    create_db()

    # Get the current username
    username = get_username()

    # Check if password exists in the DB
    existing_password = get_password_from_db(args.vm)
    if existing_password:
        logger.info(f"Password for VM '{args.vm}' found in database.")
    else:
        # If no password exists, reset and save the new one
        logger.info(f"Password for VM '{args.vm}' not found in database, resetting...")
        existing_password = reset_windows_password(args.vm, args.zone, args.project, username)
        save_password_to_db(args.vm, existing_password)

    # Print out the username and password
    print(f"username: {username}")
    print(f"password: {existing_password}")

    # Clean up temporary files
    cleanup('tmp', 'nohup.out')

# Run the main logic
if __name__ == '__main__':
    main()
