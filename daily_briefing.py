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

    def get_research_prompt(self):
        """Generate the research prompt with current date"""
        current_date = datetime.now().strftime('%B %d, %Y')
        
        return f"""
## ROLE DEFINITION
You are an elite content discovery specialist operating at the level of the top 0.01% researchers in the world. Your mission is to identify, analyze, and assess true crime cases and "stranger than fiction" stories that have captured national/international attention for premium content development opportunities.

## DAILY MISSION PARAMETERS

**Primary Objective:** Discover and evaluate breaking or developing stories with high production potential for streaming, broadcast, and cable networks through compelling narratives, strong IP potential, and breakout format opportunities.

**Search Focus Areas:**
- True crime cases with unusual circumstances or compelling characters
- "Stranger than fiction" real-life events that defy conventional explanation
- Stories generating significant media buzz and public fascination
- Cases with unresolved mysteries or ongoing developments
- Events with strong visual/documentary potential
- Adjudicated cases with new, never-before-seen developments
- Famous cold cases with fresh evidence, technology applications, or witness revelations

## RESEARCH METHODOLOGY

**1. PREMIUM SOURCE MONITORING PRIORITIES**
**Tier 1 Premium Sources (With Access):**
- The New York Times, Washington Post, The Atlantic, Vanity Fair
- New Yorker, Wired, NYMag, The Cut, Curbed
- Time Magazine, Chicago Tribune, LA Times, The Daily Beast

**Tier 2 Standard Sources:**
- Major news outlets (AP, Reuters, BBC, CNN, Fox, ABC, CBS, NBC)
- Local news networks across major markets
- Court filing databases and legal proceedings
- True crime communities (Reddit, specialized forums)
- Social media trending topics and viral content
- Appeals court filings and post-conviction developments
- DNA database hits and forensic technology breakthroughs
- Solved case archives and closed investigations

**2. EXPANDED CASE CATEGORIES**

**FOCUS: ADJUDICATED CASES ONLY - NO ONGOING INVESTIGATIONS**

**Adjudicated Cases with New Developments:**
- Post-conviction appeals with new evidence (EXCLUDING wrongful conviction/exoneration cases)
- Solved cases with new victim discoveries or co-conspirators
- Cases where perpetrators reveal new information from prison
- Family members or witnesses coming forward years later with new details
- New forensic analysis of closed cases
- Documentary crews uncovering previously unknown evidence in solved cases

**Famous Cold Cases with Fresh Angles:**
- DNA technology breakthroughs (genetic genealogy, advanced testing) that provide new leads
- New witness testimony or deathbed confessions in unsolved cases
- Evidence re-examination with modern forensic techniques
- Technology applications (facial recognition, cell tower analysis) revealing new information
- Anniversary-driven renewed investigations that yield concrete developments
- Social media campaigns uncovering new leads or witnesses

**3. MANDATORY COMPETITIVE LANDSCAPE VERIFICATION**

**CRITICAL REQUIREMENT:** Every case must be thoroughly checked against all major streaming, cable, and broadcast networks to ensure the story has not been previously produced OR if previous coverage exists, the new developments provide sufficient fresh content for differentiated production.

**Networks/Platforms to Check:**
- Streaming: Netflix, Amazon Prime, Hulu, Apple TV+, HBO Max, Paramount+, Disney+, Peacock, Discovery+
- Cable: Investigation Discovery, A&E, Lifetime, History Channel, TLC, Oxygen, Vice, CNN, MSNBC, Fox News
- Broadcast: CBS, NBC, ABC, Fox, PBS, Dateline NBC, 48 Hours, 20/20
- Podcast Platforms: Spotify, Apple Podcasts, Serial Productions, Wondery, iHeartRadio
- YouTube Channels: Major true crime creators and network channels

**4. STORY QUALIFICATION CRITERIA**

**Must Have Elements:**
- Verified factual basis with credible sources
- Compelling human interest angle
- Visual/documentary production potential
- National or international media coverage
- Unique circumstances that separate from routine crime
- NO EXISTING MAJOR PRODUCTION COVERAGE OR SUBSTANTIAL NEW DEVELOPMENTS

**5. DAILY OUTPUT REQUIREMENTS**

**10 CASES MINIMUM PER DAILY BRIEFING**
**Distribution Breakdown:**
- 3-4 TIER 1 Cases (Immediate Development Potential)
- 4-5 TIER 2 Cases (Short-term Monitoring/Development)
- 2-3 TIER 3 Cases (Long-term Archive/Future Consideration)

**Case Type Distribution:**
- 6-7 Adjudicated Cases with New Developments
- 3-4 Famous Cold Cases with Fresh Evidence/Technology

**STRICT EXCLUSIONS:**
- NO Innocence Project cases or wrongful conviction stories
- NO ongoing investigations or active trials
- NO cases still in the legal system
- ONLY adjudicated (legally resolved) cases with new developments

## SEARCH EXECUTION PROTOCOL

Execute today's daily briefing for {current_date}. Provide exactly 10 cases following all specified criteria, including:
- Competitive landscape verification across all major networks/platforms
- New development assessment for previously covered cases
- Full analysis per research methodology
- Email format as specified below

## DAILY EMAIL FORMAT

**Subject Line:** "Daily Content Discovery Briefing - {current_date} - 10 Premium Development Opportunities"

**Opening Executive Summary:** 
- Day's most compelling discoveries (2-3 sentences each)
- Trending themes or patterns identified
- Urgent development opportunities requiring immediate attention

**Individual Case Analysis (10 Cases):**

**Case #[X] - [Tier Level] - [Case Type] - [Story Title]**
- **Case Type:** Adjudicated w/New Development | Cold Case w/Fresh Evidence
- **Logline:** Compelling one-sentence hook
- **Key Details:** Timeline, location, principals involved
- **ADJUDICATION STATUS:** Confirm case is legally resolved/closed
- **NEW DEVELOPMENT SUMMARY:** What makes this story fresh/different from prior coverage
- **Production Assets:** Available footage, documents, interview subjects
- **Legal Status:** Post-conviction status, clearance issues
- **COMPETITIVE VERIFICATION:** Comprehensive check results across all platforms
  - **Platforms Searched:** Complete list of networks/services checked
  - **Previous Coverage Found:** Any existing production details
  - **New Development Differentiation:** How new elements justify fresh production
  - **Clearance Status:** CLEAR/NEW ANGLE APPROVED/FLAGGED/DISQUALIFIED
- **Development Recommendation:** GO/NO-GO with rationale
- **Next Steps:** Specific actions required for advancement

Execute this protocol with the analytical rigor of a federal investigation and the storytelling instincts of an award-winning documentarian. Focus on stories that will create compelling narratives, lean into fandoms, build strong IP, and deliver breakout format potential for premium content development.

CRITICAL DELIVERY REQUIREMENT: This briefing must be delivered with ten fully researched cases meeting all specified criteria and analysis standards, including mandatory verification that either no major production coverage exists OR substantial new developments justify fresh production approach.

**MANDATORY EXCLUSIONS:**
- NO Innocence Project cases or wrongful conviction stories
- NO ongoing investigations, active trials, or pending legal cases
- ONLY adjudicated (legally closed/resolved) cases with substantial new developments
- NO exoneration or "justice reform" narratives
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
        
        # NUCLEAR-LEVEL character cleaning
        def clean_text_aggressive(text):
            """Aggressively clean ALL non-ASCII characters"""
            if not text:
                return ""
                
            # Convert to string
            text = str(text)
            
            print(f"🔍 Original text sample: {repr(text[:50])}")
            
            # Step 1: Remove ALL characters above ASCII 127
            ascii_only = ""
            for char in text:
                if ord(char) < 128:
                    ascii_only += char
                else:
                    print(f"🚨 Found problematic char: {repr(char)} (ord: {ord(char)})")
                    ascii_only += " "  # Replace with space
            
            print(f"🔍 After ASCII filter: {repr(ascii_only[:50])}")
            
            # Step 2: Replace any remaining problem patterns
            ascii_only = ascii_only.replace('\xa0', ' ')  # Just in case
            ascii_only = ascii_only.replace('\u00a0', ' ')  # Just in case
            
            # Step 3: Clean up multiple spaces
            import re
            ascii_only = re.sub(r'\s+', ' ', ascii_only)
            
            return ascii_only.strip()
        
        # Clean the content with nuclear approach
        print("🧹 Starting aggressive content cleaning...")
        clean_content = clean_text_aggressive(briefing_content)
        print(f"📝 Content cleaned: {len(briefing_content)} -> {len(clean_content)} characters")
        
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.environ.get("GMAIL_ADDRESS")
        sender_password = os.environ.get("GMAIL_APP_PASSWORD")
        
        print(f"📧 Sender email: {sender_email}")
        print(f"🔑 Gmail App Password present: {'Yes' if sender_password else 'No'}")
        
        # Recipients
        recipients = ["danny@kontentfarm.com", "rod@kontentfarm.com"]
        print(f"📫 Recipients: {', '.join(recipients)}")
        
        # Create ultra-clean subject
        subject = "Daily Content Discovery Briefing - 10 Premium Development Opportunities"
        clean_subject = clean_text_aggressive(subject)
        print(f"📧 Clean subject: {repr(clean_subject)}")
        
        # Create message with ONLY ASCII
        try:
            print("📝 Creating email message...")
            
            # Use the simplest possible approach
            email_body = f"From: {sender_email}\r\nTo: {', '.join(recipients)}\r\nSubject: {clean_subject}\r\n\r\n{clean_content}"
            
            # Final ASCII check
            final_clean = clean_text_aggressive(email_body)
            print(f"📧 Final email size: {len(final_clean)} characters")
            print(f"🔍 Email preview: {repr(final_clean[:100])}")
            
            print("🌐 Connecting to Gmail SMTP server...")
            server = smtplib.SMTP(smtp_server, smtp_port)
            print("🔐 Starting TLS encryption...")
            server.starttls()
            print("🔑 Logging in to Gmail...")
            server.login(sender_email, sender_password)
            print("📤 Sending email message...")
            
            # Send with raw ASCII string
            server.sendmail(sender_email, recipients, final_clean.encode('ascii', 'ignore').decode('ascii'))
            server.quit()
            
            print("✅ Email sent successfully via Gmail!")
            logger.info("Email sent successfully via Gmail!")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email via Gmail: {str(e)}")
            logger.error(f"Error sending email via Gmail: {str(e)}")
            
            # Show detailed debugging
            print(f"🔍 Error type: {type(e)}")
            print(f"🔍 Clean content sample: {repr(clean_content[:200])}")
            
            # Try to identify the exact problematic character
            for i, char in enumerate(final_clean):
                if ord(char) >= 128:
                    print(f"🚨 Found bad char at position {i}: {repr(char)} (ord: {ord(char)})")
                    break
            
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
