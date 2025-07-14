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
        """Generate educational research prompt (not commercial)"""
        from datetime import datetime
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Still search for current articles for context
        real_articles = self.search_real_news_api()
        
        articles_context = ""
        if real_articles:
            articles_context = f"Found {len(real_articles)} recent investigative articles for context.\n\n"
        
        return f"""
**Research Request - {current_date}**

{articles_context}I'm conducting research on investigative journalism and need help identifying prominent American investigative journalists who have published compelling work in major publications.

**Research Focus:**
Please help me identify journalists who specialize in:
- True crime investigations
- Financial fraud and corporate misconduct
- Unusual stories and scandals
- Long-form investigative pieces

**Publications to consider:**
The Atlantic, Vanity Fair, New Yorker, Wired, NYMag, The Cut, New York Times, Time Magazine, Chicago Tribune, LA Times, Washington Post, The Daily Beast, Rolling Stone, Bloomberg, Harper's, Business Insider, Wall Street Journal, Boston Globe, and other major national publications.

**What I need:**
Please provide information about 5 investigative journalists, including:
- Their name and primary publication
- Their area of specialization 
- Notable published investigations or series
- Professional background information that's publicly available

**Research approach:**
Focus on journalists whose work demonstrates strong investigative skills and has generated significant public interest. Look for writers who have covered complex stories that might translate well to other media formats.

**Educational context:**
This research is for understanding current trends in investigative journalism and identifying examples of high-impact reporting in major publications.

Please provide your analysis of 5 notable investigative journalists who meet these criteria.
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
