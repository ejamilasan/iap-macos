import sqlite3
import argparse

# Setup argument parser to get the VM name
parser = argparse.ArgumentParser(description="Remove a server entry from the passwords database")
parser.add_argument('--vm', required=True, help="The VM name to remove from the database")
args = parser.parse_args()

# SQLite database file
DB_FILE = 'passwords.db'

# Function to remove a server entry from the database
def remove_vm_entry(vm_name):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM passwords WHERE vm_name = ?', (vm_name,))
            conn.commit()
            if c.rowcount > 0:
                print(f"Entry for VM '{vm_name}' has been removed from the database.")
            else:
                print(f"No entry found for VM '{vm_name}'.")
    except sqlite3.Error as e:
        print(f"Error removing entry: {e}")

# Main function
def main():
    vm_name = args.vm
    remove_vm_entry(vm_name)

# Run the main logic
if __name__ == '__main__':
    main()
