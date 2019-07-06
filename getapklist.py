import requests
import time, sys
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathos.multiprocessing import ProcessingPool
from tqdm import tqdm
import platform

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
        self.apklist = []
        self.result = dict()
        self.reslist = []

        if self.option == "basic" :
            self.request_url = self.play_search_basic + self.search_keyword + "&c=apps"
            print (self.request_url)
        elif self.option == "pkgid" :
            self.request_url = self.play_search_pkgid + self.search_keyword
            print (self.request_url)
            self.apklist = [search_keyword]
        elif self.option == "devid" :
            self.request_url = self.play_search_devid + self.search_keyword
        else :
            print ("Wrong categories")
            exit()
        if platform.system() == "Windows":
            self.chrome_driver = "./chromedriver.exe"
        else:
            self.chrome_driver = "./chromedriver"
    
    def init_request(self):
        if self.option == "pkgid":
            #self.get_pkginfo()
            pass
        else:
            # self.f = open ("apklist_{0}.txt".format(self.search_keyword),"w")
            self.options = Options()    
            self.options.add_argument("--start-maximized")
            self.options.headless = False
            self.browser = webdriver.Chrome(self.chrome_driver, chrome_options=self.options)
            self.browser.maximize_window()
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
                self.apklist.append(x.split("=")[1])
                # self.f.write(x.split("=")[1]+"\n")
                #print (x.split("=")[1]) 
        # self.f.close()
        print ("[+] Done Grabbing APK Lists")
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
    
    def get_pkginfo(self):
        l = self.apklist
   
        for x in tqdm(l):
            try:
                print (x)
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

                self.result[x] = []
                self.result[x].append({"popular":fin_pop, "category":fin_cat2, "title":fin_title2})

            except:
                print (x.strip("\n") + " : " + "ERROR\n")
                pass

        # print (self.result)
        with open ("apklist_{0}.json".format(self.search_keyword), 'w') as outfile:
            json.dump(self.result, outfile)

    def get_pkginfo_for_GUI(self, logger):
        l = self.apklist
        logger.info(json.dumps({"LOG":"Start Downloading "+str(len(l))+" apks."}))
        try:
            i = 1
            for x in l:
                try:
                    print (x)
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

                    self.result[x] = []
                    self.result[x].append({"popular":fin_pop, "category":fin_cat2, "title":fin_title2})
                    logger.info(json.dumps({x:{"popular":fin_pop, "category":fin_cat2, "title":fin_title2}}))
                    logger.info(json.dumps({"LOG":"("+str(i)+"/"+str(len(l))+") Loaded "+x+" info."}))
                    i+=1
                except Exception as e:
                    print (x.strip("\n") + " : " + "ERROR\n")
                    logger.info(json.dumps({"LOG":"("+str(i)+"/"+str(len(l))+") Failed to load "+x+" info."}))
                    i+=1
                    #pass
            raise GeneratorExit("complete")
        except GeneratorExit as e:
            print (x.strip("\n") + " : " + "EXIT\n")
            logger.info(json.dumps({"EXIT":{"msg":str(e)}}))
        except Exception as e:
            print(e)

