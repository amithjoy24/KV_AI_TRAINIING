from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Optional: Run in headless mode (no browser window)
options = Options()
# options.add_argument("--headless")  # Uncomment if you want headless

# Setup Chrome driver using WebDriver Manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open a webpage
driver.get("https://example.com")

# Print the page title
print("Page Title:", driver.title)

# Close the browser
driver.quit()
