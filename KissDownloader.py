import urllib, csv, re, shutil, cfscrape, pySmartDL, requests, sys, os, time, pip
from pathlib import Path
from bs4 import BeautifulSoup
from tempfile import NamedTemporaryFile
from random import randint

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

# Modified verison of https://github.com/BDrgon/KissDownloader all credit to origional author(s)
# Run UpdateModuals.py for initial setup
# Download list of kissanime series

# TODO error management (download timeout)
# TODO simultaneous downloads - KissDownloadManager.py WIP

website = "kissanime.ru"
user_name = ""
user_password = ""
destination = ""
episode_min = "0" # first episode to download
quality = "1280x720.mp4"
prefix = ""

dir_path = os.path.dirname(os.path.realpath(__file__))
randnum = str(randint(1,100000))

class KissDownloader:
    def __init__(self, params):
        #for param in params:
        #    print(param)
        # create a webdriver instance with a lenient timeout duration
        self.scraper = cfscrape.create_scraper()
        self.rootPage = ""
        self.file_extension = ""
        self.download(params)

    def login(self, user, pw, site):
        
        status = ""
        while (status == 503 and status != ""):
            req = requests.head("http://"+str(site))
            status = req.status_code
            print("status code: " + str(req.status_code))
            return status
            time.sleep(.5)
        
        print("Logging in...  (5 second delay for browser check)")
        
        # define login page
        login_url = "http://" + str(site) + "/Login"
        
        #define user and pass
        username = user
        password = pw

        #define payload
        payload = {
            'username': username,
            'password': password
        }

        #login
        self.scraper.get(login_url)
        login = self.scraper.post(login_url, data=payload)

        # confirm that login was successful and return a bool
        if login.url == "https://" + site + "/login" or login.url == "http://" + site + "/login":
            return False
        else:
            return True

    def get_episode_page(self, episode, site):
        # parses the streaming page of an episode from the root page
        soup = BeautifulSoup(self.rootPage, 'html.parser')
        ###for kisscartoon.me

        if site == "kisscartoon.me":
            if episode % 1 == 0:
                ###for non special episodes
                episode = int(episode)
                for link in soup.findAll('a'):
                    currentlink = link.get('href')
                    if currentlink is None:
                        pass
                    elif "episode-" + str(episode).zfill(3) + "-" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-" in currentlink.lower():
                        return ["http://" + site + "" + currentlink.lower(), False]
            else:
                ###for special episodes
                episode = int(episode)
                # uncensored vvv
                for link in soup.findAll('a'):
                    currentlink = link.get('href')
                    if currentlink is None:
                        pass
                    elif "episode-" + str(episode).zfill(3) + "-5" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-5" in currentlink.lower():
                        return ["http://" + site + "" + currentlink.lower(), False]
        else:

            #vvvvvv for kissanime.ru / kissasian.com - might seperate if needed
            if episode % 1 == 0:
                ###for non special episodes
                episode = int(episode)
                # uncensored vvv
                for link in soup.findAll('a'):
					
                    status = ""
                    while (status == 503 and status != ""):
                        req = requests.head(link)
                        status = req.status_code
                        print("status code: " + str(req.status_code))
                        return status
                        time.sleep(.5)
	                   
                    currentlink = link.get('href')
                    if currentlink is None:
                        pass
                    elif "uncensored-episode-" + str(episode).zfill(3) + "?" in currentlink.lower() or "uncensored-episode-" + str(episode).zfill(2) + "?" in currentlink.lower() or "uncen-episode-" + str(episode).zfill(3) + "?" in currentlink.lower() or "uncen-episode-" + str(episode).zfill(2) + "?" in currentlink.lower() or "episode-" + str(episode).zfill(3) + "-uncensored?" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-uncensored?" in currentlink.lower() or "episode-" + str(episode).zfill(3) + "-uncen?" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-uncen?" in currentlink.lower():
                        return ["http://" + site + "" + currentlink.lower(), True]
                # censored vvv
                for link in soup.findAll('a'):
                    currentlink = link.get('href')
                    if currentlink is None:
                        pass
                    elif "episode-" + str(episode).zfill(3) + "?" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "?" in currentlink.lower():
                        return ["http://" + site + "" + currentlink.lower(), False]
                # weird urls
                for link in soup.findAll('a'):
                    currentlink = link.get('href')
                    if currentlink is None:
                        pass
                    elif "episode-" + str(episode).zfill(3) + "-" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-" in currentlink.lower():
                        return ["http://" + site + "" + currentlink.lower(), False]
            else:
                ###for special episodes
                episode = int(episode)
                # uncensored vvv
                for link in soup.findAll('a'):
                    currentlink = link.get('href')
                    if currentlink is None:
                        pass
                    elif "uncensored-episode-" + str(episode).zfill(3) + "-5?" in currentlink.lower() or "uncensored-episode-" + str(episode).zfill(2) + "-5?" in currentlink.lower() or "uncen-episode-" + str(episode).zfill(3) + "-5?" in currentlink.lower() or "uncen-episode-" + str(episode).zfill(2) + "-5?" in currentlink.lower() or "episode-" + str(episode).zfill(3) + "-5-uncensored?" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-5-uncensored?" in currentlink.lower() or "episode-" + str(episode).zfill(3) + "-5-uncen?" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-5-uncen?" in currentlink.lower():
                        return ["http://" + site + "" + currentlink.lower(), True]
                # censored (normal) vvv
                for link in soup.findAll('a'):
                    currentlink = link.get('href')
                    if currentlink is None:
                        pass
                    elif "episode-" + str(episode).zfill(3) + "-5?" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-5?" in currentlink.lower():
                        return ["http://" + site + "" + currentlink.lower(), False]
                # weird urls
                for link in soup.findAll('a'):
                    currentlink = link.get('href')
                    if currentlink is None:
                        pass
                    elif "episode-" + str(episode).zfill(3) + "-5" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-5" in currentlink.lower():
                        return ["http://" + site + "" + currentlink.lower(), False]
        return ["", False]

    def get_video_src(self, episode_page, qual):
        # parses the video source link from the streaming page, currently chooses the highest available quality

        x = True
        while x:
            try:
                page = self.scraper.get(episode_page)
                #print(page.text)
                url = page.url
                if "Special/AreYouHuman?" in str(url):
                    print("please click url and prove your human")
                    print(page.url)
                    input("Press Enter to continue...")
                    print("please wait for system to refresh...")
                    time.sleep(10)
                x = False
            # try again if the page times out
            except:
                print("loading " + episode_page + " timed out, trying again.")
                time.sleep(5)
        time.sleep(1)
        #print("---")
        #print(page.url)
        currentpage = page.content
        soup = BeautifulSoup(currentpage, 'html.parser')

