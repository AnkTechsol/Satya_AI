import time
from playwright.sync_api import sync_playwright
import subprocess

subprocess.Popen(["python", "start_app.py"])
time.sleep(5)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:5000")
    time.sleep(2)
    page.get_by_text('ROI Dashboard').click()
    time.sleep(2)
    page.screenshot(path="screenshot.png")
    browser.close()