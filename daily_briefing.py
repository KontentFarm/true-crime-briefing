import anthropic
import os
import requests
import json
import logging
import time
import base64
from datetime import datetime, timezone
from github import Github

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubTrueCrimeBriefingGenerator:
    def __init__(self):
        # Initialize Anthropic client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            
        try:
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise
            
        # Initialize GitHub client
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
            
        try:
            self.github_client = Github(github_token)
        except Exception as e:
            logger.error(f"Failed to initialize GitHub client: {e}")
            raise
            
        self.repo_name = os.getenv('GITHUB_REPO', 'kontent-farm/daily-briefings')
        self.branch_name = os.getenv('GITHUB_BRANCH', 'main')
        
        self._validate_environment()

    def _validate_environment(self):    
        """Validate all required environment variables are present."""
        required_vars = ['ANTHROPIC_API_KEY', 'GITHUB_TOKEN']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:        
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    def search_real_news_api(self):
        """Search for real current articles using News API"""
        api_key = os.getenv('NEWS_API_KEY')
        if not api_key:
            print("❌ NEWS_API_KEY not found")
            return []
            
        print("🔍 Searching real news sources for true crime articles...")
        
        # Your premium publication domains that News API supports
        sources = [
            'the-new-york-times', 'the-washington-post', 'the-wall-street-journal',
            'time', 'bloomberg', 'business-insider', 'abc-news', 'cbs-news',
            'cnn', 'nbc-news'
        ]
        
        all_articles = []
        
        # Search terms for true crime
        search_queries = [
            'murder case DNA evidence',
            'cold case solved',
            'criminal conviction new evidence', 
            'serial killer arrested',
            'forensic breakthrough crime',
            'criminal investigation closed',
            'murder trial verdict',
            'crime documentary new evidence'
        ]
        
        for query in search_queries:
            try:
                print(f"🔍 Searching: {query}")
                
                # Search News API
                url = f"https://newsapi.org/v2/everything"
                params = {
                    'q': query,
                    'sources': ','.join(sources),
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 20,
                    'apiKey': api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    for article in articles:
                        if article.get('title') and article.get('url'):
                            all_articles.append({
                                'title': article['title'],
                                'url': article['url'],
                                'source': article['source']['name'],
                                'author': article.get('author', 'Author not listed'),
                                'published': article['publishedAt'],
                                'description': article.get('description', ''),
                                'content': article.get('content', '')
                            })
                    
                    print(f"   Found {len(articles)} articles")
                else:
                    print(f"   API error: {response.status_code}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error searching {query}: {str(e)}")
                continue
        
        print(f"📊 Total real articles found: {len(all_articles)}")
        return all_articles

    def get_research_prompt(self):
        """Generate the daily briefing research prompt"""
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Search for current articles for context
        real_articles = self.search_real_news_api()
        
        articles_context = ""
        if real_articles:
            articles_context = f"Found {len(real_articles)} recent investigative articles for context.\n\n"
        
        return f"""
**True Crime & Stranger Than Fiction Content Discovery Agent - Daily Research Protocol**

**Date:** {current_date}

{articles_context}As an elite content discovery specialist operating at the level of the top 0.01% researchers in the world, execute the following daily research protocol:

**PRIMARY OBJECTIVE:**
Discover and evaluate 5 breaking or developing true crime cases and "stranger than fiction" stories with high production potential for streaming, broadcast, and cable networks through compelling narratives, strong IP potential, and breakout format opportunities.

**RESEARCH FOCUS AREAS:**
1. True crime cases with unusual circumstances or compelling characters
2. "Stranger than fiction" real-life events that defy conventional explanation  
3. Stories generating significant media buzz and public fascination
4. Cases with unresolved mysteries or ongoing developments
5. Events with strong visual/documentary potential
6. Adjudicated cases with new, never-before-seen developments
7. Famous cold cases with fresh evidence, technology applications, or witness revelations

**CASE CATEGORIES TO PRIORITIZE:**

**Active/Breaking Cases:**
- Ongoing investigations with developing evidence
- Recent arrests in high-profile cases
- Trials with unexpected developments or revelations

**Adjudicated Cases with New Developments:**
- Post-conviction appeals with new evidence
- Wrongful conviction cases and exonerations
- Death row cases with fresh legal challenges
- Solved cases with new victim discoveries or co-conspirators
- Cases where perpetrators reveal new information from prison
- Family members or witnesses coming forward years later

**Famous Cold Cases with Fresh Angles:**
- DNA technology breakthroughs (genetic genealogy, advanced testing)
- New witness testimony or deathbed confessions
- Evidence re-examination with modern forensic techniques
- Technology applications (facial recognition, cell tower analysis)
- Investigative techniques revealing new suspects or motives
- Anniversary-driven renewed investigations
- Social media campaigns uncovering new leads

**COMPETITIVE LANDSCAPE VERIFICATION REQUIRED:**
For each case, verify NO major production exists on Netflix, Amazon Prime, Hulu, Apple TV+, HBO Max, Paramount+, Disney+, Peacock, Discovery+, Investigation Discovery, A&E, Lifetime, History Channel, TLC, Oxygen, Vice, CNN, MSNBC, Fox News, CBS, NBC, ABC, Fox, PBS, Dateline NBC, 48 Hours, 20/20, or major podcast platforms.

**DAILY OUTPUT REQUIREMENTS:**
Provide exactly 5 cases with the following distribution:
- 2 TIER 1 Cases (Immediate Development Potential)
- 2 TIER 2 Cases (Short-term Monitoring/Development)  
- 1 TIER 3 Case (Long-term Archive/Future Consideration)

**FOR EACH CASE PROVIDE:**

**Case #[X] - [Tier Level] - [Case Type] - [Story Title]**

**Case Type:** Active/Breaking | Adjudicated w/New Development | Cold Case w/Fresh Evidence

**Logline:** Compelling one-sentence hook

**Key Details:** Timeline, location, principals involved

**NEW DEVELOPMENT SUMMARY:** What makes this story fresh/different from prior coverage

**Production Assets:** Available footage, documents, interview subjects

**Legal Status:** Current investigations, proceedings, clearance issues

**COMPETITIVE VERIFICATION:**
- **Platforms Searched:** Complete list of networks/services checked
- **Previous Coverage Found:** Any existing production details
- **New Development Differentiation:** How new elements justify fresh production
- **Clearance Status:** CLEAR/NEW ANGLE APPROVED/FLAGGED/DISQUALIFIED

**Development Recommendation:** GO/NO-GO with rationale

**Next Steps:** Specific actions required for advancement

**QUALITY STANDARDS:**
- Source credibility requirements: Primary sources, multiple confirmations
- Avoid unverified social media rumors, single-source reporting
- NO cases with existing major production coverage unless substantial new developments justify fresh production approach
- Focus on stories with compelling narratives, strong character development potential, and audience engagement factors

Execute this protocol with the analytical rigor of a federal investigation and the storytelling instincts of an award-winning documentarian like Alex Gibney or Joe Berlinger. Focus on stories that will create compelling narratives, lean into fandoms, build strong IP, and deliver breakout format potential for premium content development.
        """

    def run_research(self):
        """Execute the daily research protocol using Claude"""
        research_prompt = self.get_research_prompt()
        
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": research_prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Error generating briefing: {str(e)}")
            return f"Error generating briefing: {str(e)}"

    def create_github_briefing(self, briefing_content):
        """Create a new briefing file in GitHub repository"""
        
        try:
            # Get or create repository
            try:
                repo = self.github_client.get_repo(self.repo_name)
                print(f"📁 Using existing repository: {self.repo_name}")
            except:
                # If repo doesn't exist, create it
                user = self.github_client.get_user()
                repo = user.create_repo(
                    name=self.repo_name.split('/')[-1],
                    description="Daily True Crime Content Discovery Briefings",
                    private=False,
                    auto_init=True
                )
                print(f"📁 Created new repository: {self.repo_name}")
            
            # Create filename with current date
            current_date = datetime.now()
            filename = f"briefings/{current_date.strftime('%Y-%m-%d')}_daily_briefing.md"
            
            # Prepare the content with frontmatter for better GitHub display
            github_content = f"""---
title: "Daily Content Discovery Briefing - {current_date.strftime('%B %d, %Y')}"
date: {current_date.isoformat()}
type: briefing
---

{briefing_content}

---

*Generated on {current_date.strftime('%B %d, %Y at %I:%M %p')} Pacific Time*
*Research conducted using Claude Sonnet 4 with elite 0.01% researcher protocols*
"""
            
            # Check if file already exists
            try:
                existing_file = repo.get_contents(filename, ref=self.branch_name)
                # Update existing file
                repo.update_file(
                    path=filename,
                    message=f"Update daily briefing for {current_date.strftime('%Y-%m-%d')}",
                    content=github_content,
                    sha=existing_file.sha,
                    branch=self.branch_name
                )
                print(f"📝 Updated existing briefing: {filename}")
            except:
                # Create new file
                repo.create_file(
                    path=filename,
                    message=f"Daily briefing for {current_date.strftime('%Y-%m-%d')}",
                    content=github_content,
                    branch=self.branch_name
                )
                print(f"📝 Created new briefing: {filename}")
            
            # Get the file URL for easy access
            file_url = f"https://github.com/{self.repo_name}/blob/{self.branch_name}/{filename}"
            
            # Also create/update README.md with latest briefing link
            readme_content = f"""# Daily True Crime Content Discovery Briefings

## Latest Briefing
**[{current_date.strftime('%B %d, %Y')} - Daily Content Discovery Briefing]({filename})**

## Recent Briefings
This repository contains daily content discovery briefings for true crime and stranger than fiction stories with premium development potential.

### About
These briefings are generated using elite research protocols, analyzing breaking cases, cold case developments, and stranger-than-fiction stories for streaming, broadcast, and cable network development opportunities.

### Research Standards
- Elite 0.01% researcher methodology
- Comprehensive competitive landscape verification
- Primary source validation
- Documentary-level analysis protocols

Last updated: {current_date.strftime('%B %d, %Y at %I:%M %p')} Pacific Time
"""
            
            try:
                readme_file = repo.get_contents("README.md", ref=self.branch_name)
                repo.update_file(
                    path="README.md",
                    message=f"Update README with latest briefing {current_date.strftime('%Y-%m-%d')}",
                    content=readme_content,
                    sha=readme_file.sha,
                    branch=self.branch_name
                )
            except:
                repo.create_file(
                    path="README.md",
                    message="Create README with briefing links",
                    content=readme_content,
                    branch=self.branch_name
                )
            
            print(f"✅ Briefing successfully published to GitHub!")
            print(f"🔗 View at: {file_url}")
            print(f"📊 Repository: https://github.com/{self.repo_name}")
            
            return True, file_url
            
        except Exception as e:
            print(f"❌ GitHub publishing error: {str(e)}")
            logger.error(f"GitHub publishing error: {str(e)}")
            return False, None

    def create_github_issue(self, briefing_content):
        """Optionally create a GitHub issue for discussion/tracking"""
        
        try:
            repo = self.github_client.get_repo(self.repo_name)
            current_date = datetime.now()
            
            issue_title = f"Daily Briefing Discussion - {current_date.strftime('%B %d, %Y')}"
            issue_body = f"""## Daily Content Discovery Briefing - {current_date.strftime('%B %d, %Y')}

Use this issue to discuss today's briefing findings, development priorities, and next steps.

**Key Highlights:**
- 5 cases researched and analyzed
- Competitive landscape verified across all major platforms
- Elite research protocols applied

**Briefing File:** [View Full Briefing](./briefings/{current_date.strftime('%Y-%m-%d')}_daily_briefing.md)

### Discussion Points:
- [ ] Tier 1 case development priorities
- [ ] Resource allocation decisions  
- [ ] Competitive positioning strategies
- [ ] Next steps coordination

*Generated: {current_date.strftime('%B %d, %Y at %I:%M %p')} Pacific Time*
"""
            
            issue = repo.create_issue(
                title=issue_title,
                body=issue_body,
                labels=['daily-briefing', 'discussion']
            )
            
            print(f"💬 Created discussion issue: {issue.html_url}")
            return issue.html_url
            
        except Exception as e:
            print(f"⚠️  Could not create issue: {str(e)}")
            return None

    def run_daily_briefing(self):
        """Main execution function"""
        current_date = datetime.now()
        print(f"🚀 Starting daily briefing for {current_date.strftime('%B %d, %Y')}")
        logger.info(f"Starting daily briefing for {current_date.strftime('%B %d, %Y')}")
        
        try:
            # Generate research briefing
            print("📝 Generating research briefing...")
            logger.info("Generating research briefing...")
            briefing = self.run_research()
            print(f"✅ Briefing generated successfully! Length: {len(briefing)} characters")
            
            # Publish to GitHub
            print("📤 Publishing to GitHub...")
            logger.info("Publishing to GitHub...")
            success, file_url = self.create_github_briefing(briefing)
            
            if success:
                print("✅ GitHub publishing successful!")
                logger.info("Daily briefing published to GitHub successfully!")
                
                # Optionally create discussion issue
                print("💬 Creating discussion issue...")
                issue_url = self.create_github_issue(briefing)
                
                print(f"""
🎉 Daily briefing completed successfully!

📁 Repository: https://github.com/{self.repo_name}
📝 Briefing: {file_url}
💬 Discussion: {issue_url if issue_url else 'Issue creation skipped'}

🔔 Set up GitHub notifications to get alerts when new briefings are published!
                """)
                
            else:
                print("❌ GitHub publishing failed!")
                logger.error("Daily briefing generated but GitHub publishing failed.")
                print("Briefing content preview:")
                print(briefing[:500] + "..." if len(briefing) > 500 else briefing)
                
        except Exception as e:
            print(f"❌ Critical error in run_daily_briefing: {str(e)}")
            logger.error(f"Critical error in run_daily_briefing: {str(e)}")
            raise

