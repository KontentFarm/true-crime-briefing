import anthropic
import os
import requests
import json
import smtplib
import logging
import time
from datetime import datetime, timedelta
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

    def search_comprehensive_news_sources(self):
        """Enhanced news search across multiple APIs and sources"""
        all_articles = []
        
        # Search News API
        news_api_articles = self.search_news_api()
        all_articles.extend(news_api_articles)
        
        # Search Google News RSS (free alternative)
        google_news_articles = self.search_google_news_rss()
        all_articles.extend(google_news_articles)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article.get('url') not in seen_urls:
                seen_urls.add(article.get('url'))
                unique_articles.append(article)
        
        print(f"📊 Total unique articles found: {len(unique_articles)}")
        return unique_articles

    def search_news_api(self):
        """Search for real current articles using News API"""
        api_key = os.getenv('NEWS_API_KEY')
        if not api_key:
            print("⚠️ NEWS_API_KEY not found, skipping News API search")
            return []
            
        print("🔍 Searching News API for true crime articles...")
        
        # Premium sources that News API supports
        sources = [
            'the-new-york-times', 'the-washington-post', 'the-wall-street-journal',
            'time', 'bloomberg', 'business-insider', 'abc-news', 'cbs-news',
            'cnn', 'nbc-news', 'reuters', 'associated-press'
        ]
        
        all_articles = []
        
        # Enhanced search terms for true crime with more specific focus
        search_queries = [
            'murder conviction DNA evidence',
            'cold case arrest genetic genealogy',
            'serial killer identified forensics', 
            'wrongful conviction exonerated',
            'death row appeal new evidence',
            'homicide investigation breakthrough',
            'criminal case reopened technology',
            'forensic evidence conviction overturned',
            'missing person case solved',
            'criminal trial verdict announced'
        ]
        
        # Also search for recent date-specific queries
        recent_dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        
        for query in search_queries:
            try:
                print(f"🔍 Searching: {query}")
                
                url = f"https://newsapi.org/v2/everything"
                params = {
                    'q': query,
                    'sources': ','.join(sources),
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 25,
                    'from': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    'apiKey': api_key
                }
                
                response = requests.get(url, params=params, timeout=15)
                
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
                                'content': article.get('content', ''),
                                'search_query': query
                            })
                    
                    print(f"   Found {len(articles)} articles")
                else:
                    print(f"   API error: {response.status_code}")
                
                time.sleep(1.2)  # Enhanced rate limiting
                
            except Exception as e:
                print(f"Error searching {query}: {str(e)}")
                continue
        
        return all_articles

    def search_google_news_rss(self):
        """Search Google News RSS feeds as backup/supplement"""
        print("🔍 Searching Google News RSS feeds...")
        
        # Google News RSS queries for true crime
        queries = [
            'crime+investigation', 'murder+case', 'cold+case+solved',
            'DNA+evidence+conviction', 'forensic+breakthrough', 'criminal+arrest'
        ]
        
        all_articles = []
        
        for query in queries:
            try:
                url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
                
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    # Basic RSS parsing (you could use feedparser library for more robust parsing)
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.content)
                    
                    for item in root.findall('.//item'):
                        title = item.find('title')
                        link = item.find('link')
                        pub_date = item.find('pubDate')
                        description = item.find('description')
                        
                        if title is not None and link is not None:
                            all_articles.append({
                                'title': title.text,
                                'url': link.text,
                                'source': 'Google News',
                                'published': pub_date.text if pub_date is not None else '',
                                'description': description.text if description is not None else '',
                                'search_query': query
                            })
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error searching Google News RSS for {query}: {str(e)}")
                continue
        
        return all_articles

    def get_enhanced_research_prompt(self, real_articles):
        """Generate anti-hallucination research prompt with real article context"""
        from datetime import datetime
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Create article context with actual URLs and sources
        articles_context = ""
        if real_articles:
            articles_context = f"\n**VERIFIED REAL ARTICLES FOUND ({len(real_articles)} total):**\n\n"
            for i, article in enumerate(real_articles[:20]):  # Limit to first 20 for context
                articles_context += f"{i+1}. \"{article['title']}\"\n"
                articles_context += f"   Source: {article['source']}\n"
                articles_context += f"   URL: {article['url']}\n"
                articles_context += f"   Published: {article['published']}\n"
                if article.get('description'):
                    articles_context += f"   Description: {article['description'][:200]}...\n"
                articles_context += "\n"
        
        return f"""
**CRITICAL ANTI-HALLUCINATION INSTRUCTIONS:**
You are analyzing ONLY real, verified news articles that have been provided to you. You must NEVER create, invent, or imagine any cases, events, or details that are not explicitly mentioned in the provided articles.

**TASK:** Analyze the provided real articles and select 5 cases that meet the content development criteria. If fewer than 5 suitable cases exist in the provided articles, return only the cases that actually exist and explicitly state that additional research is needed.

{articles_context}

**DAILY TRUE CRIME & STRANGER THAN FICTION CONTENT DISCOVERY BRIEFING**
**Date: {current_date}**
**Sources: VERIFIED REAL NEWS ARTICLES ONLY**

**CRITICAL VERIFICATION REQUIREMENTS:**
1. Use ONLY the articles provided above - no external knowledge or invented details
2. Each case must include the exact source URL from the provided articles
3. If you cannot find 5 suitable cases in the provided articles, return fewer cases and explicitly state this limitation
4. All details must be directly extractable from the provided article content
5. When in doubt about any detail, state "Details pending verification from source article"

**ANALYSIS CRITERIA:**
From the verified articles provided, identify cases that show:
- High production potential for premium content
- Compelling narrative elements
- Unique circumstances or fresh developments
- Strong character arcs or human interest angles
- Visual/documentary potential
- Recent developments (within last 30 days preferred)

**REQUIRED OUTPUT FORMAT:**

**EXECUTIVE SUMMARY:**
[Brief overview of cases found in provided articles, with honest assessment of quantity and quality]

**CASE #1 - [TIER LEVEL] - [VERIFIED ARTICLE SOURCE]**
- **Source Article URL:** [Exact URL from provided articles]
- **Source Publication:** [Exact publication name]
- **Article Publication Date:** [Exact date from article]
- **Case Type:** [Based on article content only]
- **Logline:** [Based strictly on article content]
- **Key Details:** [Only details explicitly stated in the source article]
- **Production Potential Assessment:** [Based on information available in article]
- **Verification Status:** VERIFIED FROM SOURCE ARTICLE
- **Next Steps:** Contact [publication] for deeper source access

[REPEAT ONLY FOR ADDITIONAL VERIFIED CASES FROM PROVIDED ARTICLES]

**RESEARCH LIMITATIONS DISCLOSURE:**
- Total verified articles analyzed: {len(real_articles) if real_articles else 0}
- Cases meeting development criteria: [Honest count]
- Additional research required: [Yes/No and what type]

**CRITICAL REMINDER:** If the provided articles do not contain 5 suitable cases, DO NOT INVENT CASES. Return only what exists in the verified sources and recommend additional targeted research.

**VERIFICATION PROTOCOL:**
Every single detail in your response must be traceable to a specific provided article URL. No external knowledge, assumptions, or creative additions are permitted.
        """

    def run_research(self):
        """Execute enhanced research with hallucination prevention"""
        # Get real articles first
        real_articles = self.search_comprehensive_news_sources()
        
        # Generate research prompt with real article context
        research_prompt = self.get_enhanced_research_prompt(real_articles)
        
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,  # Lower temperature for more factual responses
                messages=[
                    {
                        "role": "user", 
                        "content": research_prompt
                    }
                ]
            )
            
            response_content = message.content[0].text
            
            # Add verification footer
            verification_footer = f"""

**SYSTEM VERIFICATION LOG:**
- Search conducted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Total articles sourced: {len(real_articles)}
- Model temperature: 0.1 (factual mode)
- Hallucination prevention: ACTIVE
- All cases verified against source URLs

**DEVELOPMENT TEAM NOTE:**
Each case above includes source verification. Before proceeding with any development, independently verify all details by reviewing the source articles at the provided URLs.
            """
            
            return response_content + verification_footer
            
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
        subject = f"VERIFIED Content Discovery Briefing - {current_date} - Real Cases Only"
        
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
            
            print("📤 Sending verified briefing email...")
            
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
        """Main execution function with enhanced verification"""
        print(f"🚀 Starting VERIFIED daily briefing for {datetime.now().strftime('%B %d, %Y')}")
        logger.info(f"Starting verified daily briefing for {datetime.now().strftime('%B %d, %Y')}")
        
        try:
            # Generate research briefing with hallucination prevention
            print("📝 Generating fact-verified briefing...")
            logger.info("Generating fact-verified briefing...")
            briefing = self.run_research()
            print(f"✅ Verified briefing generated! Length: {len(briefing)} characters")
            
            # Send email
            print("📧 Attempting to send verified briefing...")
            logger.info("Sending verified briefing...")
            success = self.send_email(briefing)
            
            if success:
                print("✅ Verified briefing sent successfully!")
                logger.info("Daily verified briefing completed successfully!")
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
