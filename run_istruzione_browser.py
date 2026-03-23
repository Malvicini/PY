#!/usr/bin/env python3
"""Standalone runner converted from Selenium IDE output.

Usage:
  python run_istruzione_browser.py [--browser edge|chrome] [--driver-path PATH] [--username USER] [--password PASS] [--code CODE]

If `--driver-path` is provided, the script will try to use that executable for the browser driver.
"""
import argparse
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import tempfile
import os

def make_driver(browser='chrome', driver_path=None, browser_binary=None):
    """Create webdriver instance for chrome or edge; accept explicit driver_path."""
    try:
        # Selenium 4 preferred Service approach
        if browser == 'edge':
            from selenium.webdriver.edge.service import Service as EdgeService
            from selenium.webdriver import Edge
            from selenium.webdriver.edge.options import Options as EdgeOptions
            options = EdgeOptions()
            if browser_binary:
                options.binary_location = browser_binary
            # prefer new headless mode when available
            if getattr(options, 'headless', False) is False:
                try:
                    options.add_argument('--headless=new')
                except Exception:
                    options.headless = True
            # if driver_path provided, use explicit Service
            if driver_path:
                service = EdgeService(executable_path=driver_path)
                return Edge(service=service, options=options)
            return Edge(options=options)
        else:
            from selenium.webdriver.chrome.service import Service as ChromeService
            from selenium.webdriver import Chrome
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            options = ChromeOptions()
            if browser_binary:
                options.binary_location = browser_binary
            if getattr(options, 'headless', False) is False:
                try:
                    options.add_argument('--headless=new')
                except Exception:
                    options.headless = True
            if driver_path:
                service = ChromeService(executable_path=driver_path)
                return Chrome(service=service, options=options)
            return Chrome(options=options)
    except Exception as e:
        raise


