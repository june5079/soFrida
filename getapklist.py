import requests
import time, sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# HOW to Use 
# from getapklist import Getlists
    # getlist = Getlists("basic", "happylabs") 
    # getlist.init_request()
    # getlist.get_result()

class Getlists:

    def __init__(self, option, search_keyword):
        # Define base info
        self.option = option
        self.search_keyword = search_keyword
        self.play_search_basic = "https://play.google.com/store/search?q="
        self.play_search_pkgid = "https://play.google.com/store/apps/details?id="
        self.play_search_devid = "https://play.google.com/store/apps/dev?id="

        if self.option == "basic" :
            self.request_url = self.play_search_basic
            print (self.request_url)
        elif self.option == "pkgid" :
            self.request_url = self.play_search_pkgid
            print (self.request_url)
        elif self.category == "devid" :
            self.request_url = self.play_search_devid
        else :
            print ("Wrong categories")
            exit()
    
    def init_request(self):
        self.f = open ("apklist_{0}.txt".format(self.search_keyword),"w")
        self.options = Options()
        self.options.headless = True
        self.browser = webdriver.Chrome('./chromedriver', chrome_options=self.options)
        self.make_connection()

    def make_connection(self):
        self.browser.get(self.request_url)
        # Get Pkg names
        self.load_pkglists()

        # Call Parser
        self.full_source = self.browser.page_source
        self.parse_pkgnames()
    
    def parse_pkgnames(self):
        self.s = set()  
        soup = BeautifulSoup(self.full_source, "html.parser")
        for link in soup("a"):
            if 'href' in link.attrs:
                self.s.add(link.attrs['href'])
        
        for x in self.s:
            if "details?id" in x:
                self.f.write(x.split("=")[1]+"\n")
                #print (x.split("=")[1]) 
        self.f.close()
        print ("Done Grabbing APK Lists")
        self.browser.close()
        time.sleep(2)                

    def click_more(self):
        try:
            self.browser.find_element_by_css_selector("#show-more-button").click()
            self.load_pkglists()
        except:
            print ("Done")
            pass

    def load_pkglists(self):
        for i in range(0, 5):
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        self.click_more()
    
    def get_result(self):
        f = open("apklist_{0}.txt".format(self.search_keyword), 'r')
        # get reuest
        l = f.readlines()

        for x in l:
            try:
                # print (x)
                r = requests.get(self.play_search_pkgid + x.strip("\n"))
                res = r.text

                soup = BeautifulSoup(res, "html.parser" )

                pop = (soup.select ('div[class=IQ1z0d]'))[2]
                pop_cat = (soup.select ('span > a'))
                pop_title = (soup.select('h1 > span'))

                
                fin=''.join(str(e) for e in pop)  
                fin_pop = fin.split('+')[0].split('>')[1]
                
                fin_cat=''.join(str(k) for k in pop_cat)  
                fin_cat2 = fin_cat.split("category/")[1].split('"')[0]

                fin_title=''.join(str(g) for g in pop_title)
                fin_title2 = fin_title.split('>')[1].split('<')[0] 

                mailtos = soup.select('a[href^=mailto]')
                mailtoss = ''.join(str(u) for u in mailtos)
                print (x.strip("\n") + " : " + fin_pop + " : " + fin_cat2 + " : " + fin_title2 + " : " + mailtoss)

            except:
                print (x.strip("\n") + " : " + "ERROR\n")
                pass


    
