import anthropic
import os
import requests
import json
import smtplib
import logging
import time
import random
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import xml.etree.ElementTree as ET
from dateutil import parser
import pytz

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
        
        # CRITICAL: Set timezone and freshness thresholds
        self.timezone = pytz.timezone('US/Pacific')
        self.max_age_hours = 48  # Maximum age for "fresh" articles
        self.preferred_age_hours = 24  # Preferred age for priority articles

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
                    }
                ]
            }
        }

    def get_daily_journalist_spotlight(self):
        """Select a journalist for today's briefing spotlight"""
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

**TOP ATTENTION-GRABBING STORIES:**
"""
        
        for i, story in enumerate(journalist_data['notable_stories'], 1):
            spotlight += f"""**{i}. {story['title']}** ({story['year']})
   **Impact:** {story['impact']}
   **Story:** {story['description']}
   **Production Potential:** {story['production_potential']}

"""
        return spotlight

    def parse_article_date(self, date_string, source_name="Unknown"):
        """ROBUST date parsing with multiple format support and validation"""
        if not date_string:
            return None
            
        try:
            # Remove any timezone abbreviations that cause issues
            cleaned_date = date_string.replace(' GMT', '').replace(' UTC', '').replace(' EST', '').replace(' PST', '')
            
            # Try multiple parsing methods
            parsed_date = None
            
            # Method 1: Use dateutil parser (most flexible)
            try:
                parsed_date = parser.parse(cleaned_date)
            except:
                pass
            
            # Method 2: Try common RSS formats
            if not parsed_date:
                rss_formats = [
                    '%a, %d %b %Y %H:%M:%S',
                    '%d %b %Y %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%dT%H:%M:%SZ'
                ]
                
                for fmt in rss_formats:
                    try:
                        parsed_date = datetime.strptime(cleaned_date, fmt)
                        break
                    except:
                        continue
            
            if parsed_date:
                # Remove timezone info for consistent comparison
                if parsed_date.tzinfo:
                    parsed_date = parsed_date.replace(tzinfo=None)
                
                # Validate date is reasonable (not future, not too old)
                now = datetime.now()
                max_past = now - timedelta(days=365)  # Not older than 1 year
                
                if parsed_date <= now and parsed_date >= max_past:
                    return parsed_date
                else:
                    print(f"   ⚠️ Date outside reasonable range: {parsed_date} from {source_name}")
                    return None
            
            print(f"   ❌ Could not parse date: '{date_string}' from {source_name}")
            return None
            
        except Exception as e:
            print(f"   ❌ Date parsing error for '{date_string}' from {source_name}: {e}")
            return None

    def is_article_fresh(self, article_date, article_title=""):
        """Determine if an article is within our freshness window"""
        if not article_date:
            return False, "No date"
        
        now = datetime.now()
        age_hours = (now - article_date).total_seconds() / 3600
        
        if age_hours <= self.preferred_age_hours:
            return True, f"Very fresh ({age_hours:.1f}h old)"
        elif age_hours <= self.max_age_hours:
            return True, f"Fresh ({age_hours:.1f}h old)"
        else:
            return False, f"Stale ({age_hours:.1f}h old)"

    def search_comprehensive_news_sources(self):
        """FIXED: Enhanced news search with REAL FRESHNESS VALIDATION"""
        print(f"🔍 Starting comprehensive news search...")
        print(f"📅 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Freshness window: {self.max_age_hours} hours ({self.max_age_hours/24:.1f} days)")
        
        all_articles = []
        
        # Search News API first (most reliable for fresh content)
        print("\n📰 Searching News API...")
        news_api_articles = self.search_news_api()
        all_articles.extend(news_api_articles)
        
        # Search Google News RSS as supplement
        print("\n🌐 Searching Google News RSS...")
        google_news_articles = self.search_google_news_rss()
        all_articles.extend(google_news_articles)
        
        print(f"\n📊 RAW COLLECTION STATS:")
        print(f"   News API articles: {len(news_api_articles)}")
        print(f"   Google RSS articles: {len(google_news_articles)}")
        print(f"   Total raw articles: {len(all_articles)}")
        
        # CRITICAL: Apply strict freshness filtering
        fresh_articles = []
        stale_articles = []
        no_date_articles = []
        
        for article in all_articles:
            article_date = self.parse_article_date(article.get('published', ''), article.get('source', 'Unknown'))
            
            if article_date:
                is_fresh, reason = self.is_article_fresh(article_date, article.get('title', ''))
                article['parsed_date'] = article_date
                article['freshness_reason'] = reason
                
                if is_fresh:
                    fresh_articles.append(article)
                    print(f"   ✅ {reason}: {article.get('title', '')[:60]}...")
                else:
                    stale_articles.append(article)
                    print(f"   ❌ {reason}: {article.get('title', '')[:60]}...")
            else:
                no_date_articles.append(article)
                print(f"   ⚠️ No valid date: {article.get('title', '')[:60]}...")
        
        # Remove duplicates from fresh articles only
        seen_urls = set()
        seen_titles = set()
        unique_fresh_articles = []
        
        # Sort fresh articles by date (newest first)
        fresh_articles.sort(key=lambda x: x.get('parsed_date', datetime.min), reverse=True)
        
        for article in fresh_articles:
            url = article.get('url', '')
            title = article.get('title', '').lower().strip()
            
            if url in seen_urls:
                continue
                
            # Check for very similar titles
            title_words = set(title.split())
            is_duplicate = False
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                if len(title_words) > 0 and len(seen_words) > 0:
                    overlap = len(title_words.intersection(seen_words)) / max(len(title_words), len(seen_words))
                    if overlap > 0.7:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                seen_urls.add(url)
                seen_titles.add(title)
                unique_fresh_articles.append(article)
        
        # Final stats
        print(f"\n📊 FRESHNESS FILTERING RESULTS:")
        print(f"   ✅ Fresh articles: {len(fresh_articles)}")
        print(f"   ❌ Stale articles: {len(stale_articles)}")
        print(f"   ⚠️ No date articles: {len(no_date_articles)}")
        print(f"   🎯 Unique fresh articles: {len(unique_fresh_articles)}")
        
        if len(unique_fresh_articles) == 0:
            print("\n🚨 WARNING: NO FRESH ARTICLES FOUND!")
            print("   This indicates a serious problem with news sources or date filtering.")
            print("   Check API keys, network connectivity, and date parsing logic.")
        
        return unique_fresh_articles

    def search_news_api(self):
        """Search News API with strict freshness requirements"""
        api_key = os.getenv('NEWS_API_KEY')
        if not api_key:
            print("⚠️ NEWS_API_KEY not found, skipping News API search")
            return []
            
        print("🔍 Searching News API for fresh true crime articles...")
        
        # Focus on premium news sources
        sources = [
            'abc-news', 'cbs-news', 'cnn', 'nbc-news', 'reuters', 
            'associated-press', 'time', 'bloomberg', 'business-insider'
        ]
        
        all_articles = []
        
        # Targeted search queries
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
        
        # Set strict date range (last 2 days only)
        from_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        
        for query in search_queries:
            try:
                print(f"   🔍 Query: {query}")
                
                url = f"https://newsapi.org/v2/everything"
                params = {
                    'q': query,
                    'sources': ','.join(sources),
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 20,
                    'from': from_date,
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
                    
                    print(f"      Found {len(articles)} articles")
                elif response.status_code == 429:
                    print(f"      Rate limit hit, waiting...")
                    time.sleep(5)
                else:
                    print(f"      API error: {response.status_code}")
                
                time.sleep(1.5)  # Rate limiting
                
            except Exception as e:
                print(f"      Error: {str(e)}")
                continue
        
        print(f"📰 News API collected: {len(all_articles)} articles")
        return all_articles

    def search_google_news_rss(self):
        """FIXED: Search Google News RSS with proper date filtering"""
        print("🔍 Searching Google News RSS feeds with strict date filtering...")
        
        queries = [
            'crime+investigation', 'murder+case', 'cold+case+solved',
            'DNA+evidence+conviction', 'forensic+breakthrough', 'criminal+arrest'
        ]
        
        all_articles = []
        cutoff_date = datetime.now() - timedelta(hours=self.max_age_hours)
        
        print(f"   📅 RSS cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        for query in queries:
            try:
                print(f"   🔍 RSS Query: {query}")
                url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
                
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    try:
                        root = ET.fromstring(response.content)
                        query_articles = 0
                        fresh_count = 0
                        
                        for item in root.findall('.//item'):
                            title_elem = item.find('title')
                            link_elem = item.find('link')
                            pub_date_elem = item.find('pubDate')
                            description_elem = item.find('description')
                            
                            if title_elem is not None and link_elem is not None and pub_date_elem is not None:
                                query_articles += 1
                                
                                # Parse and validate date
                                article_date = self.parse_article_date(pub_date_elem.text, 'Google RSS')
                                
                                if article_date and article_date >= cutoff_date:
                                    fresh_count += 1
                                    all_articles.append({
                                        'title': title_elem.text,
                                        'url': link_elem.text,
                                        'source': 'Google News RSS',
                                        'published': pub_date_elem.text,
                                        'description': description_elem.text if description_elem is not None else '',
                                        'search_query': query
                                    })
                                    print(f"      ✅ Fresh: {title_elem.text[:50]}... ({article_date.strftime('%Y-%m-%d %H:%M')})")
                                elif article_date:
                                    print(f"      ❌ Stale: {title_elem.text[:50]}... ({article_date.strftime('%Y-%m-%d %H:%M')})")
                                else:
                                    print(f"      ⚠️ No date: {title_elem.text[:50]}...")
                        
                        print(f"      Found {query_articles} articles, {fresh_count} fresh")
                    
                    except ET.ParseError as e:
                        print(f"      XML parsing error: {e}")
                else:
                    print(f"      HTTP error: {response.status_code}")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"      RSS error for {query}: {str(e)}")
                continue
        
        print(f"🌐 Google RSS collected: {len(all_articles)} fresh articles")
        return all_articles

    def get_ultra_strict_prompt(self, real_articles, journalist_spotlight):
        """Generate ULTRA-STRICT anti-hallucination prompt with freshness validation"""
        current_date = datetime.now().strftime('%B %d, %Y')
        current_time = datetime.now().strftime('%H:%M:%S PST')
        
        # Create article list with freshness indicators
        articles_text = ""
        if real_articles and len(real_articles) > 0:
            articles_text = f"\n=== {len(real_articles)} VERIFIED FRESH ARTICLES ===\n"
            articles_text += f"All articles below have been verified as published within the last {self.max_age_hours} hours.\n\n"
            
            for i, article in enumerate(real_articles[:40]):
                freshness = article.get('freshness_reason', 'Unknown age')
                articles_text += f"ARTICLE #{i+1}:\n"
                articles_text += f"Title: {article['title']}\n"
                articles_text += f"Source: {article['source']}\n"
                articles_text += f"URL: {article['url']}\n"
                articles_text += f"Published: {article['published']}\n"
                articles_text += f"Freshness: {freshness}\n"
                articles_text += f"Description: {article.get('description', 'No description')}\n"
                if article.get('content'):
                    articles_text += f"Content: {article['content'][:200]}...\n"
                articles_text += "-" * 50 + "\n\n"
        else:
            articles_text = f"\n=== NO FRESH ARTICLES AVAILABLE ===\n"
            articles_text += "CRITICAL: No articles from the last 48 hours were found.\n"
            articles_text += "This may indicate technical issues with news sources.\n\n"
        
        return f"""**ULTRA-STRICT VERIFICATION PROTOCOL - FRESHNESS GUARANTEED**