# 16:9 vvv
        if qual in ["1920x1080.mp4"] and soup.findAll('a', string="1920x1080.mp4") != []:
            for link in soup.findAll('a', string="1920x1080.mp4"):
                return [link.get('href'), ".mp4"]
        elif qual in ["1920x1080.mp4", "1280x720.mp4"] and soup.findAll('a', string="1280x720.mp4") != []:
            for link in soup.findAll('a', string="1280x720.mp4"):
                return [link.get('href'), ".mp4"]
        elif qual in ["1920x1080.mp4", "1280x720.mp4", "640x360.mp4"] and soup.findAll('a', string="640x360.mp4") != []:
            for link in soup.findAll('a', string="640x360.mp4"):
                return [link.get('href'), ".mp4"]
        elif qual in ["1920x1080.mp4", "1280x720.mp4", "640x360.mp4", "320x180.3gp"] and soup.findAll('a', string="320x180.3gp") != []:
            for link in soup.findAll('a', string="320x180.3gp"):
                return [link.get('href'), ".3pg"]
# 4:3 vvv
        elif qual in ["1920x1080.mp4", "1280x720.mp4", "640x360.mp4", "320x180.3pg", "960x720.mp4"] and soup.findAll('a', string="960x720.mp4") != []:
            for link in soup.findAll('a', string="960x720.mp4"):
                return [link.get('href'), ".mp4"]
        elif qual in ["1920x1080.mp4", "1280x720.mp4", "640x360.mp4", "320x180.3pg", "960x720.mp4", "480x360.mp4"] and soup.findAll('a', string="480x360.mp4") != []:
            for link in soup.findAll('a', string="480x360.mp4"):
                return [link.get('href'), ".mp4"]
        elif qual in ["1920x1080.mp4", "1280x720.mp4", "640x360.mp4", "320x180.3pg", "960x720.mp4", "480x360.mp4", "320x240.3pg"] and soup.findAll('a', string="320x240.3pg") != []:
            for link in soup.findAll('a', string="320x240.3pg"):
                return [link.get('href'), ".3pg"]
        else:
            return ["false", ""]

    def download_video(self, url, name, destination):
        #makes sure the directory exists
        try:
            os.stat(destination)
        except:
            os.makedirs(destination)

        filename = name
        path = destination + filename
        obj = pySmartDL.SmartDL(url, destination, progress_bar=False, fix_urls=True)
        obj.start(blocking=False)
        location = obj.get_dest()

        while True:
            if obj.isFinished():
                break
            print(name + "\t " + str(float("{0:.2f}".format((float(obj.get_progress())*100)))) + "% [" + pySmartDL.utils.sizeof_human(obj.get_speed(human=False))+"/s]", end="\r")
            #*epiode name* 0.38% 2.9 MB/s
            time.sleep(1)
        if obj.isFinished():
            time.sleep(1)
            os.rename(location, path)
        else:
            print("Download of " + name + " failed")
        return path

    def frange(self, start, stop, step):
        i = start
        while i < stop:
            yield i
            i += step

    def zpad(self, val, n):
        bits = val.split('.')
        return "%s.%s" % (bits[0].zfill(n), bits[1])

    def download(self, p):
        episode_list = []
        global prefix

        #p = [user, password, title, anime, season, episode_min, episode_max, destination, quality, site]
        # takes a list of parameters and uses them to download the show
        l = self.login(p[0], p[1], p[9])  # 0 are the indices of the username and password from get_params()
        while not l:
            print("Login failed, try again")
            l = self.login(p[0], p[1], p[9])

        time.sleep(3)
        self.rootPage = self.scraper.get(p[3]).content  # 3 is the index of the url
        time.sleep(3)


        print("Retrieve episode url...")
        for e in self.frange(float(p[5]), int(p[6])+1, 0.5):  # 5 and 6 are episodes min and max
            page = self.get_episode_page(e, p[9])
            # page = [page_url, isUncensored]
            if page[0] == "":
                pass
            else:
                video = self.get_video_src(page[0], p[8]) #8 is the quality
                if p[8] in ["1920x1080.mp4", "1280x720.mp4", "960x720.mp4"]:
                    resolution = "720p"
                elif p[8] in ["480x360.mp4", "320x180.mp4"]:
                    resolution = "480p"
                elif p[8] in ["640x360.mp4", "320x180.mp4", "320x240.mp4", "320x180.3gp", "320x240.3pg"]:
                    resolution = "360p"
                else:
                    resolution = p[8]
                # video = [url, file_extension]

                if prefix != "":
                    prefix2 = p[4] + prefix

                if video[0] != 'false':
                    if page[1]:  # if episode is called uncensored
                        if e % 1 == 0:
                            e = int(e)
                            filename = prefix2 + p[2] + "_-_" + str(e).zfill(3) + "_" + resolution +"_BD_Kiss" + video[1]  # 2 is the title
                        else:
                            filename = prefix2 + p[2] + "_-_" + self.zpad(str(e), 3) + "_" + resolution +"_BD_Kiss" + video[1]  # 2 is the title
                    else:
                        if e % 1 == 0:
                            e = int(e)
                            filename = prefix2 + p[2] + "_-_" + str(e).zfill(3) + "_" + resolution + "_Kiss" + video[1]  # 2 is the title
                        else:
                            filename = prefix2 + p[2] + "_-_" + self.zpad(str(e), 3) + "_" + resolution + "_Kiss" + video[1]  # 2 is the title
                    print("Resolved [" + filename + "]")
                    episode_list.append((video[0], filename, p[7]))
                else: print("Retrieve failed [" + str(e) + "] trying alternative quality")
        for tuple in episode_list:
            url = tuple[0]
            filename = tuple[1]
            destination = tuple[2]

            my_file = Path(destination + filename)
            if my_file.is_file():
                print("[" + filename + "] exists...")
            else:
                self.download_video(url, filename, destination)
                print("downloaded " + filename)

        # Done download

        os.rename( dir_path + "/resolved.csv", dir_path + "/resolved.csv.old")
        os.rename( dir_path + "/temp/resolved"+randnum+".csv", dir_path + "/resolved.csv")

        # Marked complete, retrieve next...
        KissDownloader
        website,user_name,user_password,title,url,mal,episode_min,episode_max,destination,quality = KissDownloader.read_config()
        KissDownloader.run_download([website,user_name,user_password,title,url,mal,episode_min,episode_max,destination,quality])
        episodes_list = []
        for tup in episodes_list:
            url = tup[0]
            filename = tup[1]
            destination = tup[2]
            KissDownloader.download_video(KissDownloader, url, filename, destination)

    def read_config():

        reader = csv.reader(open( dir_path + "/resolved.csv","r"),delimiter=",")
        newfile = open( dir_path + "/temp/resolved"+randnum+".csv", "a")
        writer = csv.writer(newfile)
        br = 0
        first = 0
        for row in reader:
            try:
                #print(row)
                if(br==0):
                    #print(row[4])
                    newrow=[row[0],row[1],row[2],row[3],row[4],1]
                    
                    title = row[0]
                    url = row[1]
                    mal = row[2]
                    episode_max = row[3]
                    br = 1
                    pass
                else:
                    writer.writerows([row])
            except IndexError:
                print("EndIndex")
            except Exception:
                print("Exception")
            
        #writer.writerows([newrow]) # uncomment to include first row from new file
        
        newfile.close()

        mapping = { ' ':'_', '-':'_', '`':'_', '@':'_', '#':'_', '$':'_', '%':'_', '^':'_', '&':'_', '*':'_', '(':'_', ')':'_', '[':'_', ']':'_', '|':'_', '+':'_', '=':'_', ':':'_', ';':'_', '~':'_', '___':'_', '__':'_'}
        for k, v in mapping.items():
            title = title.replace(k, v)
        
        return website,user_name,user_password,title,url,mal,episode_min,episode_max,destination,quality

    def run_download(self):
        # 0 website, 1 user_name,2 user_password, 3 title, 4 url, 5 mal, 6 episode_min, 7 episode_max, 8 destination, 9 quality
        destination_folder = self[8].replace("\\", "/")
        if destination_folder.endswith('/'):
            destination = destination_folder + self[3] + "/"
        else:
            destination = destination_folder + "/" + self[3] + "/"
        '''destination = destination_folder + "/"'''
        params = [self[1], self[2], self[3], self[4], self[5], self[6], self[7], destination, self[9], self[0]]
        print(params)
        KissDownloader(params)

if __name__ == "__main__":
    #params = [user, password, title, anime, season, episode_min, episode_max, destination, quality, site]
    print('Load config...')
    KissDownloader
    website,user_name,user_password,title,url,mal,episode_min,episode_max,destination,quality = KissDownloader.read_config()
    KissDownloader.run_download([website,user_name,user_password,title,url,mal,episode_min,episode_max,destination,quality])
    episodes_list = []
    for tup in episodes_list:
        url = tup[0]
        filename = tup[1]
        destination = tup[2]
        KissDownloader.download_video(KissDownloader, url, filename, destination)
