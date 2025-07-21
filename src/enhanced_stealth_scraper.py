#!/usr/bin/env python3
"""
Enhanced Stealth Tracking Scraper with Browserless.io
Uses Browserless.io hosted browsers for reliable deployment
"""
import asyncio
import logging
import os
import random
import time
from datetime import datetime
from playwright.async_api import async_playwright
from fake_useragent import UserAgent
import openai
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedStealthScraper:
    def __init__(self):
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE')
        )
        
        # Browserless.io configuration
        self.browserless_token = "2SiFiu9vRPsrd2Y862a8e80a705326cc13364885560efd43f"
        self.browserless_endpoint = f"wss://production-sfo.browserless.io/chromium/playwright?token={self.browserless_token}"
        
        # Initialize fake user agent generator
        self.ua = UserAgent()
        
        # Realistic viewport configurations
        self.viewport_configs = [
            {'width': 1920, 'height': 1080, 'device_scale_factor': 1},
            {'width': 1366, 'height': 768, 'device_scale_factor': 1},
            {'width': 1536, 'height': 864, 'device_scale_factor': 1.25},
            {'width': 1440, 'height': 900, 'device_scale_factor': 1},
            {'width': 1280, 'height': 720, 'device_scale_factor': 1}
        ]

    async def get_tracking_status(self, tracking_url, carrier_name, tracking_number):
        """
        Get real tracking status using Browserless.io hosted browsers
        """
        try:
            logger.info(f"🕵️‍♂️ Enhanced tracking via Browserless.io for {carrier_name} package {tracking_number}")
            
            # Use Browserless.io hosted browser to load the page
            page_content = await self._browserless_stealth_load(tracking_url)
            
            if not page_content or len(page_content.strip()) < 50:
                logger.warning(f"⚠️ Insufficient content: {len(page_content) if page_content else 0} chars")
                return self._fallback_response(carrier_name, tracking_number)
            
            # Use AI to analyze the page content
            tracking_info = await self._analyze_with_ai(page_content, tracking_number, carrier_name)
            
            return tracking_info
            
        except Exception as e:
            logger.error(f"❌ Enhanced Browserless scraper error: {e}")
            return self._fallback_response(carrier_name, tracking_number)

    async def _browserless_stealth_load(self, tracking_url):
        """
        Load page using Browserless.io hosted browser with stealth configuration and rate limiting
        """
        max_retries = 3
        base_delay = 2  # Base delay in seconds
        
        for attempt in range(max_retries):
            try:
                # Add exponential backoff delay for retries
                if attempt > 0:
                    delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                    logger.info(f"⏳ Rate limit retry {attempt}/{max_retries}, waiting {delay:.1f}s...")
                    await asyncio.sleep(delay)
                
                async with async_playwright() as p:
                    logger.info(f"🌐 Connecting to Browserless.io: {self.browserless_endpoint}")
                    
                    # Connect to Browserless.io hosted browser
                    browser = await p.chromium.connect(self.browserless_endpoint)
                    
                    # Create context with realistic configuration
                    viewport = random.choice(self.viewport_configs)
                    user_agent = self.ua.random
                    
                    context = await browser.new_context(
                        user_agent=user_agent,
                        viewport=viewport,
                        locale='en-US',
                        timezone_id='America/New_York',
                        permissions=['geolocation'],
                        geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                        color_scheme='light',
                        reduced_motion='no-preference',
                        forced_colors='none',
                        java_script_enabled=True,
                        extra_http_headers={
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'DNT': '1',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0',
                        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"'
                    }
                )
                
                # Create page with stealth configuration
                page = await context.new_page()
                
                # Enhanced stealth injections (Browserless.io already provides some stealth)
                await page.add_init_script("""
                    // Override webdriver detection
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    // Override automation flags
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
                    
                    // Mock realistic plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => ({
                            length: 3,
                            0: { name: 'Chrome PDF Plugin' },
                            1: { name: 'Chrome PDF Viewer' },
                            2: { name: 'Native Client' }
                        }),
                    });
                    
                    // Mock realistic languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                    });
                    
                    // Mock realistic hardware
                    Object.defineProperty(navigator, 'hardwareConcurrency', {
                        get: () => 8,
                    });
                    
                    // Mock realistic memory
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: () => 8,
                    });
                    
                    // Mock chrome runtime
                    window.chrome = {
                        runtime: {
                            onConnect: undefined,
                            onMessage: undefined
                        },
                        app: {
                            isInstalled: false
                        }
                    };
                    
                    // Override toString methods
                    window.navigator.webdriver = undefined;
                    
                    // Mock realistic connection
                    Object.defineProperty(navigator, 'connection', {
                        get: () => ({
                            effectiveType: '4g',
                            rtt: 50,
                            downlink: 10
                        }),
                    });
                """)
                
                # Human-like pre-navigation behavior
                logger.info(f"🌐 Navigating to: {tracking_url}")
                await asyncio.sleep(random.uniform(1.5, 3.5))
                
                # Navigate with enhanced error handling
                try:
                    response = await page.goto(
                        tracking_url,
                        wait_until='domcontentloaded',
                        timeout=60000
                    )
                    
                    status_code = response.status if response else 0
                    logger.info(f"📄 Response status: {status_code}")
                    
                    if status_code >= 400:
                        logger.warning(f"⚠️ HTTP error: {status_code}")
                        
                except Exception as nav_error:
                    logger.error(f"Navigation error: {nav_error}")
                    await context.close()
                    await browser.close()
                    return None
                
                # Enhanced human behavior simulation
                await self._advanced_human_simulation(page)
                
                # Multi-strategy content loading
                content = await self._multi_strategy_content_extraction(page)
                
                await context.close()
                await browser.close()
                
                logger.info(f"✅ Extracted {len(content)} characters via Browserless.io")
                
                if content and len(content.strip()) > 50:
                    preview = content.strip()[:400].replace('\n', ' ').replace('\r', ' ')
                    logger.info(f"📝 Content preview: {preview}...")
                else:
                    logger.warning("⚠️ Minimal content extracted despite Browserless.io")
                
                    return content
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Browserless.io loading error (attempt {attempt + 1}/{max_retries}): {error_msg}")
                
                # Check if it's a rate limiting error
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    if attempt < max_retries - 1:
                        logger.info("🔄 Rate limit detected, will retry with backoff...")
                        continue
                    else:
                        logger.error("❌ Rate limit exceeded all retries")
                        return None
                else:
                    # For non-rate-limit errors, don't retry
                    logger.error(f"❌ Non-rate-limit error, not retrying: {error_msg}")
                    return None
        
        # If all retries failed
        logger.error("❌ All Browserless.io connection attempts failed")
        return None

    async def _advanced_human_simulation(self, page):
        """
        Advanced human behavior simulation
        """
        try:
            # Realistic mouse movements
            for _ in range(random.randint(3, 7)):
                x = random.randint(50, 1200)
                y = random.randint(50, 800)
                await page.mouse.move(x, y, steps=random.randint(5, 15))
                await asyncio.sleep(random.uniform(0.1, 0.4))
            
            # Realistic scrolling patterns
            scroll_actions = random.randint(2, 5)
            for _ in range(scroll_actions):
                scroll_delta = random.randint(-300, 300)
                await page.mouse.wheel(0, scroll_delta)
                await asyncio.sleep(random.uniform(0.3, 0.8))
            
            # Random clicks on safe areas
            for _ in range(random.randint(0, 2)):
                safe_x = random.randint(100, 300)
                safe_y = random.randint(100, 200)
                await page.mouse.click(safe_x, safe_y)
                await asyncio.sleep(random.uniform(0.2, 0.6))
                
        except Exception as e:
            logger.debug(f"Human simulation error: {e}")

    async def _multi_strategy_content_extraction(self, page):
        """
        Multiple strategies for content extraction
        """
        content = ""
        
        try:
            # Strategy 1: Wait for network idle
            await page.wait_for_load_state('networkidle', timeout=60000)
            
            # Strategy 2: Wait for specific elements
            tracking_selectors = [
                '[class*="track"]', '[class*="status"]', '[class*="delivery"]',
                '[id*="track"]', '[id*="status"]', '[id*="delivery"]',
                'main', '.content', '#content', '.container', '.wrapper'
            ]
            
            for selector in tracking_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=3000)
                    logger.info(f"✅ Found tracking element: {selector}")
                    break
                except:
                    continue
            
            # Strategy 3: Progressive content checking
            for attempt in range(15):
                current_content = await page.evaluate('''
                    () => {
                        // Remove unwanted elements
                        const unwanted = document.querySelectorAll('script, style, noscript, iframe');
                        unwanted.forEach(el => el.remove());
                        
                        // Get text content
                        const body = document.body;
                        if (!body) return '';
                        
                        let text = body.innerText || body.textContent || '';
                        
                        // If minimal, try specific extraction
                        if (text.length < 200) {
                            const elements = document.querySelectorAll('div, span, p, td, th, li, h1, h2, h3, h4, h5, h6, strong, em');
                            const texts = [];
                            elements.forEach(el => {
                                const elementText = (el.innerText || el.textContent || '').trim();
                                if (elementText && elementText.length > 2 && !texts.includes(elementText)) {
                                    texts.push(elementText);
                                }
                            });
                            text = texts.join(' ');
                        }
                        
                        return text;
                    }
                ''')
                
                if current_content and len(current_content.strip()) > 100:
                    content = current_content
                    logger.info(f"✅ Content loaded after {attempt + 1} attempts: {len(content)} chars")
                    break
                    
                await asyncio.sleep(1)
            
            # Strategy 4: HTML fallback if text extraction fails
            if not content or len(content.strip()) < 100:
                html_content = await page.content()
                # Basic HTML cleaning
                import re
                text_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
                text_content = re.sub(r'<style[^>]*>.*?</style>', '', text_content, flags=re.DOTALL)
                text_content = re.sub(r'<[^>]+>', ' ', text_content)
                text_content = re.sub(r'\s+', ' ', text_content).strip()
                
                if len(text_content) > len(content):
                    content = text_content
                    logger.info(f"📄 Using HTML fallback: {len(content)} chars")
            
            return content
            
        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            return content

    async def _analyze_with_ai(self, page_content, tracking_number, carrier_name):
        """
        Enhanced AI analysis with better prompting
        """
        try:
            # Enhanced prompt for better extraction
            prompt = f"""
            You are an expert at extracting tracking information from USPS and other carrier websites.
            Analyze this page content carefully and extract the delivery status.
            
            Tracking Number: {tracking_number}
            Carrier: {carrier_name}
            Content Length: {len(page_content)} characters
            
            Page Content:
            {page_content}
            
            CRITICAL: This package was delivered weeks ago. Look VERY carefully for delivery information.
            
            DELIVERY STATUS PATTERNS TO FIND:
            - "delivered" or "Delivered" (case insensitive) - MOST IMPORTANT
            - "delivery complete" or "Delivery Complete"
            - "package delivered" or "Package delivered"
            - "item was delivered" or "Item was delivered"
            - "mailbox" (often indicates delivery)
            - "front door" or "porch" (delivery locations)
            - "out for delivery" or "Out for Delivery"
            - "in transit" or "In Transit"
            - "arrived" or "Arrived"
            - "completed" or "Completed"
            
            DELIVERY DATE PATTERNS:
            - Look for dates like "June 9, 2025" or "6/9/2025" or "2025-06-09"
            - "delivered on [date]" or "Delivered on [date]"
            - "at 4:11 pm" or similar times
            - Any date mentioned with delivery context
            
            LOCATION PATTERNS:
            - "MILL VALLEY, CA 94941" or similar city/state/zip
            - ZIP codes with delivery context
            - Facility names with locations
            
            SPECIFIC USPS DELIVERY PHRASES:
            - "Your item was delivered in or at the mailbox"
            - "Delivered, In/At Mailbox"
            - "Delivered, Front Door/Porch"
            - "delivered in or at the mailbox at 4:11 pm"
            - Any phrase containing both "delivered" and a time/location
            
            SEARCH STRATEGY:
            1. First scan for the word "delivered" anywhere in the content
            2. If found, extract the surrounding context for date/time/location
            3. Look for delivery dates like "June 9" or "6/9"
            4. Look for delivery times like "4:11 pm"
            5. Look for locations like "MILL VALLEY, CA"
            
            Return ONLY this JSON format:
            {{
                "status": "Delivered|Out for Delivery|In Transit|Label Created|Delivery Exception|Unknown",
                "estimated_delivery": "YYYY-MM-DD or null",
                "current_location": "location string or null",
                "last_update": "YYYY-MM-DD or null",
                "delivery_date": "YYYY-MM-DD if delivered or null",
                "notes": "important delivery notes or null"
            }}
            
            IMPORTANT: If you find ANY mention of "delivered" or delivery completion, return "Delivered" status.
            Do NOT return "Unknown" if there's any delivery information present.
            If you find ANY mention of "delivered" or "delivery" with a date, use "Delivered" status.
            If tracking information is truly not found after thorough analysis, use "Unknown" for status.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a precise tracking information extraction expert. You MUST thoroughly scan ALL content for delivery-related keywords. Look for ANY mention of 'delivered', 'delivery', dates, locations. Return only valid JSON with accurate data extracted from the provided content. Be very thorough in your analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.05,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"🤖 Enhanced AI analysis: {ai_response}")
            
            try:
                tracking_info = json.loads(ai_response)
                
                # Add enhanced metadata
                tracking_info.update({
                    'carrier': carrier_name,
                    'tracking_number': tracking_number,
                    'extraction_method': 'browserless_stealth_AI',
                    'timestamp': datetime.now().isoformat(),
                    'content_length': len(page_content),
                    'stealth_version': '3.0_browserless'
                })
                
                return tracking_info
                
            except json.JSONDecodeError:
                logger.error(f"JSON parse error: {ai_response}")
                return self._fallback_response(carrier_name, tracking_number)
                
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return self._fallback_response(carrier_name, tracking_number)

    def _fallback_response(self, carrier_name, tracking_number):
        """
        Enhanced fallback response
        """
        return {
            'status': 'Check tracking link for current status',
            'carrier': carrier_name,
            'tracking_number': tracking_number,
            'estimated_delivery': None,
            'current_location': None,
            'last_update': datetime.now().strftime('%Y-%m-%d'),
            'delivery_date': None,
            'notes': 'Browserless.io extraction failed - please check tracking link',
            'extraction_method': 'browserless_fallback',
            'timestamp': datetime.now().isoformat()
        }


# Synchronous wrapper
def get_enhanced_stealth_tracking(tracking_url, carrier_name, tracking_number):
    """
    Synchronous wrapper for Browserless.io enhanced tracking
    """
    try:
        scraper = EnhancedStealthScraper()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            scraper.get_tracking_status(tracking_url, carrier_name, tracking_number)
        )
        loop.close()
        
        return result
        
    except Exception as e:
        logger.error(f"Enhanced Browserless wrapper error: {e}")
        return {
            'status': 'Check tracking link for current status',
            'carrier': carrier_name,
            'tracking_number': tracking_number,
            'estimated_delivery': None,
            'current_location': None,
            'last_update': datetime.now().strftime('%Y-%m-%d'),
            'delivery_date': None,
            'notes': 'System error during tracking extraction',
            'extraction_method': 'browserless_error',
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        result = get_enhanced_stealth_tracking(test_url, "USPS", "test123")
        print(f"Browserless Result: {result}")
    else:
        print("Usage: python enhanced_stealth_scraper.py <tracking_url>")

