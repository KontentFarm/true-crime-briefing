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

    def search_web_advanced(self, query):
        """Advanced web search with multiple sources"""
        results = []
        
        try:
            # Search Google News via RSS (more reliable)
            import urllib.parse
            import urllib.request
            from bs4 import BeautifulSoup
            import xml.etree.ElementTree as ET
            
            # Google News RSS search
            encoded_query = urllib.parse.quote_plus(query)
            news_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(news_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                xml_content = response.read()
            
            root = ET.fromstring(xml_content)
            for item in root.findall('.//item'):
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                pub_date = item.find('pubDate')
                
                if title is not None and link is not None:
                    results.append({
                        'title': title.text,
                        'url': link.text,
                        'description': description.text if description is not None else '',
                        'date': pub_date.text if pub_date is not None else ''
                    })
            
            return results[:10]
            
        except Exception as e:
            print(f"Advanced search error: {str(e)}")
            return []

    def search_current_cases(self):
        """Comprehensive search for current true crime cases"""
        print("🔍 Conducting comprehensive true crime search...")
        
        # More specific and current search terms
        search_queries = [
            "true crime cold case solved 2025",
            "DNA evidence new arrest murder",
            "criminal conviction overturned 2025", 
            "murder case new evidence witness",
            "serial killer identified DNA genealogy",
            "cold case breakthrough forensics",
            "true crime documentary development",
            "murder trial verdict guilty 2025",
            "criminal investigation closed solved",
            "forensic evidence new technology crime"
        ]
        
        all_results = []
        for query in search_queries:
            print(f"🔍 Searching: {query}")
            results = self.search_web_advanced(query)
            if results:
                all_results.extend(results)
                print(f"   Found {len(results)} results")
            time.sleep(2)  # More conservative rate limiting
        
        print(f"📊 Total search results: {len(all_results)}")
        return all_results

    def get_research_prompt(self):
        """Generate the research prompt with extensive search results"""
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Get comprehensive search results
        search_results = self.search_current_cases()
        
        # Format search results with more detail
        search_results_text = ""
        for i, result in enumerate(search_results[:30], 1):
            search_results_text += f"{i}. {result['title']}\n   URL: {result['url']}\n   Description: {result['description'][:200]}...\n   Date: {result['date']}\n\n"
        
        return f"""
## ROLE DEFINITION
You are an elite content discovery specialist. You MUST analyze these REAL search results and provide 10 ACTUAL cases.

## CURRENT DATE: {current_date}

## REAL SEARCH RESULTS FROM CURRENT NEWS
{search_results_text}

## CRITICAL INSTRUCTIONS - READ CAREFULLY

**YOU MUST:**
1. Analyze the search results above - these are REAL current news stories
2. Select 10 cases that meet the criteria from these REAL results
3. Provide full analysis for each REAL case
4. NO explanations about limitations or access issues
5. NO disclaimers about hypothetical nature
6. ONLY work with the REAL information provided above

**CASE SELECTION CRITERIA:**
- Focus on adjudicated cases with new developments
- Cold cases with DNA breakthroughs
- Murder cases with new evidence
- Cases where perpetrators have been convicted/sentenced
- NO ongoing trials or active investigations

**STRICT EXCLUSIONS:**
- NO Innocence Project or wrongful conviction cases
- NO ongoing investigations
- NO cases still in active litigation

## OUTPUT FORMAT

**Subject Line:** "Daily Content Discovery Briefing - {current_date} - 10 Premium Development Opportunities"

**Provide exactly 10 cases in this format:**

**Case #[1-10] - [TIER 1/2/3] - [Case Type] - "[Case Name]"**
- **Case Type:** Adjudicated w/New Development | Cold Case w/Fresh Evidence
- **Logline:** One compelling sentence about the case
- **Key Details:** Timeline, location, victim/perpetrator names from search results
- **ADJUDICATION STATUS:** Case resolution status
- **NEW DEVELOPMENT SUMMARY:** What's new about this case
- **Production Assets:** Potential interview subjects, documents, footage
- **COMPETITIVE VERIFICATION:** Check against major networks/platforms
- **Development Recommendation:** GO/NO-GO with rationale
- **Next Steps:** Specific production actions

**MANDATORY REQUIREMENTS:**
- Use ONLY the real search results provided above
- Extract actual case names, locations, and details from the news stories
- Provide 10 complete case analyses
- Focus on cases suitable for documentary production
- NO explanations about limitations

**START WITH CASE #1 AND CONTINUE THROUGH CASE #10. USE THE REAL SEARCH RESULTS ABOVE.**

**BEGIN YOUR ANALYSIS NOW:**
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
