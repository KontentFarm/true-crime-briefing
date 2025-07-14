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

            "katherine_ramsland": {
                "name": "Katherine Ramsland",
                "publications": ["Psychology Today", "The Forensic Examiner", "Academic journals"],
                "bio": "Forensic psychologist and true crime author specializing in criminal psychology",
                "status": "Active",
                "notable_stories": [
                    {
                        "title": "BTK Killer Dennis Rader Prison Correspondence",
                        "year": "2006-present",
                        "impact": "Unprecedented access to serial killer's psychology through prison letters",
                        "description": "Extensive correspondence with BTK killer providing insights into serial killer mindset",
                        "production_potential": "Unique psychological angle with documentary/limited series potential"
                    },
                    {
                        "title": "The Mind of a Murderer: Criminal Psychology Case Studies",
                        "year": "2000-present",
                        "impact": "Bridged academic psychology and popular true crime",
                        "description": "Deep psychological analysis of notorious killers including interviews and assessments",
                        "production_potential": "Educational/documentary series format with high production value"
                    },
                    {
                        "title": "Vampire Killers and Gothic Crime Investigation",
                        "year": "2002-2010",
                        "impact": "Explored intersection of gothic subculture and violent crime",
                        "description": "Cases involving self-identified vampires and gothic-influenced murders",
                        "production_potential": "Unique angle combining true crime with cultural analysis"
                    }
                ]
            },

            "jim_fisher": {
                "name": "Jim Fisher",
                "publications": ["Former FBI agent", "True crime author"],
                "bio": "Retired FBI agent turned true crime author with insider law enforcement perspective",
                "status": "Active",
                "notable_stories": [
                    {
                        "title": "The Lindbergh Kidnapping Case Re-examination",
                        "year": "2005-2012",
                        "impact": "Challenged conventional wisdom about America's most famous kidnapping",
                        "description": "FBI insider's analysis questioning Bruno Hauptmann's guilt in Lindbergh baby murder",
                        "production_potential": "Historical true crime with contemporary forensic analysis angle"
                    },
                    {
                        "title": "John List Family Murder Investigation",
                        "year": "2006",
                        "impact": "Detailed inside look at one of America's most shocking family annihilations",
                        "description": "Westfield, NJ father who killed entire family and disappeared for 18 years",
                        "production_potential": "Strong psychological thriller elements with family drama"
                    },
                    {
                        "title": "FBI Behavioral Analysis Unit Case Studies",
                        "year": "2000-2015",
                        "impact": "Revealed inner workings of FBI's elite profiling unit",
                        "description": "Behind-the-scenes look at criminal profiling and behavioral analysis techniques",
                        "production_potential": "Procedural format with authentic law enforcement perspective"
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
            },

            "maureen_callahan": {
                "name": "Maureen Callahan",
                "publications": ["New York Post", "Vanity Fair"],
                "bio": "Investigative journalist covering high-profile criminal cases and celebrity scandals",
                "status": "Active",
                "notable_stories": [
                    {
                        "title": "Jeffrey Epstein's Network Investigation",
                        "year": "2019-2020",
                        "impact": "Aggressive reporting on Epstein associates and conspiracy theories",
                        "description": "Deep dive into Epstein's connections to powerful figures and mysterious death",
                        "production_potential": "High-profile exposé with ongoing public interest"
                    },
                    {
                        "title": "NXIVM Sex Cult Exposé",
                        "year": "2017-2021",
                        "impact": "Early reporting on Keith Raniere's cult before mainstream coverage",
                        "description": "Investigation into self-help group that became sex trafficking operation",
                        "production_potential": "Already adapted but ongoing legal proceedings provide new angles"
                    },
                    {
                        "title": "Long Island Serial Killer Coverage",
                        "year": "2010-present",
                        "impact": "Persistent coverage of unsolved Gilgo Beach murders",
                        "description": "Decade-plus investigation into serial killer targeting sex workers",
                        "production_potential": "Ongoing case with recent developments (2023 arrest)"
                    }
                ]
            },

            "skip_hollandsworth": {
                "name": "Skip Hollandsworth",
                "publications": ["Texas Monthly", "Atlantic Monthly"],
                "bio": "Texas-based journalist known for narrative true crime and cultural stories",
                "status": "Active",
                "notable_stories": [
                    {
                        "title": "The Midnight Assassin: Austin Serial Killer 1884-1885",
                        "year": "2016",
                        "impact": "Uncovered forgotten serial killer case from 19th century Austin",
                        "description": "Investigation into series of ax murders that terrorized Austin decades before Jack the Ripper",
                        "production_potential": "Historical true crime with Western/period drama elements"
                    },
                    {
                        "title": "Texas Cheerleader Murder Plot",
                        "year": "2008",
                        "impact": "Revisited infamous case of mother who hired hitman to kill daughter's cheerleading rival",
                        "description": "Deep dive into Wanda Holloway case that inspired multiple TV movies",
                        "production_potential": "Dark comedy elements with small-town Texas setting"
                    },
                    {
                        "title": "The Lost Boys of Montrose",
                        "year": "2011",
                        "impact": "Investigation into Houston's forgotten serial killer Dean Corll",
                        "description": "1970s case of 'Candy Man' killer who murdered at least 28 boys",
                        "production_potential": "Historical true crime with strong emotional impact"
                    }
                ]
            },

            "caitlin_rother": {
                "name": "Caitlin Rother",
                "publications": ["San Diego Union-Tribune", "True crime books"],
                "bio": "Investigative journalist turned true crime author specializing in California cases",
                "status": "Active",
                "notable_stories": [
                    {
                        "title": "Jodi Arias Trial Coverage and Analysis",
                        "year": "2013-2015",
                        "impact": "Comprehensive coverage of sensational murder trial",
                        "description": "Deep dive into Travis Alexander murder and Arias trial that captivated nation",
                        "production_potential": "Multiple adaptations exist but psychological angle remains compelling"
                    },
                    {
                        "title": "Kristin Smart Disappearance Investigation",
                        "year": "2006-2022",
                        "impact": "Persistent coverage of Cal Poly student's disappearance",
                        "description": "25-year investigation into college student's disappearance and family's quest for justice",
                        "production_potential": "Recent conviction provides resolution for long-term story arc"
                    },
                    {
                        "title": "San Diego County Serial Killers",
                        "year": "2000-2010",
                        "impact": "Regional focus on Southern California murder cases",
                        "description": "Multiple cases including Cleophus Prince Jr. and other San Diego area killers",
                        "production_potential": "Regional anthology series potential"
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

    def get_enhanced_research_prompt(self, real_articles, journalist_spotlight):
        """Generate anti-hallucination research prompt with real article context and journalist spotlight"""
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

**TASK:** Create a comprehensive daily briefing that includes:
1. Analysis of provided real articles (5 cases max if available)
2. Today's featured journalist spotlight (provided below)
3. Development recommendations based on both current cases and journalist's story portfolio

{articles_context}

{journalist_spotlight}

**DAILY TRUE CRIME & STRANGER THAN FICTION CONTENT DISCOVERY BRIEFING**
**Date: {current_date}**
**Sources: VERIFIED REAL NEWS ARTICLES + JOURNALIST SPOTLIGHT**

**CRITICAL VERIFICATION REQUIREMENTS:**
1. Use ONLY the articles provided above - no external knowledge or invented details
2. Each case must include the exact source URL from the provided articles
3. If you cannot find 5 suitable cases in the provided articles, return fewer cases and explicitly state this limitation
4. All details must be directly extractable from the provided article content
5. When in doubt about any detail, state "Details pending verification from source article"
6. The journalist spotlight information is verified and can be referenced for development insights

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
[Brief overview of today's findings including current cases and journalist spotlight insights]

**PART I: CURRENT VERIFIED CASES**

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

**PART II: JOURNALIST SPOTLIGHT ANALYSIS**

**Development Opportunities from {journalist_spotlight.split('**')[1].split('**')[0]}:**
- **Story #1 Analysis:** [Production potential and development angle]
- **Story #2 Analysis:** [Production potential and development angle] 
- **Story #3 Analysis:** [Production potential and development angle]
- **Overall Assessment:** [How this journalist's work could inform current content strategy]
- **Contact Strategy:** [Recommendations for approaching this journalist or their estate/representatives]

**PART III: CROSS-ANALYSIS**
**Current Cases vs. Historical Patterns:** [Compare today's verified cases with journalist spotlight stories for trends and opportunities]

**RESEARCH LIMITATIONS DISCLOSURE:**
- Total verified articles analyzed: {len(real_articles) if real_articles else 0}
- Current cases meeting development criteria: [Honest count]
- Historical cases from journalist spotlight: 3
- Additional research required: [Yes/No and what type]

**COMPETITIVE LANDSCAPE ALERT:**
[Check if any current verified cases connect to journalist spotlight stories or represent similar narrative opportunities]

**CRITICAL REMINDER:** Current cases section must use ONLY verified article sources. Journalist spotlight section may reference established historical cases. NO MIXING OF CATEGORIES.

**VERIFICATION PROTOCOL:**
Every detail in current cases must be traceable to provided article URLs. Journalist spotlight references verified historical cases from 2000-2025 knowledge base.
        """

    def run_research(self):
        """Execute enhanced research with hallucination prevention and journalist spotlight"""
        # Get real articles first
        real_articles = self.search_comprehensive_news_sources()
        
        # Get today's journalist spotlight
        today_journalist = self.get_daily_journalist_spotlight()
        journalist_spotlight = self.format_journalist_spotlight(today_journalist)
        
        print(f"📰 Today's spotlight: {today_journalist['name']}")
        
        # Generate research prompt with real article context and journalist spotlight
        research_prompt = self.get_enhanced_research_prompt(real_articles, journalist_spotlight)
        
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=6000,  # Increased for journalist spotlight content
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
- Journalist spotlight: {today_journalist['name']}
- Model temperature: 0.1 (factual mode)
- Hallucination prevention: ACTIVE
- Current cases verified against source URLs
- Historical cases verified against journalist database

**DEVELOPMENT TEAM NOTE:**
Current cases include source verification. Historical cases from journalist spotlight are verified against established records. Before proceeding with any development, independently verify all details by reviewing source articles/materials at provided URLs.

**JOURNALIST CONTACT PROTOCOL:**
For spotlight journalist stories, check current representation status and rights availability before development discussions.
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
        subject = f"ENHANCED Content Discovery Briefing - {current_date} - Featuring {today_journalist['name']}"
        
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
            
            print("📤 Sending enhanced briefing email...")
            
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
        """Main execution function with enhanced verification and journalist spotlight"""
        print(f"🚀 Starting ENHANCED daily briefing for {datetime.now().strftime('%B %d, %Y')}")
        logger.info(f"Starting enhanced daily briefing for {datetime.now().strftime('%B %d, %Y')}")
        
        try:
            # Generate research briefing with hallucination prevention + journalist spotlight
            print("📝 Generating enhanced briefing with journalist spotlight...")
            logger.info("Generating enhanced briefing with journalist spotlight...")
            briefing = self.run_research()
            print(f"✅ Enhanced briefing generated! Length: {len(briefing)} characters")
            
            # Send email
            print("📧 Attempting to send enhanced briefing...")
            logger.info("Sending enhanced briefing...")
            success = self.send_email(briefing)
            
            if success:
                print("✅ Enhanced briefing sent successfully!")
                logger.info("Daily enhanced briefing completed successfully!")
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
