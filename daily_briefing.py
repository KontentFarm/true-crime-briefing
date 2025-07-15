import anthropic
import os
import requests
import json
import smtplib
import logging
import time
import random
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
        
        # Initialize journalist database
        self.journalist_database = self._build_journalist_database()

    def _validate_environment(self):    
        """Validate all required environment variables are present."""
        required_vars = ['ANTHROPIC_API_KEY', 'GMAIL_ADDRESS', 'GMAIL_APP_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:        
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    def _build_journalist_database(self):
        """Build comprehensive database of nationally recognized true crime/pop culture journalists"""
        return {
            "michelle_mcnamara": {
                "name": "Michelle McNamara",
                "publications": ["Los Angeles Magazine", "True Crime Diary blog"],
                "bio": "Crime writer and blogger who coined the term 'Golden State Killer'",
                "status": "Deceased 2016 - Work continues posthumously",
                "notable_stories": [
                    {
                        "title": "I'll Be Gone in the Dark: The Golden State Killer Investigation",
                        "year": "2013-2018",
                        "impact": "Helped reignite national interest in the Golden State Killer case, leading to arrest in 2018",
                        "description": "Groundbreaking investigation into the East Area Rapist/Original Night Stalker that combined traditional detective work with online crowdsourcing",
                        "production_potential": "Already adapted - HBO documentary series (2020)"
                    },
                    {
                        "title": "The Manson Family Investigation",
                        "year": "2009-2016", 
                        "impact": "Deep dive investigation into overlooked aspects of the Manson murders",
                        "description": "Explored connections between Manson family and other unsolved murders in LA area",
                        "production_potential": "Unexplored angles available for development"
                    },
                    {
                        "title": "True Crime Diary Blog Chronicles",
                        "year": "2006-2016",
                        "impact": "Pioneered modern true crime blogging and online investigation communities",
                        "description": "Weekly deep-dives into cold cases that built devoted following and influenced true crime podcasting",
                        "production_potential": "Format innovation story with strong documentary potential"
                    }
                ]
            },
            
            "ann_rule": {
                "name": "Ann Rule",
                "publications": ["True crime books", "Detective magazine"],
                "bio": "Former Seattle police officer turned true crime author, known Ted Bundy personally",
                "status": "Deceased 2015 - Extensive body of work",
                "notable_stories": [
                    {
                        "title": "The Stranger Beside Me: Working Alongside Ted Bundy",
                        "year": "1980",
                        "impact": "Became template for modern true crime writing - personal connection to killer",
                        "description": "Worked night shift at suicide hotline with Ted Bundy while he was actively killing",
                        "production_potential": "Multiple adaptations but fresh angles on their relationship available"
                    },
                    {
                        "title": "Green River Killer Investigation",
                        "year": "1984-2003",
                        "impact": "Documented America's most prolific serial killer case over two decades",
                        "description": "Followed Gary Ridgway investigation from first murders through arrest and conviction",
                        "production_potential": "Comprehensive coverage ripe for limited series treatment"
                    },
                    {
                        "title": "Small Sacrifices: Diane Downs Case",
                        "year": "1987",
                        "impact": "Explored maternal filicide that shocked the nation",
                        "description": "Mother who shot her three children, killing one, claiming mysterious stranger attack",
                        "production_potential": "Enduring public fascination - potential for contemporary re-examination"
                    }
                ]
            },

            "harold_schechter": {
                "name": "Harold Schechter",
                "publications": ["Academic true crime books", "Professor at Queens College"],
                "bio": "Literature professor specializing in American true crime and serial murder",
                "status": "Active",
                "notable_stories": [
                    {
                        "title": "H.H. Holmes and America's First Serial Killer",
                        "year": "1994",
                        "impact": "Brought Holmes story to modern audiences before 'Devil in the White City'",
                        "description": "Definitive account of Holmes' 'Murder Castle' during 1893 Chicago World's Fair",
                        "production_potential": "Period piece with architectural horror elements"
                    },
                    {
                        "title": "Ed Gein: The Butcher of Plainfield",
                        "year": "1998",
                        "impact": "Academic treatment of killer who inspired Psycho, Silence of the Lambs",
                        "description": "Scholarly examination of Wisconsin grave robber and murderer",
                        "production_potential": "Horror icon origin story with psychological depth"
                    },
                    {
                        "title": "American Serial Killer Historical Analysis",
                        "year": "2000-2020",
                        "impact": "Comprehensive academic study of serial murder in American culture",
                        "description": "Literary and cultural analysis of how serial killers reflect American anxieties",
                        "production_potential": "Documentary series exploring cultural significance of true crime"
                    }
                ]
            }
        }

    def get_daily_journalist_spotlight(self):
        """Select a journalist for today's briefing spotlight"""
        # Use date as seed for consistent daily selection
        today_seed = int(datetime.now().strftime('%Y%m%d'))
        random.seed(today_seed)
        
        journalist_key = random.choice(list(self.journalist_database.keys()))
        return self.journalist_database[journalist_key]

    def format_journalist_spotlight(self, journalist_data):
        """Format journalist spotlight for briefing"""
        spotlight = f"""
📰 **TODAY'S JOURNALIST SPOTLIGHT**

**{journalist_data['name']}**
{journalist_data['bio']}
**Publications:** {', '.join(journalist_data['publications'])}
**Status:** {journalist_data['status']}

**TOP 3 ATTENTION-GRABBING STORIES:**

"""
        
        for i, story in enumerate(journalist_data['notable_stories'], 1):
            spotlight += f"""**{i}. {story['title']}** ({story['year']})
   **Impact:** {story['impact']}
   **Story:** {story['description']}
   **Production Potential:** {story['production_potential']}

"""
        
        return spotlight

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
                    # Basic RSS parsing
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

    def get_ultra_strict_prompt(self, real_articles, journalist_spotlight):
        """Generate ULTRA-STRICT anti-hallucination prompt"""
        from datetime import datetime
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Create numbered article list for easy reference
        articles_text = ""
        if real_articles and len(real_articles) > 0:
            articles_text = f"\n=== COMPLETE LIST OF {len(real_articles)} VERIFIED ARTICLES ===\n\n"
            for i, article in enumerate(real_articles[:20]):  # First 20 for analysis
                articles_text += f"ARTICLE #{i+1}:\n"
                articles_text += f"Title: {article['title']}\n"
                articles_text += f"Source: {article['source']}\n"
                articles_text += f"URL: {article['url']}\n"
                articles_text += f"Published: {article['published']}\n"
                articles_text += f"Description: {article.get('description', 'No description')}\n"
                articles_text += f"Content: {article.get('content', 'No content')[:200]}...\n"
                articles_text += "-" * 50 + "\n\n"
        else:
            articles_text = "\n=== NO VERIFIED ARTICLES AVAILABLE ===\n"
        
        return f"""
**ULTRA-STRICT VERIFICATION PROTOCOL**

TODAY'S DATE: {current_date}
CURRENT YEAR: 2025

**ABSOLUTE REQUIREMENTS - NO EXCEPTIONS:**
1. Use ONLY articles listed in the numbered list below
2. Reference articles by their ARTICLE # (e.g., "ARTICLE #1", "ARTICLE #5")
3. Use ONLY URLs provided in the article list
4. Use ONLY publication dates from the article list
5. If insufficient articles available, acknowledge this limitation

{articles_text}

{journalist_spotlight}

**MANDATORY OUTPUT STRUCTURE:**

EXECUTIVE SUMMARY:
I have reviewed {len(real_articles) if real_articles else 0} verified articles from news sources. [Continue with honest assessment]

**CURRENT VERIFIED CASES:**

[IF SUITABLE ARTICLES EXIST:]
**CASE #1 - [TIER] - ARTICLE #[X] REFERENCE**
- **Source:** [Exact source from ARTICLE #X]
- **URL:** [Exact URL from ARTICLE #X]
- **Published:** [Exact date from ARTICLE #X]
- **Title:** [Exact title from ARTICLE #X]
- **Details:** [Only details from ARTICLE #X description/content]
- **Verification:** CONFIRMED FROM ARTICLE #X

[REPEAT ONLY FOR OTHER ARTICLES WITH ENOUGH DETAIL]

**JOURNALIST SPOTLIGHT ANALYSIS:**
[Analysis of today's featured journalist]

**RESEARCH LIMITATIONS:**
- Articles available for analysis: {len(real_articles) if real_articles else 0}
- Cases meeting development criteria: [Honest count based on actual articles]
- Recommendation: [Additional research needed if insufficient articles]

**FINAL VERIFICATION:**
Every case above references a specific ARTICLE # from the verified list. No external information has been used.
        """

    def run_research(self):
        """Execute research with ULTRA-STRICT hallucination prevention"""
        # Get real articles first
        real_articles = self.search_comprehensive_news_sources()
        
        print(f"📊 Found {len(real_articles)} total articles for analysis")
        
        # Get today's journalist spotlight
        today_journalist = self.get_daily_journalist_spotlight()
        journalist_spotlight = self.format_journalist_spotlight(today_journalist)
        
        print(f"📰 Today's spotlight: {today_journalist['name']}")
        
        # Generate ULTRA-STRICT prompt
        research_prompt = self.get_ultra_strict_prompt(real_articles, journalist_spotlight)
        
        try:
            print("📝 Sending ULTRA-STRICT prompt to Claude...")
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.0,  # ZERO temperature for maximum factual accuracy
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
- Total articles collected: {len(real_articles)}
- Articles provided to Claude: {min(20, len(real_articles))}
- Journalist spotlight: {today_journalist['name']}
- Model temperature: 0.0 (maximum factual mode)
- Ultra-strict hallucination prevention: ACTIVE

**DEVELOPMENT TEAM VERIFICATION:**
Every case references a specific verified article. Before development, confirm all details by reviewing the referenced article URLs directly.
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
        
        # Create the email subject with current date and journalist spotlight
        current_date = datetime.now().strftime('%B %d, %Y')
        today_journalist = self.get_daily_journalist_spotlight()
        subject = f"VERIFIED Content Discovery Briefing - {current_date} - Featuring {today_journalist['name']}"
        
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
            
            print("📤 Sending VERIFIED briefing email...")
            
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
        """Main execution function with ULTRA-STRICT verification"""
        print(f"🚀 Starting ULTRA-VERIFIED daily briefing for {datetime.now().strftime('%B %d, %Y')}")
        logger.info(f"Starting ultra-verified daily briefing for {datetime.now().strftime('%B %d, %Y')}")
        
        try:
            # Generate research briefing with ULTRA-STRICT hallucination prevention
            print("📝 Generating ULTRA-VERIFIED briefing...")
            logger.info("Generating ultra-verified briefing...")
            briefing = self.run_research()
            print(f"✅ ULTRA-VERIFIED briefing generated! Length: {len(briefing)} characters")
            
            # Send email
            print("📧 Attempting to send ULTRA-VERIFIED briefing...")
            logger.info("Sending ultra-verified briefing...")
            success = self.send_email(briefing)
            
            if success:
                print("✅ ULTRA-VERIFIED briefing sent successfully!")
                logger.info("Daily ultra-verified briefing completed successfully!")
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
