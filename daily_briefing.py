import anthropic
import smtplib
import os
import requests
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class TrueCrimeBriefing:
    def __init__(self):
        self.anthropic_client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        
    def get_research_prompt(self):
        """Return the comprehensive True Crime Discovery Agent prompt"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        return f"""
# True Crime & Stranger Than Fiction Content Discovery Agent

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

**1. SOURCE MONITORING PRIORITIES**
- Major news outlets (AP, Reuters, BBC, CNN, Fox, ABC, CBS, NBC)
- Local news networks across major markets
- Police department press releases and public records
- Court filing databases and legal proceedings
- True crime communities (Reddit, specialized forums)
- Social media trending topics and viral content
- Appeals court filings and post-conviction developments
- Cold case unit announcements and reopened investigations
- DNA database hits and forensic technology breakthroughs
- Innocence Project developments and exonerations

**2. EXPANDED CASE CATEGORIES**

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
- 4-5 Active/Breaking Cases
- 3-4 Adjudicated Cases with New Developments
- 2-3 Famous Cold Cases with Fresh Evidence/Technology

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
- **Case Type:** Active/Breaking | Adjudicated w/New Development | Cold Case w/Fresh Evidence
- **Logline:** Compelling one-sentence hook
- **Key Details:** Timeline, location, principals involved
- **NEW DEVELOPMENT SUMMARY:** What makes this story fresh/different from prior coverage
- **Production Assets:** Available footage, documents, interview subjects
- **Legal Status:** Current investigations, proceedings, clearance issues
- **COMPETITIVE VERIFICATION:** Comprehensive check results across all platforms
  - **Platforms Searched:** Complete list of networks/services checked
  - **Previous Coverage Found:** Any existing production details
  - **New Development Differentiation:** How new elements justify fresh production
  - **Clearance Status:** CLEAR/NEW ANGLE APPROVED/FLAGGED/DISQUALIFIED
- **Development Recommendation:** GO/NO-GO with rationale
- **Next Steps:** Specific actions required for advancement

Execute this protocol with the analytical rigor of a federal investigation and the storytelling instincts of an award-winning documentarian. Focus on stories that will create compelling narratives, lean into fandoms, build strong IP, and deliver breakout format potential for premium content development.

CRITICAL DELIVERY REQUIREMENT: This briefing must be delivered with ten fully researched cases meeting all specified criteria and analysis standards, including mandatory verification that either no major production coverage exists OR substantial new developments justify fresh production approach.
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
            return f"Error generating briefing: {str(e)}"
    
    def send_email(self, briefing_content):
        """Send the briefing via email"""
        
        # Email configuration
        smtp_server = "smtp.sendgrid.net"
        smtp_port = 587
        sender_email = os.environ.get("SENDER_EMAIL")
        sender_password = os.environ.get("SENDGRID_API_KEY")
        
        # Recipients
        recipients = ["danny@kontentfarm.com", "rod@kontentfarm.com"]
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"Daily Content Discovery Briefing - {datetime.now().strftime('%B %d, %Y')} - 10 Premium Development Opportunities"
        
        # Add body
        msg.attach(MIMEText(briefing_content, 'plain'))
        
        try:
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            print("Email sent successfully!")
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def run_daily_briefing(self):
        """Main execution function"""
        print(f"Starting daily briefing for {datetime.now().strftime('%B %d, %Y')}")
        
        # Generate research briefing
        print("Generating research briefing...")
        briefing = self.run_research()
        
        # Send email
        print("Sending email...")
        success = self.send_email(briefing)
        
        if success:
            print("Daily briefing completed successfully!")
        else:
            print("Daily briefing generated but email failed to send.")
            print("Briefing content:")
            print(briefing)

if __name__ == "__main__":
    briefing_system = TrueCrimeBriefing()
    briefing_system.run_daily_briefing()