TODAY'S DATE: {current_date}
CURRENT TIME: {current_time}
FRESHNESS WINDOW: Last {self.max_age_hours} hours

**CRITICAL FRESHNESS VALIDATION:**
Every article below has been validated to be published within the last {self.max_age_hours} hours.
Articles older than this threshold have been automatically excluded.

{articles_text}

{journalist_spotlight}

**ABSOLUTE REQUIREMENTS:**
1. Use ONLY articles from the verified list above
2. Reference articles by ARTICLE # (e.g., "ARTICLE #1")
3. If fewer than 5 fresh articles available, acknowledge this limitation
4. Prioritize articles with "Very fresh" indicators
5. Include actual publication times and freshness indicators

**MANDATORY OUTPUT:**

EXECUTIVE SUMMARY:
I have reviewed {len(real_articles)} verified fresh articles from the last {self.max_age_hours} hours. [Continue with honest assessment]

**VERIFIED FRESH CASES:**

[For each case, include:]
- **Source:** [From article list]
- **Published:** [Exact timestamp from article]  
- **Freshness:** [From freshness_reason field]
- **Verification:** CONFIRMED FROM ARTICLE #X

**FRESHNESS GUARANTEE VERIFICATION:**
- Search conducted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Articles filtered by date: {self.max_age_hours} hour window enforced
- Stale articles excluded: YES
- Fresh articles available: {len(real_articles)}
"""

    def run_research(self):
        """Execute research with REAL freshness validation"""
        print(f"🚀 Starting VERIFIED FRESH research for {datetime.now().strftime('%B %d, %Y')}")
        
        # Get genuinely fresh articles
        real_articles = self.search_comprehensive_news_sources()
        
        if len(real_articles) == 0:
            error_msg = """
