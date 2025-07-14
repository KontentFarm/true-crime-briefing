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

    def debug_date_handling(self):
        """Debug current date handling"""
        print("🔍 DEBUG: Date Handling")
        now = datetime.now()
        print(f"Current datetime: {now}")
        print(f"Formatted date: {now.strftime('%B %d, %Y')}")
        print(f"ISO date: {now.strftime('%Y-%m-%d')}")
        print(f"30 days ago: {(now - timedelta(days=30)).strftime('%Y-%m-%d')}")
        print(f"7 days ago: {(now - timedelta(days=7)).strftime('%Y-%m-%d')}")
        return now

    def debug_news_api_connection(self):
        """Debug News API connectivity and responses"""
        print("\n🔍 DEBUG: News API Connection")
        
        api_key = os.getenv('NEWS_API_KEY')
        print(f"NEWS_API_KEY present: {'Yes' if api_key else 'No'}")
        
        if not api_key:
            print("❌ No NEWS_API_KEY found - this explains empty results")
            return []
            
        # Test simple query
        test_query = "murder"
        test_url = "https://newsapi.org/v2/everything"
        test_params = {
            'q': test_query,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 5,
            'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'apiKey': api_key
        }
        
        print(f"Testing query: {test_query}")
        print(f"API URL: {test_url}")
        print(f"Parameters: {test_params}")
        
        try:
            response = requests.get(test_url, params=test_params, timeout=10)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                total_results = data.get('totalResults', 0)
                articles = data.get('articles', [])
                
                print(f"Total results reported: {total_results}")
                print(f"Articles returned: {len(articles)}")
                
                if articles:
                    print("\n📰 Sample article:")
                    sample = articles[0]
                    print(f"Title: {sample.get('title', 'No title')}")
                    print(f"Source: {sample.get('source', {}).get('name', 'No source')}")
                    print(f"Published: {sample.get('publishedAt', 'No date')}")
                    print(f"URL: {sample.get('url', 'No URL')}")
                    print(f"Description: {sample.get('description', 'No description')[:100]}...")
                else:
                    print("❌ No articles returned despite positive status")
                    
                return articles
            else:
                print(f"❌ API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Raw response: {response.text[:200]}...")
                return []
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return []

    def debug_google_news_rss(self):
        """Debug Google News RSS as fallback"""
        print("\n🔍 DEBUG: Google News RSS")
        
        test_query = "crime+investigation"
        test_url = f"https://news.google.com/rss/search?q={test_query}&hl=en-US&gl=US&ceid=US:en"
        
        print(f"Testing Google News RSS: {test_url}")
        
        try:
            response = requests.get(test_url, timeout=10)
            print(f"Response status: {response.status_code}")
            print(f"Content length: {len(response.content)}")
            
            if response.status_code == 200:
                # Try basic XML parsing
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(response.content)
                    items = root.findall('.//item')
                    print(f"RSS items found: {len(items)}")
                    
                    if items:
                        sample = items[0]
                        title = sample.find('title')
                        link = sample.find('link')
                        pub_date = sample.find('pubDate')
                        
                        print("\n📰 Sample RSS item:")
                        print(f"Title: {title.text if title is not None else 'No title'}")
                        print(f"Link: {link.text if link is not None else 'No link'}")
                        print(f"Date: {pub_date.text if pub_date is not None else 'No date'}")
                        
                        return True
                    else:
                        print("❌ No items found in RSS feed")
                        return False
                        
                except ET.ParseError as e:
                    print(f"❌ XML parsing error: {e}")
                    print(f"Raw content sample: {response.content[:200]}")
                    return False
            else:
                print(f"❌ RSS Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ RSS connection error: {str(e)}")
            return False

    def debug_article_collection(self):
        """Debug the full article collection process"""
        print("\n🔍 DEBUG: Full Article Collection Process")
        
        # Test News API
        news_articles = []
        if os.getenv('NEWS_API_KEY'):
            print("Testing News API...")
            news_articles = self.debug_news_api_connection()
        else:
            print("Skipping News API (no key)")
            
        # Test Google RSS
        print("\nTesting Google RSS...")
        rss_working = self.debug_google_news_rss()
        
        # Simulate the real collection process
        print("\n🔍 Running actual search_comprehensive_news_sources()...")
        try:
            all_articles = self.search_comprehensive_news_sources()
            print(f"✅ Real search returned: {len(all_articles)} articles")
            
            if all_articles:
                print("\n📰 First 3 real articles:")
                for i, article in enumerate(all_articles[:3]):
                    print(f"\n{i+1}. {article.get('title', 'No title')}")
                    print(f"   Source: {article.get('source', 'No source')}")
                    print(f"   URL: {article.get('url', 'No URL')}")
                    print(f"   Published: {article.get('published', 'No date')}")
            else:
                print("❌ No articles collected - this explains hallucination problem!")
                
            return all_articles
            
        except Exception as e:
            print(f"❌ Error in article collection: {str(e)}")
            return []

    def debug_claude_prompt(self, articles):
        """Debug what prompt is being sent to Claude"""
        print("\n🔍 DEBUG: Claude Prompt Generation")
        
        # Get journalist spotlight
        today_journalist = self.get_daily_journalist_spotlight()
        journalist_spotlight = self.format_journalist_spotlight(today_journalist)
        
        print(f"Today's journalist: {today_journalist['name']}")
        print(f"Articles to analyze: {len(articles)}")
        
        # Generate the prompt
        prompt = self.get_enhanced_research_prompt(articles, journalist_spotlight)
        
        print(f"\n📝 Prompt length: {len(prompt)} characters")
        lines_with_articles = [line for line in prompt.split('\n') if 'VERIFIED REAL ARTICLES' in line]
        print(f"Articles section length: {len(lines_with_articles)}")
        
        # Check if articles are actually in the prompt
        if articles:
            print(f"✅ Articles found in data: {len(articles)}")
            if "VERIFIED REAL ARTICLES FOUND" in prompt:
                print("✅ Articles section exists in prompt")
            else:
                print("❌ Articles section missing from prompt")
        else:
            print("❌ No articles to include in prompt - MAJOR ISSUE")
            
        print("\n📝 First 500 characters of prompt:")
        print(prompt[:500])
        print("\n...")
        
        return prompt

    def debug_claude_response(self, prompt):
        """Send a test prompt to Claude and analyze response"""
        print("\n🔍 DEBUG: Claude Response Analysis")
        
        # Add extra anti-hallucination instructions
        debug_prompt = f"""
CRITICAL DEBUG MODE: You are in anti-hallucination testing mode.

ABSOLUTE REQUIREMENTS:
1. If NO real articles are provided, respond with "NO VERIFIED ARTICLES AVAILABLE FOR ANALYSIS"
2. NEVER create fake URLs, dates, or article details
3. If articles list is empty, acknowledge this limitation
4. Today's date is: {datetime.now().strftime('%Y-%m-%d')}
5. Do NOT create articles with future dates

{prompt}

FINAL REMINDER: If the article list above is empty or contains no valid articles, you MUST respond with a limitation disclosure instead of creating fake articles.
"""
        
        try:
            print("Sending debug prompt to Claude...")
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,  # Reduced for debugging
                temperature=0.0,  # Zero temperature for debugging
                messages=[
                    {
                        "role": "user", 
                        "content": debug_prompt
                    }
                ]
            )
            
            response = message.content[0].text
            print(f"✅ Claude response received: {len(response)} characters")
            
            # Check for hallucination indicators
            print("\n🔍 Checking for hallucination indicators:")
            
            # Check for future dates
            import re
            future_dates = re.findall(r'July \d+, 2025|2025-07-\d+', response)
            if future_dates:
                print(f"❌ FUTURE DATES DETECTED: {future_dates}")
            else:
                print("✅ No future dates found")
                
            # Check for fake verification claims
            if "VERIFIED FROM SOURCE ARTICLE" in response and not any("http" in str(article.get('url', '')) for article in [] if hasattr(article, 'get')):
                print("❌ FAKE VERIFICATION CLAIMS DETECTED")
            else:
                print("✅ No fake verification claims")
                
            # Check for limitation acknowledgment
            if "NO VERIFIED ARTICLES" in response or "limitation" in response.lower():
                print("✅ Limitation properly acknowledged")
            else:
                print("❌ No limitation acknowledgment")
                
            print("\n📝 First 300 characters of response:")
            print(response[:300])
            
            return response
            
        except Exception as e:
            print(f"❌ Claude API error: {str(e)}")
            return None

    def run_full_debug(self):
        """Run complete debugging sequence"""
        print("🚀 STARTING FULL DEBUG SEQUENCE")
        print("=" * 50)
        
        # 1. Debug date handling
        current_date = self.debug_date_handling()
        
        # 2. Debug article collection
        articles = self.debug_article_collection()
        
        # 3. Debug prompt generation
        prompt = self.debug_claude_prompt(articles)
        
        # 4. Debug Claude response
        response = self.debug_claude_response(prompt)
        
        print("\n" + "=" * 50)
        print("🎯 DEBUG SUMMARY:")
        print(f"Date handling: ✅ Working")
        print(f"Articles collected: {len(articles) if articles else 0}")
        print(f"Prompt generated: {'✅ Yes' if prompt else '❌ No'}")
        print(f"Claude response: {'✅ Yes' if response else '❌ No'}")
        
        if len(articles) == 0:
            print("\n🚨 ROOT CAUSE: No articles being collected")
            print("SOLUTIONS:")
            print("1. Check NEWS_API_KEY environment variable")
            print("2. Verify News API account status/credits")
            print("3. Test Google RSS connectivity")
            print("4. Implement better fallback handling")
        
        return {
            'articles_count': len(articles) if articles else 0,
            'prompt_length': len(prompt) if prompt else 0,
            'response_length': len(response) if response else 0,
            'has_future_dates': bool(response and ('July' in response and '2025' in response)),
            'articles': articles[:3] if articles else []  # Sample articles for inspection
        }

    # Include all the original methods for completeness...
    def _build_journalist_database(self):
        """Build comprehensive database of nationally recognized true crime/pop culture journalists"""
        return {
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
            'death row appeal new evidence'
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
                    'pageSize': 10,
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
            'crime+investigation', 'murder+case', 'cold+case+solved'
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

    def get_enhanced_research_prompt(self, real_articles, journalist_spotlight):
        """Generate anti-hallucination research prompt with real article context and journalist spotlight"""
        from datetime import datetime
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Create article context with actual URLs and sources
        articles_context = ""
        if real_articles:
            articles_context = f"\n**VERIFIED REAL ARTICLES FOUND ({len(real_articles)} total):**\n\n"
            for i, article in enumerate(real_articles[:10]):  # Limit to first 10 for context
                articles_context += f"{i+1}. \"{article['title']}\"\n"
                articles_context += f"   Source: {article['source']}\n"
                articles_context += f"   URL: {article['url']}\n"
                articles_context += f"   Published: {article['published']}\n"
                if article.get('description'):
                    articles_context += f"   Description: {article['description'][:150]}...\n"
                articles_context += "\n"
        else:
            articles_context = "\n**NO VERIFIED ARTICLES FOUND**\n"
        
        return f"""
**CRITICAL ANTI-HALLUCINATION INSTRUCTIONS:**
TODAY'S DATE: {current_date}
NEVER create articles with future dates or fake URLs.

You are analyzing ONLY real, verified news articles that have been provided to you. You must NEVER create, invent, or imagine any cases, events, or details.

{articles_context}

{journalist_spotlight}

**MANDATORY RESPONSE PROTOCOL:**
- If NO verified articles are provided above, respond with "INSUFFICIENT VERIFIED ARTICLES FOR ANALYSIS"
- If fewer than 3 articles available, state this limitation clearly
- NEVER create fake URLs, dates, or case details
- All details must be directly from provided articles only

**REQUIRED OUTPUT FORMAT:**
**EXECUTIVE SUMMARY:**
[Honest assessment of available verified content]

[Only proceed with case analysis if verified articles exist above]
        """

if __name__ == "__main__":
    print("🔧 RUNNING DEBUG MODE")
    briefing_system = TrueCrimeBriefingGenerator()
    debug_results = briefing_system.run_full_debug()
    print(f"\n🎯 Debug completed: {debug_results}")
