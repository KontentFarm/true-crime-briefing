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

    def search_web(self, query, max_results=10):
        """Search the web for current information"""
        try:
            # Using DuckDuckGo search (free, no API key required)
            import urllib.parse
            import urllib.request
            from bs4 import BeautifulSoup
            
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
            
            soup = BeautifulSoup(html, 'html.parser')
            results = []
            
            # Extract search results
            for result in soup.find_all('a', class_='result__url')[:max_results]:
                link = result.get('href', '')
                if link.startswith('http'):
                    results.append(link)
            
            return results[:max_results]
            
        except Exception as e:
            print(f"Web search error: {str(e)}")
            return []

    def search_current_cases(self):
        """Search for current true crime cases and developments"""
        print("🔍 Searching for current true crime cases...")
        
        search_queries = [
            "true crime new evidence 2025",
            "cold case solved DNA 2025", 
            "murder case new development",
            "criminal conviction appeal 2025",
            "forensic breakthrough crime",
            "true crime documentary new",
            "criminal case new witness",
            "murder trial verdict 2025"
        ]
        
        all_results = []
        for query in search_queries:
            print(f"🔍 Searching: {query}")
            results = self.search_web(query, max_results=5)
            all_results.extend(results)
            time.sleep(1)  # Rate limiting
        
        return all_results

    def get_research_prompt(self):
        """Generate the research prompt with current date and search results"""
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Get current search results
        search_results = self.search_current_cases()
        search_results_text = "\n".join([f"- {url}" for url in search_results[:20]])
        
        return f"""
## ROLE DEFINITION
You are an elite content discovery specialist operating at the level of the top 0.01% researchers in the world. Your mission is to identify, analyze, and assess true crime cases and "stranger than fiction" stories for premium content development opportunities.

## CURRENT DATE: {current_date}

## REAL-TIME SEARCH RESULTS
I have conducted web searches for current true crime developments. Here are recent search results to analyze:

{search_results_text}

## DAILY MISSION PARAMETERS

**Primary Objective:** Discover and evaluate REAL breaking or developing stories with high production potential for streaming, broadcast, and cable networks.

**CRITICAL INSTRUCTION: You MUST provide 10 REAL cases from current news sources. NO hypothetical cases. NO explanations about limitations. ONLY real, current cases with actual details.**

## RESEARCH METHODOLOGY

**1. PREMIUM SOURCE MONITORING PRIORITIES**
**Tier 1 Premium Sources (With Access):**
- The New York Times, Washington Post, The Atlantic, Vanity Fair
- New Yorker, Wired, NYMag, The Cut, Curbed
- Time Magazine, Chicago Tribune, LA Times, The Daily Beast

**2. CASE REQUIREMENTS - REAL CASES ONLY**

**Focus: ADJUDICATED CASES WITH NEW DEVELOPMENTS:**
- Post-conviction appeals with new evidence (EXCLUDING wrongful conviction/exoneration cases)
- Solved cases with new victim discoveries or co-conspirators
- Cases where perpetrators reveal new information from prison
- Family members or witnesses coming forward with new details
- New forensic analysis of closed cases
- Documentary crews uncovering previously unknown evidence

**Famous Cold Cases with Fresh Angles:**
- DNA technology breakthroughs providing new leads
- New witness testimony or deathbed confessions
- Evidence re-examination with modern forensic techniques
- Technology applications revealing new information

**3. MANDATORY COMPETITIVE LANDSCAPE VERIFICATION**
Check against all major networks: Netflix, Amazon Prime, Hulu, HBO Max, Investigation Discovery, A&E, Dateline NBC, 48 Hours, 20/20, etc.

**4. DAILY OUTPUT REQUIREMENTS - 10 REAL CASES**

**Distribution:**
- 3-4 TIER 1 Cases (Immediate Development Potential)
- 4-5 TIER 2 Cases (Short-term Monitoring/Development)  
- 2-3 TIER 3 Cases (Long-term Archive/Future Consideration)

**STRICT EXCLUSIONS:**
- NO Innocence Project cases or wrongful conviction stories
- NO ongoing investigations or active trials
- ONLY adjudicated (legally resolved) cases with new developments
- NO hypothetical or example cases

## EXECUTION INSTRUCTIONS

**YOU MUST:**
1. Analyze the search results provided above
2. Research additional current true crime developments
3. Provide exactly 10 REAL cases with full details
4. Include competitive verification for each case
5. Focus on cases with documentable new developments

**DO NOT:**
- Explain limitations about accessing real-time information
- Provide hypothetical or example cases
- Suggest alternative approaches
- Give disclaimers about the exercise

## DAILY EMAIL FORMAT

**Subject Line:** "Daily Content Discovery Briefing - {current_date} - 10 Premium Development Opportunities"

**Individual Case Analysis (10 REAL Cases):**

**Case #[X] - [Tier Level] - [Case Type] - [Story Title]**
- **Case Type:** Adjudicated w/New Development | Cold Case w/Fresh Evidence  
- **Logline:** Compelling one-sentence hook
- **Key Details:** Timeline, location, principals involved
- **ADJUDICATION STATUS:** Confirm case is legally resolved/closed
- **NEW DEVELOPMENT SUMMARY:** What makes this story fresh/different from prior coverage
- **Production Assets:** Available footage, documents, interview subjects
- **COMPETITIVE VERIFICATION:** Check results across all platforms
- **Development Recommendation:** GO/NO-GO with rationale
- **Next Steps:** Specific actions required for advancement

**DELIVER 10 REAL CASES NOW - NO EXPLANATIONS, NO LIMITATIONS, ONLY REAL CURRENT TRUE CRIME DEVELOPMENTS.**
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
