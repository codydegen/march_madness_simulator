# import requests

# # proxies = {
# # #  "http": "http://10.10.10.10:8000",
# #  "https": "https://3.83.212.156:8080",
# # }
# # r = requests.get("http://toscrape.com", proxies=proxies)

# from selenium import webdriver
# # from selenium.webdriver import Chrome
# PROXY = "https://3.83.212.156:8080"
# webdriver.DesiredCapabilities.CHROME['proxy'] = {
#     "httpProxy":PROXY,
#     "ftpProxy":PROXY,
#     "sslProxy":PROXY,
#     "noProxy":None,
#     "proxyType":"MANUAL",
#     "class":"org.openqa.selenium.Proxy",
#     "autodetect":False
# }

# driver = webdriver.Remote("http://localhost:4444/wd/hub", webdriver.DesiredCapabilities.CHROME)


# # chrome_options = WebDriverWait.ChromeOptions()
# # chrome_options.add_argument('--proxy-server=%s' % "https://3.83.212.156:8080")

# # chrome = webdriver.Chrome(chrome_options=chrome_options)
# # chrome.get("https://www.google.com")

from selenium import webdriver
import time

PROXY = "3.83.212.156:8080"
webdriver.DesiredCapabilities.CHROME['proxy']={
    "httpProxy":PROXY,
    "ftpProxy":PROXY,
    "sslProxy":PROXY,
    "noProxy":None,
    "proxyType":"MANUAL",
    "autodetect":False
}
driver = webdriver.Chrome()
driver.get('http://www.whatsmyip.org/')
time.sleep(30)


# from selenium import webdriver
# from selenium.webdriver.common.proxy import Proxy, ProxyType

# prox = Proxy()
# prox.proxy_type = ProxyType.MANUAL
# prox.http_proxy = "ip_addr:port"
# prox.socks_proxy = "ip_addr:port"
# prox.ssl_proxy = "ip_addr:port"

# capabilities = webdriver.DesiredCapabilities.CHROME
# prox.add_to_capabilities(capabilities)

# driver = webdriver.Chrome(desired_capabilities=capabilities)