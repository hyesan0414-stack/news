name: Auto News Clipping

on:
  schedule:
    - cron: "0 0 * * *"   # KST 09:00 (UTC 00:00)
    - cron: "0 9 * * *"   # KST 18:00 (UTC 09:00)
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repo
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"

    - name: Install dependencies
      run: pip install feedparser requests pytz

    - name: Run script
      env:
        NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
        NOTION_DB_ID: ${{ secrets.NOTION_DB_ID }}
      run: python update_notion.py