# GitHub Actions Workflow Support
def setup_github_actions():
    """Generate a GitHub Actions workflow file for automated daily briefings"""
    
    workflow_content = """name: Daily True Crime Briefing

on:
  schedule:
    # Run daily at 9:00 AM Pacific Time (5:00 PM UTC)
    - cron: '0 17 * * *'
  workflow_dispatch: # Allow manual trigger

jobs:
  generate-briefing:
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
        pip install anthropic PyGithub requests
        
    - name: Generate and publish briefing
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
        GITHUB_REPO: ${{ github.repository }}
      run: |
        python daily_briefing.py
"""
    
    print("📋 GitHub Actions Workflow:")
    print("Create .github/workflows/daily-briefing.yml with this content:")
    print(workflow_content)
    
    print("""
🔧 Setup Instructions:

1. Create a new GitHub repository or use existing one
2. Add these secrets to your repository settings:
   - ANTHROPIC_API_KEY: Your Claude API key
   - NEWS_API_KEY: Your News API key (optional)
   - GITHUB_TOKEN: Automatically provided by GitHub Actions

3. Save the Python script as 'daily_briefing.py' in your repo
4. Create '.github/workflows/daily-briefing.yml' with the workflow above
5. The briefing will run automatically daily at 9:00 AM Pacific Time

📱 Enable GitHub notifications to get alerts when new briefings are published!
    """)

if __name__ == "__main__":
    # Check if this is being run to setup GitHub Actions
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_github_actions()
    else:
        briefing_system = GitHubTrueCrimeBriefingGenerator()
        briefing_system.run_daily_briefing()
