name: Daily True Crime Briefing

on:
  schedule:
    # Run daily at 9:00 AM Pacific Time (5:00 PM UTC)
    - cron: '0 17 * * *'
  workflow_dispatch: # Allow manual trigger

jobs:
  generate-briefing:
    runs-on: ubuntu-latest
    
    permissions:
      contents: write
      issues: write
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        pip install anthropic PyGithub requests
        
    - name: Generate and publish briefing
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
        GITHUB_REPO: ${{ github.repository }}
      run: |
        python daily_briefing.py
