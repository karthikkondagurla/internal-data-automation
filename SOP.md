# Standard Operating Procedure (SOP): Internal Data Automation

## What is this system?
This system automates the daily collection of stock market data and finance news. instead of manually checking websites and spreadsheets, this tool fetches the data, saves it safely, and creates a daily report for you.

## How to Run the Daily Sync

**Step 1: Open Terminal**
- Open Command Prompt or PowerShell (Windows) or Terminal (Mac/Linux).

**Step 2: Navigate to the Project Folder**
- Type `cd path/to/internal-data-automation` and press Enter.

**Step 3: Run the Command**
- Type the following command and press Enter:
  ```bash
  python run_pipeline.py
  ```

**Step 4: Wait for Completion**
- You will see messages appearing on the screen.
- Wait until you see: `Reporting stage completed`.

## Where to Find Reports
After the run is complete, go to the **`reports`** folder inside the project directory.
- **Summary**: Look for a text file named like `summary_2026-02-08.txt`. It tells you how many records were collected.
- **Excel Data**: Look for a CSV file named like `market_data_2026-02-08.csv`. You can open this in Excel.

## Troubleshooting

### "Command not found" or "python is not recognized"
- Ensure Python is installed on your computer.
- Try using `py run_pipeline.py` instead of `python ...`.

### "API key not configured" Warning
- The system ran, but didn't fetch new data because the passwords (API keys) are missing.
- Contact the technical team to update the `config.yaml` file with valid keys.

### "Error initializing pipeline"
- Check the `logs/pipeline.log` file for detailed error messages.
- Provide this log file to the technical support team.