def run(login_url, username, password, code, browser='chrome', driver_path=None, browser_path=None, save_to=None, headless=False):
    print(f"Starting browser ({browser}), driver_path={driver_path}")
    try:
        # pass headless via environment: if headless requested, set headless on options
        if headless:
            # make_driver will attempt to add headless arguments
            driver = make_driver(browser=browser, driver_path=driver_path, browser_binary=browser_path)
        else:
            driver = make_driver(browser=browser, driver_path=driver_path, browser_binary=browser_path)
    except Exception as e:
        print('Failed to start WebDriver:', e, file=sys.stderr)
        raise

    try:
        driver.get(login_url)
        driver.set_window_size(1147, 854)
        time.sleep(0.3)

        # fill username
        el = driver.find_element(By.NAME, 'UN')
        el.click()
        el.clear()
        el.send_keys(username)

        # fill password
        el = driver.find_element(By.NAME, 'PW')
        el.click()
        el.clear()
        el.send_keys(password)

        # click login
        driver.find_element(By.CSS_SELECTOR, '.login-button').click()
        time.sleep(1.0)

        # click Ricerca — wait for search UI to be available after login
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#query > span')))
            driver.find_element(By.CSS_SELECTOR, '#query > span').click()
        except TimeoutException:
            print('Timeout waiting for search button after login; continuing and trying selectors directly')

        # allow time for folder tree to become interactive
        time.sleep(0.7)
        try:
            el_folder = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.k-state-hover > .tree-item-label')))
            el_folder.click()
        except TimeoutException:
            # not fatal; continue
            print('Folder node not found or clickable; continuing')

        # wait for codice field
        try:
            f1008 = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.ID, 'F1008')))
            f1008.click()
            f1008.clear()
            f1008.send_keys(code)
        except TimeoutException:
            print('Codice field F1008 not found after login/search; aborting search step')

        # click search if available
        try:
            do_search = driver.find_element(By.ID, 'do-search')
            do_search.click()
        except NoSuchElementException:
            print('do-search button not found; continuing')

        time.sleep(1.0)

        # select first document row
        try:
            driver.find_element(By.CSS_SELECTOR, '.document-row:nth-child(1) input').click()
        except Exception:
            # try alternative selector
            try:
                driver.find_element(By.CSS_SELECTOR, '.document-row input').click()
            except Exception as e:
                print('Could not select document row:', e, file=sys.stderr)

        # click view selected - this may open a new window/tab
        driver.find_element(By.CSS_SELECTOR, '#viewSelected > div').click()
        # wait for a new window and switch
        time.sleep(1.0)
        handles = driver.window_handles
        if len(handles) > 1:
            driver.switch_to.window(handles[-1])
            print('Switched to new window/tab; current URL:', driver.current_url)
        else:
            print('No new window opened; current URL:', driver.current_url)

        # After opening the document viewer, try to locate a PDF URL.
        pdf_url = None

        # If a new window/tab was opened, the driver switched to it earlier.
        current = driver.current_url
        if current and current.lower().endswith('.pdf'):
            pdf_url = current

        # Try to find any anchor with a .pdf href on the page
        if not pdf_url:
            try:
                anchors = driver.find_elements(By.CSS_SELECTOR, 'a')
                for a in anchors:
                    href = a.get_attribute('href')
                    if href and '.pdf' in href.lower():
                        pdf_url = href
                        break
            except Exception:
                pass

        # If still not found, try to click the first view link and then check URL
        if not pdf_url:
            try:
                # Attempt to click a viewer button if exists
                el = driver.find_element(By.CSS_SELECTOR, '#viewSelected > div')
                el.click()
                time.sleep(1.0)
                handles = driver.window_handles
                if len(handles) > 1:
                    driver.switch_to.window(handles[-1])
                    current = driver.current_url
                    if current and '.pdf' in current.lower():
                        pdf_url = current
            except Exception:
                pass

        if pdf_url:
            print('Found PDF URL:', pdf_url)
            # Export cookies from selenium to requests session
            s = requests.Session()
            for c in driver.get_cookies():
                s.cookies.set(c['name'], c['value'], domain=c.get('domain'))

            try:
                r = s.get(pdf_url, stream=True, timeout=20)
                if r.status_code == 200 and 'pdf' in r.headers.get('Content-Type','').lower():
                    # If caller requested a specific save path, write there and exit
                    if save_to:
                        with open(save_to, 'wb') as f:
                            for chunk in r.iter_content(8192):
                                f.write(chunk)
                        print('Saved PDF to', save_to)
                        return save_to
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                    with open(tmp.name, 'wb') as f:
                        for chunk in r.iter_content(8192):
                            f.write(chunk)
                    print('Saved PDF to', tmp.name)
                    # Open with default application on Windows
                    try:
                        os.startfile(tmp.name)
                    except Exception:
                        print('Could not open file automatically; please open', tmp.name)
                else:
                    print('Failed to download PDF via requests; status', r.status_code, 'content-type', r.headers.get('Content-Type'))
                    if save_to:
                        raise RuntimeError(f'Failed to download PDF: status {r.status_code}')
            except Exception as e:
                print('Error downloading PDF via requests:', e)
                if save_to:
                    raise
        else:
            print('Could not find PDF URL on the page. Saving screenshot and page source for debugging.')
            try:
                ss = os.path.join(tempfile.gettempdir(), 'adi_screenshot.png')
                driver.save_screenshot(ss)
                ps = os.path.join(tempfile.gettempdir(), 'adi_page_source.html')
                with open(ps, 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print('Saved screenshot to', ss)
                print('Saved page source to', ps)
            except Exception as e:
                print('Failed to save debug artifacts:', e)
            if save_to:
                raise RuntimeError('PDF URL not found on page')

        # keep browser open briefly so user can see what happened
        print('Automation finished. Browser will close in 5 seconds...')
        time.sleep(5)

    finally:
        try:
            driver.quit()
        except Exception:
            pass


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--browser', choices=['chrome', 'edge'], default='chrome')
    p.add_argument('--driver-path', default=None)
    p.add_argument('--browser-path', default=None, help='Full path to browser executable (eg. C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe)')
    p.add_argument('--username', default='mmalvicini')
    p.add_argument('--password', default='v54E2RDqwn')
    p.add_argument('--code', default='tuni032')
    p.add_argument('--save-to', default=None, help='If provided, save downloaded PDF to this path and exit')
    p.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    p.add_argument('--login-url', default='http://172.16.90.4:8080/adiJed/ui/login/page.jsp')
    args = p.parse_args()

    try:
        run(args.login_url, args.username, args.password, args.code, browser=args.browser, driver_path=args.driver_path, browser_path=args.browser_path, save_to=args.save_to, headless=args.headless)
        # Note: saving handled inside run() when --save-to is passed
    except Exception as e:
        print('Error during run:', e, file=sys.stderr)
        print('\nIf you see an error about WebDriver or driver executable, ensure you have a matching driver (msedgedriver/chromedriver) available and pass its path via --driver-path.')
        sys.exit(2)


if __name__ == '__main__':
    main()
