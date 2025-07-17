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
import xml.etree.ElementTree as ET
import re

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
        
        # CRITICAL: Set freshness thresholds
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
        """ROBUST date parsing using only standard library"""
        if not date_string:
            return None
            
        try:
            # Clean the date string
            cleaned_date = str(date_string).strip()
            
            # Remove timezone abbreviations
            tz_abbrevs = [' GMT', ' UTC', ' EST', ' PST', ' CST', ' MST', ' EDT', ' PDT', ' CDT', ' MDT']
            for tz in tz_abbrevs:
                cleaned_date = cleaned_date.replace(tz, '')
            
            # Remove timezone offsets like +0000, -0500
            tz_pattern = r'\s*[+-]\d{4}$'
            cleaned_date = re.sub(tz_pattern, '', cleaned_date)
            
            # Date format patterns to try
            formats = [
                '%a, %d %b %Y %H:%M:%S',  # RSS format
                '%d %b %Y %H:%M:%S',      # Simplified RSS
                '%Y-%m-%dT%H:%M:%S',      # ISO format
                '%Y-%m-%d %H:%M:%S',      # Standard format
                '%Y-%m-%d',               # Date only
                '%m/%d/%Y %H:%M:%S',      # US format
                '%m/%d/%Y',               # US date only
            ]
            
            parsed_date = None
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(cleaned_date, fmt)
                    break
                except ValueError:
                    continue
            
            if parsed_date:
                # Validate reasonable date range
                now = datetime.now()
                one_year_ago = now - timedelta(days=365)
                one_hour_future = now + timedelta(hours=1)
                
                if one_year_ago <= parsed_date <= one_hour_future:
                    return parsed_date
                else:
                    print(f"   ⚠️ Date out of range: {parsed_date} from {source_name}")
                    return None
            
            print(f"   ❌ Could not parse: '{date_string}' from {source_name}")
            return None
            
        except Exception as e:
            print(f"   ❌ Parse error: {str(e)} for '{date_string}' from {source_name}")
            return None

    def is_article_fresh(self, article_date, article_title=""):
        """Determine if an article is within freshness window"""
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
        """Enhanced news search with REAL freshness validation"""
        print(f"🔍 Starting news search at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Freshness window: {self.max_age_hours} hours")
        
        all_articles = []
        
        # Search News API
        print("\n📰 Searching News API...")
        news_api_articles = self.search_news_api()
        all_articles.extend(news_api_articles)
        
        # Search Google News RSS
        print("\n🌐 Searching Google News RSS...")
        google_news_articles = self.search_google_news_rss()
        all_articles.extend(google_news_articles)
        
        print(f"\n📊 Raw collection: {len(all_articles)} total articles")
        
        # Apply freshness filtering
        fresh_articles = []
        stale_articles = []
        no_date_articles = []
        
        for article in all_articles:
            date_str = article.get('published', '')
            article_date = self.parse_article_date(date_str, article.get('source', 'Unknown'))
            
            if article_date:
                is_fresh, reason = self.is_article_fresh(article_date)
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
                print(f"   ⚠️ No date: {article.get('title', '')[:60]}...")
        
        # Remove duplicates from fresh articles
        seen_urls = set()
        seen_titles = set()
        unique_fresh = []
        
        # Sort by date (newest first)
        fresh_articles.sort(key=lambda x: x.get('parsed_date', datetime.min), reverse=True)
        
        for article in fresh_articles:
            url = article.get('url', '')
            title = article.get('title', '').lower().strip()
            
            if url in seen_urls:
                continue
                
            # Check for similar titles
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
                unique_fresh.append(article)
        
        print(f"\n📊 FRESHNESS RESULTS:")
        print(f"   ✅ Fresh: {len(fresh_articles)}")
        print(f"   ❌ Stale: {len(stale_articles)}")
        print(f"   ⚠️ No date: {len(no_date_articles)}")
        print(f"   🎯 Unique fresh: {len(unique_fresh)}")
        
        if len(unique_fresh) == 0:
            print("\n🚨 WARNING: NO FRESH ARTICLES FOUND!")
        
        return unique_fresh

    def search_news_api(self):
        """Search News API with strict freshness"""
        api_key = os.getenv('NEWS_API_KEY')
        if not api_key:
            print("⚠️ NEWS_API_KEY not found")
            return []
            
        sources = ['abc-news', 'cbs-news', 'cnn', 'nbc-news', 'reuters', 'associated-press']
        
        queries = [
            'murder conviction DNA evidence',
            'cold case arrest genetic genealogy',
            'serial killer identified forensics',
            'wrongful conviction exonerated',
            'criminal trial verdict',
            'homicide investigation breakthrough'
        ]
        
        all_articles = []
        from_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        
        for query in queries:
            try:
                print(f"   🔍 {query}")
                
                url = "https://newsapi.org/v2/everything"
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
                                'author': article.get('author', 'Unknown'),
                                'published': article['publishedAt'],
                                'description': article.get('description', ''),
                                'content': article.get('content', ''),
                                'search_query': query
                            })
                    
                    print(f"      Found {len(articles)} articles")
                else:
                    print(f"      API error: {response.status_code}")
                
                time.sleep(1.5)
                
            except Exception as e:
                print(f"      Error: {str(e)}")
                continue
        
        print(f"📰 News API total: {len(all_articles)}")
        return all_articles

    def search_google_news_rss(self):
        """Search Google News RSS with date filtering"""
        queries = ['crime+investigation', 'murder+case', 'DNA+evidence+conviction']
        all_articles = []
        cutoff_date = datetime.now() - timedelta(hours=self.max_age_hours)
        
        for query in queries:
            try:
                print(f"   🔍 RSS: {query}")
                url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
                
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    try:
                        root = ET.fromstring(response.content)
                        fresh_count = 0
                        
                        for item in root.findall('.//item'):
                            title_elem = item.find('title')
                            link_elem = item.find('link')
                            pub_date_elem = item.find('pubDate')
                            desc_elem = item.find('description')
                            
                            if title_elem is not None and link_elem is not None and pub_date_elem is not None:
                                article_date = self.parse_article_date(pub_date_elem.text, 'Google RSS')
                                
                                if article_date and article_date >= cutoff_date:
                                    fresh_count += 1
                                    all_articles.append({
                                        'title': title_elem.text,
                                        'url': link_elem.text,
                                        'source': 'Google News RSS',
                                        'published': pub_date_elem.text,
                                        'description': desc_elem.text if desc_elem is not None else '',
                                        'search_query': query
                                    })
                                    print(f"      ✅ Fresh RSS article")
                        
                        print(f"      {fresh_count} fresh from RSS")
                    
                    except ET.ParseError as e:
                        print(f"      XML error: {e}")
                else:
                    print(f"      HTTP error: {response.status_code}")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"      RSS error: {str(e)}")
                continue
        
        print(f"🌐 RSS total: {len(all_articles)}")
        return all_articles

    def get_ultra_strict_prompt(self, real_articles, journalist_spotlight):
        """Generate verification prompt with freshness validation"""
        current_date = datetime.now().strftime('%B %d, %Y')
        current_time = datetime.now().strftime('%H:%M:%S')
        
        articles_text = ""
        if real_articles and len(real_articles) > 0:
            articles_text = f"\n=== {len(real_articles)} VERIFIED FRESH ARTICLES ===\n\n"
            
            for i, article in enumerate(real_articles[:40]):
                freshness = article.get('freshness_reason', 'Unknown age')
                articles_text += f"ARTICLE #{i+1}:\n"
                articles_text += f"Title: {article['title']}\n"
                articles_text += f"Source: {article['source']}\n"
                articles_text += f"URL: {article['url']}\n"
                articles_text += f"Published: {article['published']}\n"
                articles_text += f"Freshness: {freshness}\n"
                articles_text += f"Description: {article.get('description', 'No description')}\n"
                articles_text += "-" * 50 + "\n\n"
        else:
            articles_text = "\n=== NO FRESH ARTICLES AVAILABLE ===\n"
            articles_text += "CRITICAL: No articles from the last 48 hours were found.\n\n"
        
        return f"""**ULTRA-STRICT VERIFICATION PROTOCOL**

TODAY'S DATE: {current_date}
CURRENT TIME: {current_time}
FRESHNESS WINDOW: Last {self.max_age_hours} hours

**FRESHNESS VALIDATION:**
Articles below verified as published within last {self.max_age_hours} hours.

{articles_text}

{journalist_spotlight}

**REQUIREMENTS:**
1. Use ONLY articles from verified list above
2. Reference by ARTICLE # (e.g., "ARTICLE #1")
3. If fewer than 5 fresh articles, acknowledge limitation
4. Include freshness indicators

**OUTPUT FORMAT:**

EXECUTIVE SUMMARY:
I reviewed {len(real_articles)} fresh articles from last {self.max_age_hours} hours.

**VERIFIED FRESH CASES:**

**CASE #1 - ARTICLE #[X]**
- Source: [From article list]
- Published: [Exact timestamp]
- Freshness: [From freshness_reason]
- Verification: CONFIRMED FROM ARTICLE #X

[Continue for available cases...]

**FRESHNESS VERIFICATION:**
- Search time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Fresh articles: {len(real_articles)}
- Window enforced: {self.max_age_hours} hours
"""

    def run_research(self):
        """Execute research with freshness validation"""
        print(f"🚀 Starting research for {datetime.now().strftime('%B %d, %Y')}")
        
        # Get fresh articles
        real_articles = self.search_comprehensive_news_sources()
        
        if len(real_articles) == 0:
            error_msg = """
🚨 NO FRESH ARTICLES FOUND

System failure detected:
- No articles within 48-hour window
- Check API keys and connectivity
- Do not send briefing
"""
            print(error_msg)
            return error_msg
        
        print(f"✅ Found {len(real_articles)} fresh articles")
        
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
            
            verification_footer = f"""

**SYSTEM VERIFICATION:**
- Search time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Fresh articles: {len(real_articles)}
- Window: {self.max_age_hours} hours
- Filtering: ACTIVE

**ALERT:** All articles verified fresh within {self.max_age_hours} hours.
"""
            
            return response_content + verification_footer
            
        except Exception as e:
            logger.error(f"Error generating briefing: {str(e)}")
            return f"Error generating briefing: {str(e)}"

    def send_email(self, briefing_content):
        """Send briefing via Gmail"""
        try:
            sender_email = os.environ.get("GMAIL_ADDRESS", "").strip()
            sender_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
            recipients = ["danny@kontentfarm.com"]
            
            current_date = datetime.now().strftime('%B %d, %Y')
            today_journalist = self.get_daily_journalist_spotlight()
            subject = f"FRESH Daily Briefing - {current_date} - {today_journalist['name']}"
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(briefing_content, 'plain'))
            
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
        """Main execution with freshness guarantee"""
        print(f"🚀 Starting briefing for {datetime.now().strftime('%B %d, %Y %H:%M:%S')}")
        
        try:
            briefing = self.run_research()
            
            if "NO FRESH ARTICLES" in briefing:
                print("❌ No fresh content - not sending briefing")
                print(briefing)
                return
            
            success = self.send_email(briefing)
            
            if success:
                print("✅ Fresh briefing sent successfully!")
            else:
                print("❌ Email failed")
                
        except Exception as e:
            print(f"❌ Critical error: {str(e)}")
            raise

if __name__ == "__main__":
    briefing_system = TrueCrimeBriefingGenerator()
    briefing_system.run_daily_briefing()