🚨 CRITICAL ERROR: NO FRESH ARTICLES FOUND

This indicates a serious system failure:
- News API may be down or invalid key
- RSS feeds may be returning only old content  
- Date parsing may be completely broken
- Network connectivity issues

RECOMMENDATION: Do not send briefing until this is resolved.
"""
            print(error_msg)
            return error_msg
        
        print(f"✅ Found {len(real_articles)} genuinely fresh articles")
        
        # Get journalist spotlight
        today_journalist = self.get_daily_journalist_spotlight()
        journalist_spotlight = self.format_journalist_spotlight(today_journalist)
        
        # Generate research
        research_prompt = self.get_ultra_strict_prompt(real_articles, journalist_spotlight)
        
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=6000,
                temperature=0.0,
                messages=[{"role": "user", "content": research_prompt}]
            )
            
            response_content = message.content[0].text
            
            # Add verification footer
            verification_footer = f"""

**SYSTEM VERIFICATION - FRESHNESS GUARANTEED:**
- Search time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S PST')}
- Fresh articles found: {len(real_articles)}
- Freshness window: {self.max_age_hours} hours
- Oldest allowed article: {(datetime.now() - timedelta(hours=self.max_age_hours)).strftime('%Y-%m-%d %H:%M:%S')}
- Date filtering: VERIFIED ACTIVE
- Stale article removal: VERIFIED ACTIVE

