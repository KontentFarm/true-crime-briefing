name: Daily True Crime Briefing

on:
  schedule:
    - cron: '0 17 * * *'  # 9 AM Pacific Time
  workflow_dispatch:

jobs:
  send-briefing:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run daily briefing
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        GMAIL_ADDRESS: ${{ secrets.GMAIL_ADDRESS }}
        GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
        NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
      run: python daily_briefing.py
