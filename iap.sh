#!/bin/bash
set -e # Exit on error
trap 'rm -f tmp nohup.out' EXIT # Cleanup temporary files

# Function to start IAP tunnel and run xfreerdp
start_rdp() {
  local vm="$1"
  local zone="$2"
  local project="$3"

  # Get username and password using the Python script
  output=$(python3 iap-macos.py --vm "$vm" --zone "$zone" --project "$project")

  # Parse the output into 'username' and 'password' variables
  username=$(echo "$output" | grep "username:" | cut -d' ' -f2-)
  password=$(echo "$output" | grep "password:" | cut -d' ' -f2-)

  # Start the IAP tunnel in the background
  nohup gcloud compute start-iap-tunnel "$vm" 3389 --zone "$zone" --project "$project" &
  sleep 5

  # Retrieve the port number from the IAP tunnel output
  port=$(grep "unused port" nohup.out | cut -d '[' -f 2 | sed 's/].//g')

  # Check if the port was retrieved successfully
  if [ -z "$port" ]; then
      echo "Failed to retrieve port from IAP tunnel output."
      exit 1
  fi

  # Open XQuartz and run xfreerdp
  open -a XQuartz
  export DISPLAY=:0
  xfreerdp /v:localhost:$port /u:$username /p:$password /clipboard /cert:ignore
}

# Function to list compute instances in a project
get_instances() {
  local project="$1"

  # Run gcloud compute instances list to show instances in the given project
  gcloud compute instances list --project "$project"
}

# Function to list all Google Cloud projects
get_projects() {
  # Run gcloud projects list to show all available projects
  gcloud projects list
}

# Main logic to parse the usage arguments and call the appropriate function
if [ "$1" == "rdp" ]; then
  if [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
    echo "Usage: bash iap.sh rdp <vm> <zone> <project>"
    exit 1
  fi
  start_rdp "$2" "$3" "$4"
elif [ "$1" == "get-instances" ]; then
  if [ -z "$2" ]; then
    echo "Usage: bash iap.sh get-instances <project>"
    exit 1
  fi
  get_instances "$2"
elif [ "$1" == "get-projects" ]; then
  get_projects
else
  echo "Usage: bash iap.sh <rdp|get-instances|get-projects> <vm> <zone> <project> or <project>"
  exit 1
fi