**DEVELOPMENT TEAM ALERT:**
All articles have been verified fresh within the last {self.max_age_hours} hours.
If this briefing contains old articles, there is a critical system bug.
"""
            
            return response_content + verification_footer
            
        except Exception as e:
            logger.error(f"Error generating briefing: {str(e)}")
            return f"Error generating briefing: {str(e)}"

    def send_email(self, briefing_content):
        """Send briefing via Gmail with proper encoding"""
        try:
            sender_email = os.environ.get("GMAIL_ADDRESS", "").strip()
            sender_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
            recipients = ["danny@kontentfarm.com"]
            
            current_date = datetime.now().strftime('%B %d, %Y')
            today_journalist = self.get_daily_journalist_spotlight()
            subject = f"VERIFIED FRESH Daily Briefing - {current_date} - {today_journalist['name']} Spotlight"
            
            # Create proper email message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # Add content
            msg.attach(MIMEText(briefing_content, 'plain'))
            
            # Send via Gmail
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            print("✅ Email sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Email error: {str(e)}")
            return False

    def run_daily_briefing(self):
        """Main execution with VERIFIED freshness guarantee"""
        print(f"🚀 Starting VERIFIED FRESH briefing for {datetime.now().strftime('%B %d, %Y %H:%M:%S')}")
        
        try:
            briefing = self.run_research()
            
            # Don't send if critical errors
            if "CRITICAL ERROR" in briefing:
                print("❌ Briefing contains critical errors - not sending")
                print(briefing)
                return
            
            success = self.send_email(briefing)
            
            if success:
                print("✅ VERIFIED FRESH briefing sent successfully!")
            else:
                print("❌ Email failed - briefing not delivered")
                
        except Exception as e:
            print(f"❌ Critical error: {str(e)}")
            raise

if __name__ == "__main__":
    briefing_system = TrueCrimeBriefingGenerator()
    briefing_system.run_daily_briefing()
