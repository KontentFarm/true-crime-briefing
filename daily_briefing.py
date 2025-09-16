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
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PremiumSiteContentDiscovery:
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
        
        # Premium website configurations
        self.target_sites = self._build_site_database()
        
        # Content categories and keywords
        self.categories = {
            'true_crime': {
                'keywords': ['murder', 'serial killer', 'cold case', 'investigation', 'crime', 'detective', 'forensic', 'criminal', 'homicide', 'mystery'],
                'target_count': 3
            },
            'stranger_than_fiction': {
                'keywords': ['bizarre', 'unusual', 'strange', 'weird', 'unbelievable', 'extraordinary', 'shocking', 'incredible', 'mysterious', 'unexplained'],
                'target_count': 3
            },
            'nineties_2000s_culture': {
                'keywords': ['90s', '1990s', '2000s', 'millennium', 'Y2K', 'nostalgia', 'anniversary', 'retrospective', 'throwback', 'decade'],
                'target_count': 3
            }
        }
        
        self.max_age_hours = 72  # 3 days for premium content

    def _build_site_database(self):
        """Database of premium sites with RSS feeds and access methods"""
        return {
            'wired': {
                'name': 'WIRED',
                'rss_feeds': [
                    'https://www.wired.com/feed/rss',
                    'https://www.wired.com/feed/category/culture/rss',
                    'https://www.wired.com/feed/category/security/rss'
                ],
                'base_url': 'https://www.wired.com',
                'user_agent': 'Mozilla/5.0 (compatible; ContentBot/1.0)'
            },
            'time': {
                'name': 'TIME',
                'rss_feeds': [
                    'https://feeds.feedburner.com/time/topstories',
                    'https://feeds.feedburner.com/time/entertainment'
                ],
                'base_url': 'https://time.com',
                'user_agent': 'Mozilla/5.0 (compatible; ContentBot/1.0)'
            },
            'vanity_fair': {
                'name': 'Vanity Fair',
                'rss_feeds': [
                    'https://www.vanityfair.com/feed/rss',
                    'https://www.vanityfair.com/hollywood/rss',
                    'https://www.vanityfair.com/culture/rss'
                ],
                'base_url': 'https://www.vanityfair.com',
                'user_agent': 'Mozilla/5.0 (compatible; ContentBot/1.0)'
            },
            'ny_post': {
                'name': 'New York Post',
                'rss_feeds': [
                    'https://nypost.com/feed/',
                    'https://nypost.com/entertainment/feed/',
                    'https://nypost.com/news/feed/'
                ],
                'base_url': 'https://nypost.com',
                'user_agent': 'Mozilla/5.0 (compatible; ContentBot/1.0)'
            },
            'bloomberg': {
                'name': 'Bloomberg',
                'rss_feeds': [
                    'https://www.bloomberg.com/feed/podcast/rss.xml',
                    'https://feeds.bloomberg.com/markets/news.rss'
                ],
                'base_url': 'https://www.bloomberg.com',
                'user_agent': 'Mozilla/5.0 (compatible; ContentBot/1.0)'
            },
            'rolling_stone': {
                'name': 'Rolling Stone',
                'rss_feeds': [
                    'https://www.rollingstone.com/feed/',
                    'https://www.rollingstone.com/culture/feed/',
                    'https://www.rollingstone.com/music/feed/'
                ],
                'base_url': 'https://www.rollingstone.com',
                'user_agent': 'Mozilla/5.0 (compatible; ContentBot/1.0)'
            },
            'vulture': {
                'name': 'Vulture',
                'rss_feeds': [
                    'https://www.vulture.com/rss/index.xml',
                    'https://www.vulture.com/rss/tv.xml',
                    'https://www.vulture.com/rss/movies.xml'
                ],
                'base_url': 'https://www.vulture.com',
                'user_agent': 'Mozilla/5.0 (compatible; ContentBot/1.0)'
            }
        }

    def parse_article_date(self, date_string, source_name="Unknown"):
        """Parse article dates with multiple format support"""
        if not date_string:
            return None
            
        try:
            cleaned_date = str(date_string).strip()
            
            # Remove timezone info
            tz_abbrevs = [' GMT', ' UTC', ' EST', ' PST', ' CST', ' MST', ' EDT', ' PDT', ' CDT', ' MDT']
            for tz in tz_abbrevs:
                cleaned_date = cleaned_date.replace(tz, '')
            
            # Remove timezone offsets
            cleaned_date = re.sub(r'\s*[+-]\d{4}$', '', cleaned_date)
            
            formats = [
                '%a, %d %b %Y %H:%M:%S',
                '%d %b %Y %H:%M:%S', 
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%m/%d/%Y %H:%M:%S',
                '%m/%d/%Y'
            ]
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(cleaned_date, fmt)
                    # Validate reasonable range
                    now = datetime.now()
                    if (now - timedelta(days=365)) <= parsed_date <= (now + timedelta(hours=1)):
                        return parsed_date
                except ValueError:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Date parsing error for {source_name}: {e}")
            return None

    def fetch_rss_feed(self, feed_url, site_name):
        """Fetch and parse RSS feed with error handling"""
        try:
            headers = {
                'User-Agent': self.target_sites.get(site_name.lower().replace(' ', '_'), {}).get('user_agent', 'Mozilla/5.0 (compatible; ContentBot/1.0)'),
                'Accept': 'application/rss+xml, application/xml, text/xml'
            }
            
            response = requests.get(feed_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    root = ET.fromstring(response.content)
                    articles = []
                    
                    # Handle both RSS and Atom feeds
                    items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
                    
                    for item in items:
                        # RSS format
                        title_elem = item.find('title')
                        link_elem = item.find('link')
                        pub_date_elem = item.find('pubDate')
                        desc_elem = item.find('description')
                        
                        # Atom format fallbacks
                        if title_elem is None:
                            title_elem = item.find('.//{http://www.w3.org/2005/Atom}title')
                        if link_elem is None:
                            link_elem = item.find('.//{http://www.w3.org/2005/Atom}link')
                        if pub_date_elem is None:
                            pub_date_elem = item.find('.//{http://www.w3.org/2005/Atom}published')
                        if desc_elem is None:
                            desc_elem = item.find('.//{http://www.w3.org/2005/Atom}summary')
                        
                        if title_elem is not None and link_elem is not None:
                            # Get link URL (handle both text and href attributes)
                            link_url = link_elem.text if link_elem.text else link_elem.get('href', '')
                            
                            article_date = None
                            if pub_date_elem is not None:
                                article_date = self.parse_article_date(pub_date_elem.text, site_name)
                            
                            # Only include articles within our freshness window
                            if not article_date or (datetime.now() - article_date).total_seconds() / 3600 <= self.max_age_hours:
                                articles.append({
                                    'title': title_elem.text or '',
                                    'url': link_url,
                                    'source': site_name,
                                    'published': pub_date_elem.text if pub_date_elem is not None else '',
                                    'description': desc_elem.text if desc_elem is not None else '',
                                    'parsed_date': article_date,
                                    'feed_url': feed_url
                                })
                    
                    return articles
                    
                except ET.ParseError as e:
                    print(f"XML parsing error for {site_name}: {e}")
                    return []
            else:
                print(f"HTTP error {response.status_code} for {site_name} RSS")
                return []
                
        except Exception as e:
            print(f"Error fetching RSS for {site_name}: {e}")
            return []

    def search_all_premium_sites(self):
        """Fetch articles from all premium sites"""
        print(f"Searching premium sites at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_articles = []
        
        for site_key, site_info in self.target_sites.items():
            print(f"\nSearching {site_info['name']}...")
            site_articles = []
            
            for feed_url in site_info['rss_feeds']:
                print(f"  Fetching: {feed_url}")
                feed_articles = self.fetch_rss_feed(feed_url, site_info['name'])
                site_articles.extend(feed_articles)
                time.sleep(1)  # Rate limiting
            
            print(f"  Found {len(site_articles)} articles from {site_info['name']}")
            all_articles.extend(site_articles)
        
        print(f"\nTotal articles collected: {len(all_articles)}")
        return all_articles

    def categorize_articles(self, articles):
        """Categorize articles into true crime, stranger than fiction, and 90s/2000s culture"""
        categorized = {
            'true_crime': [],
            'stranger_than_fiction': [],
            'nineties_2000s_culture': []
        }
        
        print(f"\nCategorizing {len(articles)} articles...")
        
        for article in articles:
            title = (article.get('title', '') + ' ' + article.get('description', '')).lower()
            
            # Check each category
            for category, config in self.categories.items():
                score = 0
                matched_keywords = []
                
                for keyword in config['keywords']:
                    if keyword in title:
                        score += 1
                        matched_keywords.append(keyword)
                
                # If article matches keywords, add to category
                if score > 0:
                    article['category_score'] = score
                    article['matched_keywords'] = matched_keywords
                    categorized[category].append(article.copy())
        
        # Sort each category by score (highest first), then by date
        for category in categorized:
            categorized[category].sort(key=lambda x: (x.get('category_score', 0), x.get('parsed_date') or datetime.min), reverse=True)
        
        print(f"Categorization results:")
        for category, articles_list in categorized.items():
            print(f"  {category.replace('_', ' ').title()}: {len(articles_list)} articles")
        
        return categorized

    def select_top_articles(self, categorized_articles):
        """Select top articles for each category"""
        selected = {}
        
        for category, articles_list in categorized_articles.items():
            target_count = self.categories[category]['target_count']
            selected[category] = articles_list[:target_count]
            
            print(f"\nSelected {len(selected[category])} articles for {category.replace('_', ' ').title()}:")
            for i, article in enumerate(selected[category], 1):
                print(f"  {i}. {article['title'][:80]}... ({article['source']})")
        
        return selected

    def generate_briefing_prompt(self, selected_articles):
        """Generate prompt for Claude to create the briefing"""
        current_date = datetime.now().strftime('%B %d, %Y')
        current_time = datetime.now().strftime('%H:%M:%S')
        
        articles_text = ""
        total_articles = 0
        
        for category, articles_list in selected_articles.items():
            if articles_list:
                category_title = category.replace('_', ' ').title()
                articles_text += f"\n=== {category_title.upper()} ARTICLES ===\n\n"
                
                for i, article in enumerate(articles_list, 1):
                    total_articles += 1
                    articles_text += f"ARTICLE #{total_articles} ({category_title}):\n"
                    articles_text += f"Title: {article['title']}\n"
                    articles_text += f"Source: {article['source']}\n"
                    articles_text += f"URL: {article['url']}\n"
                    articles_text += f"Published: {article.get('published', 'Date not available')}\n"
                    articles_text += f"Description: {article.get('description', 'No description')}\n"
                    articles_text += f"Matched Keywords: {', '.join(article.get('matched_keywords', []))}\n"
                    articles_text += f"Category Score: {article.get('category_score', 0)}\n"
                    articles_text += "-" * 60 + "\n\n"
        
        if total_articles == 0:
            articles_text = "\n=== NO ARTICLES FOUND IN TARGET CATEGORIES ===\n"
            articles_text += "No articles matching true crime, stranger than fiction, or 90s/2000s culture criteria were found.\n\n"
        
        return f"""**PREMIUM WEBSITE CONTENT DISCOVERY BRIEFING**

DATE: {current_date}
TIME: {current_time}
SOURCES: WIRED, TIME, Vanity Fair, NY Post, Bloomberg, Rolling Stone, Vulture
SEARCH WINDOW: Last {self.max_age_hours} hours

**TARGET CATEGORIES:**
1. TRUE CRIME (Target: 3 stories)
2. STRANGER THAN FICTION (Target: 3 stories)  
3. 90S/2000S POP CULTURE (Target: 3 stories)

{articles_text}

**BRIEFING REQUIREMENTS:**
1. Analyze ONLY the articles listed above
2. Create three distinct sections for each category
3. For each article, provide:
   - Development potential assessment
   - Unique angle identification
   - Production viability analysis
4. If fewer than 3 articles available in any category, acknowledge this
5. Reference articles by their ARTICLE # and category

**OUTPUT FORMAT:**

EXECUTIVE SUMMARY:
Found {total_articles} articles across premium publications matching target categories.

**SECTION 1: TRUE CRIME DISCOVERIES**
[Analyze true crime articles with development focus]

**SECTION 2: STRANGER THAN FICTION STORIES**
[Analyze unusual/bizarre stories with narrative potential]

**SECTION 3: 90S/2000S POP CULTURE**
[Analyze nostalgic/anniversary content with audience appeal]

**DEVELOPMENT RECOMMENDATIONS:**
- Priority articles for immediate development
- Content gaps identified
- Additional research suggestions

**SOURCE PERFORMANCE:**
- Which premium sites delivered the most relevant content
- Category-specific source recommendations
"""

    def run_content_discovery(self):
        """Main content discovery execution"""
        print(f"Starting premium site content discovery for {datetime.now().strftime('%B %d, %Y')}")
        
        try:
            # Search all premium sites
            all_articles = self.search_all_premium_sites()
            
            if not all_articles:
                error_msg = """
CRITICAL: NO ARTICLES FOUND FROM PREMIUM SITES

Possible issues:
- RSS feeds are down or changed
- Network connectivity problems  
- Sites blocking our requests
- All content is paywalled

Recommend manual verification of RSS feed URLs.
"""
                print(error_msg)
                return error_msg
            
            # Categorize articles
            categorized = self.categorize_articles(all_articles)
            
            # Select top articles for each category
            selected = self.select_top_articles(categorized)
            
            # Generate briefing
            briefing_prompt = self.generate_briefing_prompt(selected)
            
            # Send to Claude for analysis
            message = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=8000,
                temperature=0.1,
                messages=[{"role": "user", "content": briefing_prompt}]
            )
            
            response_content = message.content[0].text
            
            # Add verification footer
            total_selected = sum(len(articles) for articles in selected.values())
            verification_footer = f"""

**SYSTEM VERIFICATION:**
- Search conducted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Premium sites searched: {len(self.target_sites)}
- Total articles collected: {len(all_articles)}
- Articles selected for analysis: {total_selected}
- Search window: {self.max_age_hours} hours
- Categories: True Crime, Stranger Than Fiction, 90s/2000s Culture

**DEVELOPMENT TEAM NOTE:**
All content sourced from premium publications. Verify subscription access
for full article review before development decisions.
"""
            
            return response_content + verification_footer
            
        except Exception as e:
            logger.error(f"Error in content discovery: {str(e)}")
            return f"Error in content discovery: {str(e)}"

    def send_email(self, briefing_content):
        """Send briefing via Gmail"""
        try:
            sender_email = os.environ.get("GMAIL_ADDRESS", "").strip()
            sender_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
            recipients = ["danny@kontentfarm.com"]
            
            current_date = datetime.now().strftime('%B %d, %Y')
            subject = f"Premium Content Discovery - {current_date} - True Crime + Pop Culture"
            
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
            
            print("Email sent successfully!")
            return True
            
        except Exception as e:
            print(f"Email error: {str(e)}")
            return False

    def run_daily_briefing(self):
        """Execute daily premium content briefing"""
        print(f"Starting premium content briefing for {datetime.now().strftime('%B %d, %Y %H:%M:%S')}")
        
        try:
            briefing = self.run_content_discovery()
            
            if "NO ARTICLES FOUND" in briefing:
                print("No content found - not sending briefing")
                print(briefing)
                return
            
            success = self.send_email(briefing)
            
            if success:
                print("Premium content briefing sent successfully!")
            else:
                print("Email delivery failed")
                
        except Exception as e:
            print(f"Critical error: {str(e)}")
            raise

if __name__ == "__main__":
    discovery_system = PremiumSiteContentDiscovery()
    discovery_system.run_daily_briefing()
