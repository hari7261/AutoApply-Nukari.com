import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, InvalidSessionIdException, WebDriverException, TimeoutException
import configparser

class NaukriAutoApply:
    def __init__(self):
        # Initialize configuration
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        self.driver = None
        self.wait = None
        self.setup_driver()
        
        # Login credentials
        self.email = self.config['NAUKRI']['email']
        
        # Job search criteria
        self.keywords = self.config['JOB_SEARCH']['keywords'].split(',')
        self.locations = self.config['JOB_SEARCH']['locations'].split(',')
        self.experience = self.config['JOB_SEARCH']['experience']
        self.salary = self.config['JOB_SEARCH']['salary']
    
    def setup_driver(self):
        """Initialize WebDriver with improved stability"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Check for headless mode
        headless = self.config['DEFAULT'].getboolean('headless', fallback=False)
        if headless:
            chrome_options.add_argument("--headless")
        
        # Check if chrome driver path is specified
        chrome_driver_path = self.config['DEFAULT'].get('chrome_driver_path', '').strip()
        
        if chrome_driver_path:
            service = Service(chrome_driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            # Use system PATH or ChromeDriverManager
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
    
    def is_session_active(self):
        """Check if the browser session is still active"""
        try:
            self.driver.current_url
            return True
        except (InvalidSessionIdException, WebDriverException):
            return False
    
    def ensure_session_active(self):
        """Ensure browser session is active, restart if needed"""
        if not self.is_session_active():
            print("Browser session lost, restarting...")
            try:
                self.driver.quit()
            except:
                pass
            self.setup_driver()
            return False
        return True
    
    def find_element_by_multiple_selectors(self, selectors, timeout=10):
        """Try multiple selectors to find an element"""
        for selector_type, selector_value in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                return element
            except TimeoutException:
                try:
                    # Fallback to just presence if clickable fails
                    element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    return element
                except TimeoutException:
                    continue
        return None
    
    def safe_click(self, element):
        """Safely click an element using multiple methods"""
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            
            # Try regular click first
            element.click()
            return True
        except Exception:
            try:
                # Try JavaScript click as fallback
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                return False
    
    def safe_send_keys(self, element, text):
        """Safely send keys to an element"""
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            
            # Clear and send keys
            element.clear()
            time.sleep(0.5)
            element.send_keys(text)
            return True
        except Exception:
            try:
                # Try JavaScript method
                self.driver.execute_script("arguments[0].value = '';", element)
                self.driver.execute_script("arguments[0].value = arguments[1];", element, text)
                return True
            except Exception:
                return False

    def login(self):
        """Login to Naukri account using Google OAuth"""
        print("Opening Naukri login page...")
        self.driver.get("https://www.naukri.com/nlogin/login")
        
        try:
            # Look for and click the "Continue with Google" button
            google_login_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Google') or contains(@class,'google') or contains(@id,'google')]|//a[contains(text(),'Google') or contains(@class,'google')]")
            ))
            print("Clicking 'Continue with Google' button...")
            google_login_button.click()
            
        except Exception:
            # Alternative: Look for Google login by different selectors
            try:
                google_login_button = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//*[contains(text(), 'Continue with Google') or contains(text(), 'Sign in with Google')]")
                ))
                print("Found Google login button, clicking...")
                google_login_button.click()
            except Exception:
                print("Could not find Google login button. Please check if the page layout has changed.")
                print("You may need to manually click the 'Continue with Google' button.")
                input("Press Enter after you've clicked the Google login button...")
        
        # Wait for Google login page to load
        print("Waiting for Google login page...")
        try:
            # Wait for Google's email input field
            email_field = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@type='email' or @id='identifierId']")
            ))
            print("Entering email address...")
            email_field.send_keys(self.email)
            
            # Click Next button
            next_button = self.driver.find_element(By.XPATH, "//button[@id='identifierNext']|//input[@id='identifierNext']")
            next_button.click()
            
            # Wait for manual password entry (since we don't store password)
            print(f"Please enter your Google password for {self.email} in the browser...")
            print("The script will continue automatically once you're logged in.")
            
        except Exception as e:
            print(f"Error during Google login process: {str(e)}")
            print("Please complete the login manually in the browser.")
        
        # Enhanced login detection with session validation
        print("Waiting for login completion...")
        login_completed = False
        max_wait_time = 300  # 5 minutes
        start_time = time.time()
        
        while not login_completed and (time.time() - start_time) < max_wait_time:
            try:
                if not self.ensure_session_active():
                    print("Session lost during login, please restart the script.")
                    return False
                
                current_url = self.driver.current_url
                page_title = self.driver.title.lower()
                
                # Check multiple indicators of successful login
                if ("naukri.com" in current_url and 
                    "login" not in current_url and 
                    "nlogin" not in current_url and
                    ("home" in current_url or "jobs" in current_url or "mynaukri" in page_title)):
                    print("Login successful! Proceeding with job search...")
                    login_completed = True
                    break
                    
                time.sleep(2)
                
            except Exception as e:
                print(f"Error checking login status: {str(e)}")
                time.sleep(2)
        
        if not login_completed:
            print("Login timeout. Please ensure you complete the login process.")
            return False
            
        # Give extra time for page to stabilize after login
        time.sleep(5)
        return True
    
    def search_jobs(self):
        """Search for jobs based on criteria"""
        if not self.ensure_session_active():
            print("Browser session not active. Please restart the script.")
            return
            
        print("Starting job search...")
        
        for keyword in self.keywords:
            for location in self.locations:
                try:
                    if not self.ensure_session_active():
                        print("Session lost during job search.")
                        return
                    
                    print(f"Searching for: {keyword.strip()} in {location.strip()}")
                    
                    # Use direct URL approach as primary method
                    keyword_encoded = keyword.strip().replace(' ', '%20').replace(',', '')
                    location_encoded = location.strip().replace(' ', '%20').replace(',', '')
                    
                    # Try multiple URL formats with date filter
                    search_urls = [
                        f"https://www.naukri.com/{keyword_encoded}-jobs-in-{location_encoded}?experience={self.experience.replace(' ', '%20')}&jobAge=1",
                        f"https://www.naukri.com/jobs?k={keyword_encoded}&l={location_encoded}&jobAge=1",
                        f"https://www.naukri.com/{keyword_encoded}-jobs?l={location_encoded}&jobAge=1"
                    ]
                    
                    success = False
                    for search_url in search_urls:
                        try:
                            print(f"Trying URL: {search_url}")
                            self.driver.get(search_url)
                            time.sleep(5)
                            
                            # Check if we got results
                            current_url = self.driver.current_url
                            page_source = self.driver.page_source.lower()
                            
                            if ("job" in current_url and 
                                ("results" in page_source or "apply" in page_source or "position" in page_source)):
                                print("Search successful via direct URL!")
                                success = True
                                break
                                
                        except Exception as e:
                            print(f"Error with URL {search_url}: {str(e)}")
                            continue
                    
                    if not success:
                        # Fallback to manual search
                        print("Direct URL failed, trying manual search...")
                        success = self.manual_search(keyword.strip(), location.strip())
                    
                    if success:
                        # Apply filters and process results
                        self.apply_filters()
                        self.process_job_listings()
                    else:
                        print(f"Could not search for {keyword} in {location}")
                    
                except Exception as e:
                    print(f"Error searching for {keyword} in {location}: {str(e)}")
                    continue
    
    def manual_search(self, keyword, location):
        """Manual search using search form"""
        try:
            # Go to main jobs page
            self.driver.get("https://www.naukri.com/")
            time.sleep(3)
            
            # Multiple selectors for search field
            search_selectors = [
                (By.ID, "qsb-keyword-sugg"),
                (By.XPATH, "//input[@placeholder='Enter keyword / designation / companies']"),
                (By.XPATH, "//input[contains(@class, 'suggestor-input')]"),
                (By.XPATH, "//input[@data-cy='keyword-input']"),
                (By.CSS_SELECTOR, "input[data-cy='keyword-input']"),
                (By.CSS_SELECTOR, ".suggestor-input"),
                (By.XPATH, "//input[contains(@id, 'keyword')]"),
                (By.XPATH, "//input[@name='qp']"),
                (By.XPATH, "//input[contains(@placeholder, 'keyword')]")
            ]
            
            search_field = self.find_element_by_multiple_selectors(search_selectors, timeout=10)
            if not search_field:
                print("Could not find search field")
                return False
            
            print("Found search field, entering keyword...")
            if not self.safe_send_keys(search_field, keyword):
                print("Could not enter keyword")
                return False
            
            time.sleep(2)
            
            # Multiple selectors for location field
            location_selectors = [
                (By.ID, "qsb-location-sugg"),
                (By.XPATH, "//input[@placeholder='Enter location']"),
                (By.XPATH, "//input[contains(@class, 'suggestor-input') and contains(@placeholder, 'location')]"),
                (By.XPATH, "//input[@data-cy='location-input']"),
                (By.CSS_SELECTOR, "input[data-cy='location-input']"),
                (By.XPATH, "//input[contains(@id, 'location')]"),
                (By.XPATH, "//input[@name='ql']"),
                (By.XPATH, "//input[contains(@placeholder, 'location')]")
            ]
            
            location_field = self.find_element_by_multiple_selectors(location_selectors, timeout=5)
            if location_field:
                print("Found location field, entering location...")
                self.safe_send_keys(location_field, location)
                time.sleep(2)
            else:
                print("Could not find location field, continuing without location filter")
            
            # Multiple selectors for search button
            search_button_selectors = [
                (By.XPATH, "//button[contains(text(),'Search')]"),
                (By.CSS_SELECTOR, "button[data-cy='search-button']"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//input[@type='submit']"),
                (By.CSS_SELECTOR, ".qsb-search-button"),
                (By.XPATH, "//button[contains(@class, 'search')]"),
                (By.XPATH, "//button[contains(@class, 'btn')]"),
                (By.CSS_SELECTOR, ".search-btn")
            ]
            
            search_button = self.find_element_by_multiple_selectors(search_button_selectors, timeout=5)
            if search_button:
                print("Found search button, clicking...")
                if self.safe_click(search_button):
                    time.sleep(5)
                    return True
                else:
                    print("Could not click search button")
            else:
                # Try pressing Enter on search field
                print("Search button not found, trying Enter key...")
                try:
                    search_field.send_keys(Keys.RETURN)
                    time.sleep(5)
                    return True
                except:
                    print("Enter key also failed")
            
            return False
            
        except Exception as e:
            print(f"Error in manual search: {str(e)}")
            return False

    def apply_filters(self):
        """Apply experience and salary filters"""
        try:
            if not self.ensure_session_active():
                return
            
            print("Attempting to apply filters...")
            time.sleep(3)
            
            # First try to apply date filter for last 24 hours
            try:
                # Multiple selectors for date posted filter
                date_selectors = [
                    (By.XPATH, "//span[contains(text(),'Date Posted')]"),
                    (By.XPATH, "//div[contains(text(),'Date Posted')]"),
                    (By.CSS_SELECTOR, "[data-cy='date-filter']"),
                    (By.XPATH, "//button[contains(@class, 'filter') and contains(text(), 'Date')]"),
                    (By.XPATH, "//div[contains(@class, 'filter') and contains(text(), 'Date')]"),
                    (By.XPATH, "//h3[contains(text(), 'Date')]"),
                    (By.XPATH, "//span[text()='Date']")
                ]
                
                date_dropdown = self.find_element_by_multiple_selectors(date_selectors, timeout=3)
                if date_dropdown:
                    if self.safe_click(date_dropdown):
                        time.sleep(2)
                        # Try to select 24 hours filter
                        date_option_selectors = [
                            "//li[contains(text(),'24 hours') or contains(text(),'Last 24 hours') or contains(text(),'Today')]",
                            "//div[contains(text(),'24 hours') or contains(text(),'Last 24 hours') or contains(text(),'Today')]",
                            "//label[contains(text(),'24 hours') or contains(text(),'Last 24 hours') or contains(text(),'Today')]"
                        ]
                        
                        date_option_found = False
                        for selector in date_option_selectors:
                            try:
                                date_options = self.driver.find_elements(By.XPATH, selector)
                                if date_options:
                                    for option in date_options:
                                        if self.safe_click(option):
                                            print("Applied 24 hours date filter")
                                            time.sleep(2)
                                            date_option_found = True
                                            break
                                if date_option_found:
                                    break
                            except:
                                continue
                        
                        if not date_option_found:
                            print("Could not find 24 hours filter option")
                else:
                    print("Date filter not found - skipping")
            except Exception as date_error:
                print(f"Error applying date filter: {str(date_error)}")
            
            # Skip other filters if they cause issues
            try:
                # Multiple selectors for experience filter
                exp_selectors = [
                    (By.XPATH, "//span[contains(text(),'Experience')]"),
                    (By.XPATH, "//div[contains(text(),'Experience')]"),
                    (By.CSS_SELECTOR, "[data-cy='experience-filter']"),
                    (By.XPATH, "//button[contains(@class, 'filter') and contains(text(), 'Experience')]"),
                    (By.XPATH, "//div[contains(@class, 'filter') and contains(text(), 'Experience')]")
                ]
                
                exp_dropdown = self.find_element_by_multiple_selectors(exp_selectors, timeout=3)
                if exp_dropdown:
                    if self.safe_click(exp_dropdown):
                        time.sleep(2)
                        try:
                            exp_option = self.driver.find_element(By.XPATH, f"//li[contains(text(),'{self.experience}')]")
                            if self.safe_click(exp_option):
                                print("Applied experience filter")
                                time.sleep(2)
                        except:
                            print("Experience filter option not found")
                else:
                    print("Experience filter not found - skipping")
                
                # Multiple selectors for salary filter
                salary_selectors = [
                    (By.XPATH, "//span[contains(text(),'Salary')]"),
                    (By.XPATH, "//div[contains(text(),'Salary')]"),
                    (By.CSS_SELECTOR, "[data-cy='salary-filter']"),
                    (By.XPATH, "//button[contains(@class, 'filter') and contains(text(), 'Salary')]"),
                    (By.XPATH, "//div[contains(@class, 'filter') and contains(text(), 'Salary')]")
                ]
                
                salary_dropdown = self.find_element_by_multiple_selectors(salary_selectors, timeout=3)
                if salary_dropdown:
                    if self.safe_click(salary_dropdown):
                        time.sleep(2)
                        try:
                            salary_option = self.driver.find_element(By.XPATH, f"//li[contains(text(),'{self.salary}')]")
                            if self.safe_click(salary_option):
                                print("Applied salary filter")
                                time.sleep(2)
                        except:
                            print("Salary filter option not found")
                else:
                    print("Salary filter not found - skipping")
                    
            except Exception as filter_error:
                print(f"Filter error (continuing anyway): {str(filter_error)}")
            
        except Exception as e:
            print(f"Error applying filters (continuing): {str(e)}")
    
    def process_job_listings(self):
        """Process job listings and apply to relevant ones"""
        if not self.ensure_session_active():
            return
            
        page = 1
        max_pages = 3  # Reduced to prevent long execution
        applied_count = 0
        
        while page <= max_pages:
            try:
                if not self.ensure_session_active():
                    print("Session lost during job processing.")
                    return
                
                print(f"Processing page {page}...")
                
                # Multiple selectors for job listings
                job_selectors = [
                    (By.XPATH, "//article[contains(@class,'jobTuple')]"),
                    (By.CSS_SELECTOR, ".jobTuple"),
                    (By.XPATH, "//div[contains(@class, 'srp-jobtuple-wrapper')]"),
                    (By.CSS_SELECTOR, ".srp-jobtuple-wrapper"),
                    (By.XPATH, "//div[contains(@class, 'result')]"),
                    (By.CSS_SELECTOR, "[data-job-id]"),
                    (By.XPATH, "//div[contains(@class, 'job-tile')]"),
                    (By.XPATH, "//div[@class='row'][.//a[contains(@class,'title')]]")
                ]
                
                job_listings = []
                for selector_type, selector_value in job_selectors:
                    try:
                        job_listings = self.driver.find_elements(selector_type, selector_value)
                        if job_listings:
                            print(f"Found jobs using selector: {selector_value}")
                            break
                    except:
                        continue
                
                if not job_listings:
                    print("No job listings found on this page")
                    break
                
                print(f"Found {len(job_listings)} job listings")
                
                for i, job in enumerate(job_listings[:10]):  # Limit to first 10 jobs per page
                    try:
                        # Scroll job into view
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", job)
                        time.sleep(1)
                        
                        job_title = "Unknown"
                        company = "Unknown"
                        
                        # Get job title and find clickable link to job details
                        job_link = None
                        
                        # Multiple selectors for job title links
                        title_link_selectors = [
                            "a.title",
                            ".title a", 
                            "[data-cy='job-title']",
                            "a[title]",
                            ".jobTupleHeader a",
                            ".row1 a",
                            "h3 a",
                            ".jobtitle a"
                        ]
                        
                        for selector in title_link_selectors:
                            try:
                                job_links = job.find_elements(By.CSS_SELECTOR, selector)
                                if job_links:
                                    job_link = job_links[0]
                                    job_title = job_link.text or job_link.get_attribute('title')
                                    if job_title and job_title != "Unknown":
                                        break
                            except:
                                continue
                        
                        # Get company name if available
                        company_selectors = [
                            ".compName",
                            ".company-name", 
                            "[data-cy='company-name']",
                            ".subTitle a",
                            ".row2 .ellipsis",
                            ".org a",
                            ".comp-name",
                            "a.comp-name"
                        ]
                        for selector in company_selectors:
                            try:
                                company_element = job.find_element(By.CSS_SELECTOR, selector)
                                company = company_element.text
                                if company and company != "Unknown":
                                    break
                            except:
                                continue
                        
                        if not job_link:
                            print(f"No clickable link found for: {job_title} at {company}")
                            continue
                            
                        # Open job in a new tab
                        print(f"Opening job details for: {job_title} at {company}")
                        
                        # Save the current window handle
                        main_window = self.driver.current_window_handle
                        
                        # Open in new tab using JavaScript
                        try:
                            self.driver.execute_script("arguments[0].setAttribute('target', '_blank');", job_link)
                            if not self.safe_click(job_link):
                                # Try to get the URL and open manually if click fails
                                job_url = job_link.get_attribute('href')
                                if job_url:
                                    self.driver.execute_script(f"window.open('{job_url}', '_blank');")
                                else:
                                    print(f"Could not open job details for: {job_title}")
                                    continue
                            
                            # Wait for new tab and switch to it
                            time.sleep(2)
                            self.wait.until(lambda d: len(d.window_handles) > 1)
                            
                            # Switch to the new tab
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            time.sleep(3)
                            
                            # Look for apply button on the job details page
                            apply_selectors = [
                                "//button[contains(text(),'Apply')]",
                                "//button[contains(text(),'Easy Apply')]",
                                "//a[contains(text(),'Apply')]",
                                "//span[contains(text(),'Apply')]",
                                "//div[contains(@class,'apply')]//button",
                                "//button[contains(@class,'apply')]",
                                "//*[@id='apply-button']",
                                "//button[@data-cy='apply-button']",
                                "//button[@id='apply-button']",
                                "//a[contains(@class,'apply')]",
                                "//div[contains(@class,'apply')]//a"
                            ]
                            
                            apply_button_found = False
                            for selector in apply_selectors:
                                try:
                                    apply_buttons = self.driver.find_elements(By.XPATH, selector)
                                    if apply_buttons:
                                        for apply_btn in apply_buttons:
                                            if apply_btn.is_displayed() and apply_btn.is_enabled():
                                                print(f"Found apply button for: {job_title}")
                                                if self.safe_click(apply_btn):
                                                    applied_count += 1
                                                    apply_button_found = True
                                                    
                                                    # Handle any follow-up confirmation
                                                    try:
                                                        time.sleep(2)
                                                        confirm_buttons = self.driver.find_elements(
                                                            By.XPATH, 
                                                            "//button[contains(text(),'Confirm') or contains(text(),'Submit') or contains(text(),'Apply')]"
                                                        )
                                                        if confirm_buttons:
                                                            for btn in confirm_buttons:
                                                                if btn.is_displayed():
                                                                    self.safe_click(btn)
                                                                    time.sleep(1)
                                                    except:
                                                        pass
                                                        
                                                    print(f"Successfully applied to: {job_title} at {company}")
                                                    time.sleep(3)
                                                    break
                                                else:
                                                    print(f"Could not click apply button for: {job_title}")
                                        if apply_button_found:
                                            break
                                except Exception:
                                    continue
                                    
                            if not apply_button_found:
                                print(f"No apply button found on the job details page for: {job_title} at {company}")
                            
                            # Close the job details tab and switch back to main window
                            self.driver.close()
                            self.driver.switch_to.window(main_window)
                            time.sleep(1)
                            
                            if applied_count >= 5:  # Limit applications per session
                                print(f"Applied to {applied_count} jobs. Stopping for now.")
                                return
                                
                        except Exception as e:
                            print(f"Error processing job details for {job_title}: {str(e)}")
                            # Make sure to return to main window
                            if len(self.driver.window_handles) > 1:
                                self.driver.close()
                                self.driver.switch_to.window(main_window)
                    
                    except Exception as e:
                        print(f"Error processing job {i+1}: {str(e)}")
                        continue
                
                # Try to go to next page
                try:
                    next_selectors = [
                        (By.XPATH, "//a[contains(@class,'fright') and contains(text(),'Next')]"),
                        (By.CSS_SELECTOR, ".pagination-next"),
                        (By.XPATH, "//a[contains(text(), 'Next')]"),
                        (By.CSS_SELECTOR, "[data-cy='next-page']"),
                        (By.XPATH, "//a[@aria-label='Next']"),
                        (By.CSS_SELECTOR, "a[aria-label='Next']")
                    ]
                    
                    next_button = self.find_element_by_multiple_selectors(next_selectors, timeout=5)
                    if next_button and next_button.is_enabled():
                        if self.safe_click(next_button):
                            page += 1
                            time.sleep(5)
                        else:
                            print("Could not click next button")
                            break
                    else:
                        print("No more pages available")
                        break
                except:
                    print("Could not find next page button")
                    break
                    
            except Exception as e:
                print(f"Error on page {page}: {str(e)}")
                break
        
        print(f"Total applications submitted: {applied_count}")
    
    def recover_from_errors(self):
        """Try to recover from common errors"""
        try:
            # Check if we need to handle alerts
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
                print("Alert accepted")
            except:
                pass
                
            # Check if we have multiple windows open
            if len(self.driver.window_handles) > 1:
                # Keep only the first window and close others
                main_window = self.driver.window_handles[0]
                for handle in self.driver.window_handles[1:]:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
                self.driver.switch_to.window(main_window)
                print("Closed extra windows")
                
            return True
        except Exception as e:
            print(f"Error during recovery: {str(e)}")
            return False
    
    def run(self):
        """Main method to run the automation"""
        try:
            if self.login():
                self.search_jobs()
            else:
                print("Login failed. Exiting...")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            self.recover_from_errors()
        finally:
            try:
                if self.driver:
                    self.driver.quit()
            except:
                pass

if __name__ == "__main__":
    automator = NaukriAutoApply()
    automator.run()
