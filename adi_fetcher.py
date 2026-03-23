"""Helpers to fetch PDFs from the internal ADI site.
        # Try to open the folder tree. Prefer clicking the label/checkbox for
        # "01. Ufficio Tecnico - Disegni" if present (uses famid or label text).
        try:
            clicked = False
            # try by label text first (robust if text matches)
            try:
                lbl = driver.find_element(By.XPATH, "//label[contains(normalize-space(.), 'Ufficio Tecnico - Disegni')]")
                lbl.click(); clicked = True
            except Exception:
                pass

            # try by checkbox with famid or value attribute
            if not clicked:
                el = None
                try:
                    el = driver.find_element(By.CSS_SELECTOR, "input.res-chk[famid='1134']")
                except Exception:
                    try:
                        el = driver.find_element(By.CSS_SELECTOR, "input.res-chk[value='1134']")
                    except Exception:
                        el = None
                if el:
                    # clickable element might be the checkbox or the label
                    try:
                        el.click(); clicked = True
                    except Exception:
                        try:
                            driver.execute_script('arguments[0].click();', el); clicked = True
                        except Exception:
                            clicked = False

            if clicked:
                time.sleep(0.6)
        except Exception:
            # ignore if not found
            pass

        # Optionally click the child section '01 codice a disegno' if present
        try:
            try:
                sec = driver.find_element(By.XPATH, "//label[contains(normalize-space(.), '01 codice a disegno') or contains(normalize-space(.), '01. Ufficio Tecnico - Disegni')]")
                sec.click()
                time.sleep(0.6)
            except Exception:
                # fallback: look for any label containing '01' and 'diseg' as heuristics
                sec = driver.find_element(By.XPATH, "//label[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '01') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'diseg')]")
                sec.click(); time.sleep(0.6)
        except Exception:
            pass
  pdf_bytes = fetch_pdf_via_selenium(username, password, search_code)

"""
import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_pdf_via_selenium(username: str, password: str, search_code: str, headless=True, timeout=30, chrome_path: str = None, browser: str = 'chrome', browser_path: str = None, driver_path: str = None):
    """Try to log into the ADI site and return bytes of a found PDF for search_code.

    Returns bytes of the PDF on success, or raises RuntimeError on failure.
    """
    try:
        from selenium import webdriver
    except Exception as e:
        raise RuntimeError('Selenium not installed: ' + str(e))

    # choose driver manager based on browser
    try:
        if browser and browser.lower().startswith('edge'):
            from selenium.webdriver.edge.service import Service as EdgeService
            # webdriver-manager optional for online installs
            try:
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
            except Exception:
                EdgeChromiumDriverManager = None
        else:
            from selenium.webdriver.chrome.service import Service as ChromeService
            try:
                from webdriver_manager.chrome import ChromeDriverManager
            except Exception:
                ChromeDriverManager = None
    except Exception as e:
        raise

    login_url = 'http://172.16.90.4:8080/adiJed/ui/login/page.jsp'

    # options per browser
    if browser and browser.lower().startswith('edge'):
        try:
            options = webdriver.EdgeOptions()
        except Exception:
            options = webdriver.ChromeOptions()
    else:
        options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # allow explicit chrome binary path via argument or CHROME_PATH env var
    import os
    # allow explicit browser binary path via argument or env var
    if not browser_path:
        if browser and browser.lower().startswith('edge'):
            browser_path = os.environ.get('EDGE_PATH')
        else:
            browser_path = os.environ.get('CHROME_PATH')
    if browser_path:
        try:
            options.binary_location = browser_path
        except Exception:
            pass

    # instantiate driver depending on chosen browser, with debug output
    try:
        print('[adi_fetcher] DEBUG: browser=', browser, ' browser_path=', browser_path, ' driver_path_arg=', driver_path)
        used_driver_path = None
        if browser and browser.lower().startswith('edge'):
            # Edge: if driver_path provided, use it; else try webdriver_manager if available
            if driver_path:
                used_driver_path = driver_path
            elif EdgeChromiumDriverManager is not None:
                used_driver_path = EdgeChromiumDriverManager().install()
            else:
                used_driver_path = None

            print('[adi_fetcher] DEBUG: Edge driver path chosen=', used_driver_path)
            if used_driver_path:
                service = EdgeService(used_driver_path)
                driver = webdriver.Edge(service=service, options=options)
            else:
                raise RuntimeError('No Edge driver available (provide driver_path or enable internet for webdriver_manager)')
        else:
            # Chrome
            if driver_path:
                used_driver_path = driver_path
            elif 'ChromeDriverManager' in globals() and ChromeDriverManager is not None:
                used_driver_path = ChromeDriverManager().install()
            else:
                used_driver_path = None

            print('[adi_fetcher] DEBUG: Chrome driver path chosen=', used_driver_path)
            if used_driver_path:
                service = ChromeService(used_driver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                raise RuntimeError('No Chrome driver available (provide driver_path or enable internet for webdriver_manager)')
        print('[adi_fetcher] DEBUG: webdriver instantiated successfully')
    except Exception as e:
        # raise a clearer error including debug hints
        msg = f'WebDriver start failed: browser={browser}, browser_path={browser_path}, driver_path={driver_path}, error={e}'
        print('[adi_fetcher] ERROR:', msg)
        raise RuntimeError(msg) from e

    try:
        driver.set_page_load_timeout(timeout)
        driver.get(login_url)

        wait = WebDriverWait(driver, 15)
        # Based on the HTML you provided, the login form uses name="UN" and name="PW"
        # and the form is submitted via document.getElementById('loginForm').submit();
        try:
            user_el = wait.until(EC.presence_of_element_located((By.NAME, 'UN')))
            pass_el = driver.find_element(By.NAME, 'PW')
        except Exception:
            # fallback to other common selectors
            try:
                user_el = driver.find_element(By.NAME, 'username')
                pass_el = driver.find_element(By.NAME, 'password')
            except Exception:
                # last resort: try generic name attributes
                user_el = driver.find_element(By.CSS_SELECTOR, 'input[type=text]')
                pass_el = driver.find_element(By.CSS_SELECTOR, 'input[type=password]')

        # Enter credentials
        user_el.clear(); user_el.send_keys(username)
        pass_el.clear(); pass_el.send_keys(password)

        # Submit form via JS call to loginForm if present, else submit element
        try:
            driver.execute_script("document.getElementById('loginForm').submit();")
        except Exception:
            try:
                pass_el.submit()
            except Exception:
                # fallback: press Enter
                pass_el.send_keys('\n')

        # Wait for post-login page to load (this may need adjustment)
        time.sleep(2)

        # After login, navigate to search or click 'Ricerca' button
        # These selectors are placeholders and need to be adapted to the real UI
        # Try the specific toolbar button with id 'query' (provided HTML)
        try:
            ric_el = wait.until(EC.element_to_be_clickable((By.ID, 'query')))
            ric_el.click()
        except Exception:
            # fallback: try a generic button containing 'Ricerca' or 'Search'
            try:
                ric_el = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Ricerca') or contains(., 'Search') or contains(., 'Ricerche')]")))
                ric_el.click()
            except Exception:
                # if there's a menu or direct link, the user may need to customize here
                pass

        time.sleep(1)

        # Drill down into folder UTM_ufficio tecnico meccanico and select section '01 codice a disegno'
        # These steps are highly site-specific; we try generic approaches but may fail.
        try:
            # Example: expand folder by visible link text
            folder = driver.find_element(By.XPATH, "//span[contains(., 'UTM_ufficio tecnico meccanico')]")
            folder.click()
            time.sleep(0.6)
        except Exception:
            # ignore if not found
            pass

        try:
            section = driver.find_element(By.XPATH, "//span[contains(., '01 codice a disegno') or contains(., '01 codice')]")
            section.click()
            time.sleep(0.6)
        except Exception:
            pass

        # Now perform a search for search_code in the 'Codice Disegno' input (id F1008 / name vlF1008)
        try:
            from selenium.webdriver.common.keys import Keys
            search_input = None
            try:
                search_input = driver.find_element(By.ID, 'F1008')
            except Exception:
                try:
                    search_input = driver.find_element(By.NAME, 'vlF1008')
                except Exception:
                    pass

            if search_input is None:
                # fallback: generic search inputs
                try:
                    search_input = driver.find_element(By.XPATH, "//input[contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'f1008') or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'vf1008')]")
                except Exception:
                    search_input = None

            if search_input is not None:
                search_input.clear(); search_input.send_keys(search_code)
                # try pressing Enter to submit
                try:
                    search_input.send_keys(Keys.ENTER)
                except Exception:
                    try:
                        search_input.submit()
                    except Exception:
                        pass
            else:
                # as last resort try previous heuristics
                try:
                    s2 = driver.find_element(By.XPATH, "//input[contains(@id,'search') or contains(@name,'search') or contains(@id,'cod') or contains(@name,'cod')]")
                    s2.clear(); s2.send_keys(search_code); s2.send_keys(Keys.ENTER)
                except Exception:
                    pass
        except Exception:
            pass

        # Wait briefly for results
        time.sleep(2)
        # Try to find a document result element with class 'document-value' containing the desired section
        pdf_link = None
        pdf_handle = None

        try:
            # prefer elements with class document-value and title/text matching
            candidates = driver.find_elements(By.CSS_SELECTOR, '.document-value')
            target_text = search_code.strip().lower()
            found_elem = None
            for el in candidates:
                title = (el.get_attribute('title') or '').strip().lower()
                text = (el.text or '').strip().lower()
                if target_text and (target_text in title or target_text in text):
                    found_elem = el
                    break
            # if not found by exact match, fallback to any document-value
            if not found_elem and candidates:
                found_elem = candidates[0]

            if found_elem:
                try:
                    driver.execute_script('arguments[0].scrollIntoView(true);', found_elem)
                except Exception:
                    pass
                try:
                    found_elem.click()
                except Exception:
                    try:
                        driver.execute_script('arguments[0].click();', found_elem)
                    except Exception:
                        pass

                # Wait a bit for any new tab or pdf link to appear
                time.sleep(1.2)

                # If clicking opened a new window/tab, switch and get its URL
                handles = driver.window_handles
                if len(handles) > 1:
                    original = driver.current_window_handle
                    for h in handles:
                        if h != original:
                            pdf_handle = h
                            break
                    if pdf_handle:
                        driver.switch_to.window(pdf_handle)
                        cur = driver.current_url
                        if cur and cur.lower().endswith('.pdf'):
                            pdf_link = cur
                        # if content is a PDF embedded, we'll still try to download by URL
                        driver.switch_to.window(original)

            # If still no pdf_link, try to find anchor with .pdf in href
            if not pdf_link:
                anchors = driver.find_elements(By.XPATH, "//a[contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'.pdf')]")
                if anchors:
                    pdf_link = anchors[0].get_attribute('href')

            # If still not found, try iframe/embed src
            if not pdf_link:
                frames = driver.find_elements(By.XPATH, "//iframe|//embed")
                for f in frames:
                    src = f.get_attribute('src')
                    if src and '.pdf' in src.lower():
                        pdf_link = src
                        break

            if not pdf_link:
                raise RuntimeError('Non ho trovato un link PDF automaticamente; potrebbe essere necessario adattare i selettori o controllare manualmente.')

            # Build a requests session with cookies from Selenium to download the PDF
            sess = requests.Session()
            for c in driver.get_cookies():
                sess.cookies.set(c['name'], c['value'], domain=c.get('domain'))

            resp = sess.get(pdf_link, timeout=30)
            if resp.status_code != 200 or 'application/pdf' not in resp.headers.get('content-type',''):
                # sometimes server delivers with different content-type; allow if response is bytes and small check
                if resp.status_code != 200:
                    raise RuntimeError('Download PDF fallito, status: ' + str(resp.status_code))
            return resp.content
        except Exception as e:
            raise

    finally:
        try:
            driver.quit()
        except Exception:
            pass
