# inventory-sheets
 This project is a system that automates inventory processing, saves logs in organized files, and sends updates to a Telegram group. In addition, the process is scheduled to run automatically twice a day.

# How to install
- python -m venv venv
- venv\Scripts\activate
- pip install -r requirements.txt
- Configure access to your sheets in credentials.py
- Grant access to your Google account using Google Cloud
- Configure telegram access in credentials.py
- Configure stock update times in scheduler.py
- run scheduler.py or main.py!
