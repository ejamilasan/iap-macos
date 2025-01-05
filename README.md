# iap-macos
## Why?
* IAP Desktop is not an option in MacOS. This is to help with IAP local user creation and starting an IAP Tunnel connection via CLI.

## Pre-requisite
* Install [freerdp](https://github.com/freerdp/freerdp?tab=readme-ov-file)
    ```bash
    brew install freerdp
    brew install --cask xquartz
    ```

## Usage
1. Auth to `gcloud`
    ```bash
    gcloud auth application-default login
    ```
2. run `./iap.sh`
    * To connect to a VM:
        ```bash
        ./iap.sh rdp <vm name> <zone> <project>
        ```
    * To get list of instances in a GCP Project:
        ```bash
        ./iap.sh get-instances <project>
        ```
    * To get list of Projects in GCP:
        ```bash
        ./iap.sh get-projects
        ```