import anthropic
import os
import requests
import json
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrueCrimeBriefingGenerator:
    def __init__(self):
        # Initialize Anthropic client with error handling for GitHub Actions
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

import anthropic
import os
import requests
import json
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrueCrimeBriefingGenerator:
    def __init__(self):
        # Initialize Anthropic client with error handling for GitHub Actions
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

    def search_premium_publications(self):
        """Search specifically major newspapers and magazines for true crime stories"""
        print("🔍 Searching premium publications for true crime stories...")
        
        # Focus on major publications only
        publication_searches = [
            # Premium news sources with specific true crime terms
            "site:nytimes.com cold case DNA solved",
            "site:washingtonpost.com murder case new evidence", 
            "site:wsj.com criminal investigation closed",
            "site:latimes.com true crime arrest made",
            "site:chicagotribune.com murder conviction DNA",
            "site:atlanticmagazine.com criminal case",
            "site:newyorker.com true crime investigation",
            "site:vanityfair.com murder case documentary",
            "site:time.com cold case breakthrough",
            "site:thedailybeast.com criminal conviction"
        ]
        
        all_articles = []
        
        for search_term in publication_searches:
            try:
                print(f"🔍 Searching: {search_term}")
                
                # Use Google Custom Search for premium sources
                import urllib.parse
                import urllib.request
                from bs4 import BeautifulSoup
                
                encoded_query = urllib.parse.quote_plus(search_term)
                search_url = f"https://www.google.com/search?q={encoded_query}&tbm=nws&num=10"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                req = urllib.request.Request(search_url, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as response:
                    html = response.read().decode('utf-8')
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract news articles
                for article in soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd'):
                    title = article.get_text().strip()
                    
                    # Find the parent link
                    parent = article.find_parent('a')
                    if parent and parent.get('href'):
                        url = parent.get('href')
                        if url.startswith('/url?q='):
                            # Clean Google redirect URL
                            url = urllib.parse.unquote(url.split('/url?q=')[1].split('&')[0])
                        
                        # Only include major publications
                        major_pubs = [
                            'nytimes.com', 'washingtonpost.com', 'wsj.com', 
                            'latimes.com', 'chicagotribune.com', 'theatlantic.com',
                            'newyorker.com', 'vanityfair.com', 'time.com',
                            'thedailybeast.com', 'npr.org', 'cnn.com',
                            'abcnews.go.com', 'nbcnews.com', 'cbsnews.com'
                        ]
                        
                        if any(pub in url for pub in major_pubs):
                            all_articles.append({
                                'title': title,
                                'url': url,
                                'publication': next((pub for pub in major_pubs if pub in url), 'Unknown'),
                                'search_term': search_term
                            })
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                print(f"Error searching {search_term}: {str(e)}")
                continue
        
        print(f"📊 Found {len(all_articles)} articles from major publications")
        return all_articles

    def extract_article_details(self, url):
        """Extract journalist and article details from major publication URLs"""
        try:
            import urllib.request
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract byline/author info (varies by publication)
            author = None
            date = None
            
            # Try common author selectors
            author_selectors = [
                '[data-module="Byline"]',
                '.byline-author',
                '.author-name', 
                '.byline',
                '[rel="author"]',
                '.css-1baulvz',  # NYT specific
                '.author'
            ]
            
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = author_elem.get_text().strip()
                    break
            
            # Try to find publish date
            date_selectors = [
                'time[datetime]',
                '.publish-date',
                '.date',
                '.css-15w69y9'  # NYT specific
            ]
            
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date = date_elem.get('datetime') or date_elem.get_text().strip()
                    break
            
            return {
                'author': author or 'Author not found',
                'date': date or 'Date not found'
            }
            
        except Exception as e:
            return {
                'author': f'Error extracting author: {str(e)}',
                'date': 'Error extracting date'
            }

    def get_research_prompt(self):
        """Generate research prompt with all user requirements"""
        from datetime import datetime
        # Use actual current date - December 2024
        current_date = datetime.now().strftime('%B %d, %Y')
        
        return f"""
CONTENT DISCOVERY BRIEFING - {current_date}

I need you to provide 10 adjudicated true crime cases with RECENT developments (2023-2024) that meet these EXACT requirements:

CRITICAL: Use only REAL, RECENT cases from 2023-2024 with actual published articles. NO future information needed.

MANDATORY REQUIREMENTS:
1. REAL cases from 2023-2024 with actual article links from major publications
2. Journalist name and contact information when available
3. Cases that have resonated NATIONALLY (not local stories)
4. ONLY written articles from major newspapers/magazines
5. NO YouTube or local TV news
6. Focus on cases with RECENT developments (2023-2024)
7. ADJUDICATED cases only (legally resolved/closed)
8. NO Innocence Project or wrongful conviction cases
9. Include competitive verification against existing documentaries

PREMIUM SOURCES YOU HAVE ACCESS TO:
- The Atlantic, Vanity Fair, New Yorker, Wired
- NYMag, The Cut, Curbed  
- The New York Times, Time Magazine
- Chicago Tribune, LA Times, Washington Post, The Daily Beast
- Rolling Stone, Air Mail, The Atavist
- Philadelphia Inquirer, Bloomberg, Harper's, Business Insider
- Wall Street Journal, Boston Globe, Baltimore Banner
- Town & Country, Esquire, High Country News, Texas Monthly
- Outside Mag, SF Chronicle, Scientific American
- Oregonian, Sun Sentinel
- NO local news, NO YouTube, NO basic crime coverage

WHAT I DON'T WANT:
- Famous serial killer cases everyone knows about
- Cases that already have major documentaries (Golden State Killer, BTK, etc.)
- Hypothetical or example cases
- Cases without source articles and journalist names
- Future developments or speculative information

FOCUS ON: Recent developments in adjudicated cases from 2023-2024 that appeared in your premium publication list.

FORMAT REQUIRED:

**Case #[X] - [Tier] - [Case Type] - "[Actual Case Name]"**
- **Source Article:** [Full URL to actual article from 2023-2024]
- **Publication:** [Major newspaper/magazine name from approved list]
- **Journalist:** [Reporter name and contact if available]
- **Case Type:** Adjudicated w/New Development | Cold Case w/Fresh Evidence
- **Logline:** One compelling sentence
- **Key Details:** Real names, locations, timeline from article
- **Adjudication Status:** How case was legally resolved
- **RECENT Development:** What's new from 2023-2024 articles
- **National Significance:** Why this case has broad appeal beyond local interest
- **Competitive Verification:** Check against Netflix, HBO, Investigation Discovery, etc.
- **Development Recommendation:** GO/NO-GO with rationale

Use your knowledge of RECENT (2023-2024) true crime developments that appeared in major publications. Focus on lesser-known adjudicated cases with new developments that haven't been heavily covered by major documentaries.

Provide 10 cases from 2023-2024:
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
        
        # Get environment variables and clean them too
        sender_email = os.environ.get("GMAIL_ADDRESS", "").strip()
        sender_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
        
        # Check sender email for problematic characters
        print(f"📧 Checking sender email: {repr(sender_email)}")
        for i, char in enumerate(sender_email):
            if ord(char) >= 128:
                print(f"🚨 Bad character in sender email at position {i}: {repr(char)} (ord: {ord(char)})")
        
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
        
        recipients = ["danny@kontentfarm.com", "rod@kontentfarm.com"]
        
        # Create the most basic email possible
        subject = "Daily True Crime Briefing"
        
        print(f"📧 Using simple approach...")
        
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
            print(f"🔍 Unicode error details: {repr(e)}")
            
            # Try to locate the exact character
            if hasattr(e, 'start') and hasattr(e, 'object'):
                print(f"🚨 Problem at position {e.start} in: {repr(e.object[max(0, e.start-10):e.start+10])}")
            
            # Try sending without ANY formatting
            try:
                print("🔄 Trying with just content...")
                basic_msg = f"Subject: Briefing\n\n{super_clean(clean_content)}"
                server.sendmail(sender_email, recipients, basic_msg)
                server.quit()
                print("✅ Basic email sent!")
                return True
            except Exception as e2:
                print(f"❌ Even basic email failed: {str(e2)}")
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
            print("📝 Generating research briefing...")
            logger.info("Generating research briefing...")
            briefing = self.run_research()
            print(f"✅ Briefing generated successfully! Length: {len(briefing)} characters")
            
            # Send email
            print("📧 Attempting to send email...")
            logger.info("Sending email...")
            success = self.send_email(briefing)
            
            if success:
                print("✅ Email sent successfully!")
                logger.info("Daily briefing completed successfully!")
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
