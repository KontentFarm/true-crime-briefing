import anthropic
import os
import requests
import json
import smtplib
import logging
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrueCrimeBriefingGenerator:
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
            
        self.sender_email = os.getenv('GMAIL_ADDRESS')
        self.gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        self._validate_environment()

    def _validate_environment(self):    
        """Validate all required environment variables are present."""
        required_vars = ['ANTHROPIC_API_KEY', 'GMAIL_ADDRESS', 'GMAIL_APP_PASSWORD']
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
        """Generate the true crime briefing research prompt"""
        from datetime import datetime
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Search for current articles for context
        real_articles = self.search_real_news_api()
        
        articles_context = ""
        if real_articles:
            articles_context = f"Found {len(real_articles)} recent true crime articles for context.\n\n"
        
        return f"""
**DAILY TRUE CRIME & STRANGER THAN FICTION CONTENT DISCOVERY BRIEFING**
**Date: {current_date}**

{articles_context}As an elite content discovery specialist operating at the level of the top 0.01% researchers in the world, I need you to identify and analyze 5 premium true crime cases and "stranger than fiction" stories for content development opportunities.

**MISSION PARAMETERS:**
- Discover breaking or developing stories with high production potential
- Focus on streaming, broadcast, and cable network development
- Emphasize compelling narratives, strong IP potential, and breakout formats

**RESEARCH FOCUS AREAS:**
- True crime cases with unusual circumstances or compelling characters
- "Stranger than fiction" real-life events that defy conventional explanation
- Stories generating significant media buzz and public fascination
- Cases with unresolved mysteries or ongoing developments
- Events with strong visual/documentary potential
- Adjudicated cases with new, never-before-seen developments
- Famous cold cases with fresh evidence, technology applications, or witness revelations

**CRITICAL REQUIREMENTS:**
1. **COMPETITIVE LANDSCAPE VERIFICATION:** Every case must be thoroughly checked against ALL major streaming, cable, and broadcast networks to ensure either:
   - NO existing major production coverage exists, OR
   - Substantial new developments justify fresh production approach

2. **PLATFORMS TO CHECK:**
   - Streaming: Netflix, Amazon Prime, Hulu, Apple TV+, HBO Max, Paramount+, Disney+, Peacock, Discovery+
   - Cable: Investigation Discovery, A&E, Lifetime, History Channel, TLC, Oxygen, Vice
   - Broadcast: CBS, NBC, ABC, Fox, PBS, Dateline NBC, 48 Hours, 20/20
   - Podcasts: Major true crime podcast networks

3. **CASE DISTRIBUTION REQUIRED:**
   - 2 TIER 1 Cases (Immediate Development Potential)
   - 2 TIER 2 Cases (Short-term Monitoring/Development)  
   - 1 TIER 3 Case (Long-term Archive/Future Consideration)

4. **CASE TYPE DISTRIBUTION:**
   - 2-3 Active/Breaking Cases
   - 1-2 Adjudicated Cases with New Developments
   - 1 Famous Cold Case with Fresh Evidence/Technology

**OUTPUT FORMAT REQUIRED:**

**EXECUTIVE SUMMARY:**
[Brief overview of today's most compelling discoveries and trending themes]

**CASE #1 - [TIER LEVEL] - [CASE TYPE] - [STORY TITLE]**
- **Case Type:** Active/Breaking | Adjudicated w/New Development | Cold Case w/Fresh Evidence
- **Logline:** [Compelling one-sentence hook]
- **Key Details:** [Timeline, location, principals involved]
- **NEW DEVELOPMENT SUMMARY:** [What makes this story fresh/different from prior coverage]
- **Production Assets:** [Available footage, documents, interview subjects]
- **Legal Status:** [Current investigations, proceedings, clearance issues]
- **COMPETITIVE VERIFICATION:**
  - **Platforms Searched:** [Complete list of networks/services checked]
  - **Previous Coverage Found:** [Any existing production details]
  - **New Development Differentiation:** [How new elements justify fresh production]
  - **Clearance Status:** CLEAR/NEW ANGLE APPROVED/FLAGGED/DISQUALIFIED
- **Development Recommendation:** GO/NO-GO with rationale
- **Next Steps:** [Specific actions required for advancement]

[REPEAT FORMAT FOR CASES #2-5]

**WEEKLY TRENDS ANALYSIS:**
- Emerging story patterns or themes
- Geographic hotspots for compelling content
- Seasonal or anniversary-driven opportunities
- Competitive intelligence alerts
- Forensic technology breakthrough alerts

**RESEARCH METHODOLOGY:**
- Use only verified, credible sources (major news outlets, police reports, court documents)
- Cross-reference multiple independent confirmations
- Avoid unverified social media rumors or single-source reporting
- Focus on stories that create compelling narratives and lean into fandoms
- Prioritize cases with strong IP and breakout format potential

**SEARCH FOCUS:**
Look for cases involving: DNA breakthroughs, genetic genealogy, wrongful convictions, death row appeals, new evidence, witness revelations, forensic technology applications, social media investigations, cold case reopenings, and stranger-than-fiction circumstances.

Execute this research with the analytical rigor of a federal investigation and the storytelling instincts of an award-winning documentarian like Alex Gibney or Joe Berlinger.

**CRITICAL:** Every case must either be completely untouched by major productions OR have substantial new developments that occurred within the last 2 years that justify fresh production coverage.
        """

    def run_research(self):
        """Execute the daily research protocol"""
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

    def send_email(self, briefing_content):
        """Send the briefing via Gmail SMTP"""
        
        print("🔧 Setting up Gmail SMTP configuration...")
        
        # Ultra-simple content cleaning
        def super_clean(text):
            """Remove ALL non-printable ASCII characters"""
            if not text:
                return ""
            
            # Keep only characters 32-126 (printable ASCII) plus newline (10) and carriage return (13)
            result = ""
            for char in str(text):
                code = ord(char)
                if 32 <= code <= 126 or code in [10, 13]:  # Printable ASCII + newlines
                    result += char
                else:
                    result += " "  # Replace with space
            
            return result.strip()
        
        # Clean everything
        clean_content = super_clean(briefing_content)
        print(f"📝 Content super-cleaned: {len(briefing_content)} -> {len(clean_content)} characters")
        
        # Get environment variables and clean them too
        sender_email = os.environ.get("GMAIL_ADDRESS", "").strip()
        sender_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
        
        print(f"📧 Sender email: {sender_email}")
        print(f"🔑 Gmail App Password present: {'Yes' if sender_password else 'No'}")
        
        recipients = ["danny@kontentfarm.com"]
        
        # Create the email subject with current date
        current_date = datetime.now().strftime('%B %d, %Y')
        subject = f"Daily Content Discovery Briefing - {current_date} - 5 Premium Development Opportunities"
        
        print(f"📧 Using subject: {subject}")
        
        try:
            print("🌐 Connecting to Gmail SMTP server...")
            server = smtplib.SMTP("smtp.gmail.com", 587)
            print("🔐 Starting TLS encryption...")
            server.starttls()
            print("🔑 Logging in to Gmail...")
            server.login(sender_email, sender_password)
            
            # Create email manually with minimal formatting
            email_text = f"""From: {sender_email}
To: {', '.join(recipients)}
Subject: {subject}

{clean_content}
"""
            
            # Final cleaning of email text
            final_email = super_clean(email_text)
            
            print(f"📧 Final email preview: {repr(final_email[:100])}")
            
            # Check one more time for bad characters
            bad_found = False
            for i, char in enumerate(final_email):
                if ord(char) >= 128:
                    print(f"🚨 STILL FOUND BAD CHAR at {i}: {repr(char)} (ord: {ord(char)})")
                    bad_found = True
            
            if not bad_found:
                print("✅ Email is completely clean!")
            
            print("📤 Sending ultra-basic email...")
            
            # Try the most basic send possible
            server.sendmail(sender_email, recipients, final_email)
            server.quit()
            
            print("✅ Email sent successfully via Gmail!")
            logger.info("Email sent successfully via Gmail!")
            return True
            
        except UnicodeEncodeError as e:
            print(f"❌ Unicode error: {str(e)}")
            return False
                
        except Exception as e:
            print(f"❌ General error: {str(e)}")
            print(f"🔍 Error type: {type(e)}")
            return False

    def run_daily_briefing(self):
        """Main execution function"""
        print(f"🚀 Starting daily briefing for {datetime.now().strftime('%B %d, %Y')}")
        logger.info(f"Starting daily briefing for {datetime.now().strftime('%B %d, %Y')}")
        
        try:
            # Generate research briefing
            print("📝 Generating 5-case research briefing...")
            logger.info("Generating 5-case research briefing...")
            briefing = self.run_research()
            print(f"✅ Briefing generated successfully! Length: {len(briefing)} characters")
            
            # Send email
            print("📧 Attempting to send email...")
            logger.info("Sending email...")
            success = self.send_email(briefing)
            
            if success:
                print("✅ Email sent successfully!")
                logger.info("Daily 5-case briefing completed successfully!")
            else:
                print("❌ Email failed to send!")
                logger.error("Daily briefing generated but email failed to send.")
                print("Briefing content preview:")
                print(briefing[:500] + "..." if len(briefing) > 500 else briefing)
                
        except Exception as e:
            print(f"❌ Critical error in run_daily_briefing: {str(e)}")
            logger.error(f"Critical error in run_daily_briefing: {str(e)}")
            raise

if __name__ == "__main__":
    briefing_system = TrueCrimeBriefingGenerator()
    briefing_system.run_daily_briefing()
