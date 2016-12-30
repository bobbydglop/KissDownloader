import urllib, csv, re, shutil, cfscrape, pySmartDL, requests, sys, os, time, pip, glob, shutil, random
from pathlib import Path
from bs4 import BeautifulSoup
from tempfile import NamedTemporaryFile
from random import randint
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

# ----  CONFIG START ---- #

website = "kissanime.ru"
user_name = "" # required
user_password = "" # required
destination = "" # optional (defaults to /downloads folder)
download_limit = 12 # recommended values 2-40 (limits url to retrieve before downloading; retrieved url expire)

# ----  CONFIG END   ---- #

# TODO Simultaneous downloads - DownloadManager.py WIP
# TODO retrieve_last logic WIP
# TODO Handling for episodes values with hyphen seporator (e.g. 116-117)

retrieve_last = 0
episode_current = 0
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
            time.sleep(random.randint(1,2))
        
        print("Logging in...  (5 second cloudflare check)")
        
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
                    time.sleep(random.randint(1,2))
                       
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
            # experimental urls
            for link in soup.findAll('a'):
                currentlink = link.get('href')
                if currentlink is None:
                    pass
                else:
                    currentlinkx = currentlink.lower()
                    episodex = 0
                    #print(currentlink)
                    if("/anime/" in currentlinkx):
                        currentlinkx = currentlinkx.replace("/anime/", "")
                        animetitle = currentlinkx.split("/",1)
                        for item in animetitle: # get last item
                            episodexx=item
                        if animetitle[0]+"-" in episodexx:
                            episodex = episodexx.replace(animetitle[0]+"-", "")
                            print("found [" + episodex + "]")
                            episodex = episodex.split("-")[0]
                    try:
                        if(float(episodex) > 0 and float(episodex)==float(episode)):
                            print(episodex)
                            return ["http://" + site + "" + currentlink.lower(), False]
                        else:
                            pass
                    except ValueError:
                        print("invalid episode")
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

    def get_video_src(self, episode_page):
        # parses the video source link from the streaming page, retrieves highest available quality

        x = True
        while x:
            try:
                page = self.scraper.get(episode_page)
                #print(page.text)
                url = page.url
                if "Special/AreYouHuman?" in str(url):
                    print("Please click url and prove your human")
                    print(page.url)
                    input("Press Enter to continue...")
                x = False
            # try again if the page times out
            except:
                print("loading " + episode_page + " timed out, trying again.")
                time.sleep(random.randint(5,10))
        time.sleep(1)
        #print("---")
        #print(page.url)
        currentpage = page.content
        soup = BeautifulSoup(currentpage, 'html.parser')

        #for link in soup.findAll('a', string="1920x1080.mp4"):
        #    return [link.get('href'), ".mp4"]
        for link in soup.findAll('a', string="1280x720.mp4"):
            return [link.get('href'), ".mp4", "720p"]
        for link in soup.findAll('a', string="960x720.mp4"):
            return [link.get('href'), ".mp4", "720p"]
        for link in soup.findAll('a', string="854x480.mp4"):
            return [link.get('href'), ".mp4", "480p"]
        for link in soup.findAll('a', string="480x360.mp4"):
            return [link.get('href'), ".mp4", "480p"]
        for link in soup.findAll('a', string="640x360.mp4"):
            return [link.get('href'), ".mp4", "360p"]
        '''
        # uncomment if you want these resolutions (low quality)
        for link in soup.findAll('a', string="320x240.3pg"):
            return [link.get('href'), ".3pg", "240p"]
        for link in soup.findAll('a', string="320x180.3gp"):
            return [link.get('href'), ".3pg", "180p"]
        '''
        return ["false", "", ""]

    def download_video(self, url, name, destination, episode):
        #makes sure the directory exists
        try:
            os.stat(destination)
        except:
            os.makedirs(destination)

        try:
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
                episode_current = episode
            else:
                print("Download of " + name + " failed")
            return path
        except:
            print("except")

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
        file_list = []
        global prefix
        global episode_current
        global download_limit
        ecount = 0
        epcount = p[5]
        
        #destination = destination + title
        for infile in glob.glob(p[7]+"/*.mp4"):
            infile = infile.replace(p[7],"")
            infile = re.sub(r'.*_-_', '', infile)
            infile = infile[:3]
            #print(infile)
            if(int(infile)):
                file_list.append(infile)
        #print(file_list)
        if file_list:
            if(int(max(file_list))):
                epcount = int(max(file_list))+1
            else:
                print(str(epcount)+" is not int!")
        
        if(int(epcount) > int(retrieve_last)):
            epcount = int(epcount) - int(retrieve_last)
        #else:
        #    print("No downloaded files found")

        # takes a list of parameters and uses them to download the show
        l = self.login(p[0], p[1], p[8])  # 0 are the indices of the username and password from get_params()
        while not l:
            print("Login failed, try again")
            l = self.login(p[0], p[1], p[8])

        time.sleep(random.randint(1,2))
        self.rootPage = self.scraper.get(p[3]).content  # 3 is the index of the url
        time.sleep(random.randint(1,2))
        
        dead = 0
        #print("Retrieve from " + str(epcount))
        for e in self.frange(float(epcount), int(p[6])+1, 0.5):  # 5 and 6 are episodes min and max
            if(ecount < int(download_limit)):
                time.sleep(random.randint(0,1))
                page = self.get_episode_page(e, p[8])
                # page = [page_url, isUncensored]
                #print(dead)
                if page[0] == "":
                    dead = dead + 1
                    if(dead>=8):
                        break
                    pass
                else:
                    dead = 0
                    video = self.get_video_src(page[0])
                    # video = [url, file_extension, resolution]
                    if prefix != "":
                        prefix2 = p[4] + prefix
                    else:
                        prefix2 = ""

                    if video[0] != 'false':
                        if page[1]:  # if episode is called uncensored
                            if e % 1 == 0:
                                e = int(e)
                                filename = prefix2 + p[2] + "_-_" + str(e).zfill(3) + "_" + video[2] +"_BD_Kiss" + video[1]  # 2 is the title
                            else:
                                filename = prefix2 + p[2] + "_-_" + self.zpad(str(e), 3) + "_" + video[2] +"_BD_Kiss" + video[1]  # 2 is the title
                        else:
                            if e % 1 == 0:
                                e = int(e)
                                filename = prefix2 + p[2] + "_-_" + str(e).zfill(3) + "_" + video[2] + "_Kiss" + video[1]  # 2 is the title
                            else:
                                filename = prefix2 + p[2] + "_-_" + self.zpad(str(e), 3) + "_" + video[2] + "_Kiss" + video[1]  # 2 is the title
                        episode_list.append((video[0], filename, p[7], str(e).zfill(3)))
                        ecount = ecount + 1
                        print("Resolved [" + filename + "]")
                    else: print("Retrieve failed [" + str(e) + "]")
            else:
                print("download_limit reached ("+str(download_limit)+")")
                break

        #print(episode_list)
        for tuple in episode_list:
            url = tuple[0]
            filename = tuple[1]
            destinationf = tuple[2]
            episode = tuple[3]
            my_file = Path(destinationf + filename)
            if my_file.is_file():
                print("[" + filename + "] exists...")
            else:
                self.download_video(url, filename, destinationf, episode)
                latest_episode = episode
                print("Downloaded " + filename + "\r")

        # get list total count
        if(episode_list):
            os.rename( dir_path + "/temp/resolved"+randnum+".csv", dir_path + "/resolved.csv.trash")
            KissDownloader.init()
        else:
            print("Download complete!")
            if(1 == 0): # developer (move *.mp4 to upper folder)
                print("Move *.mp4 into downloads folder")
                destinationf = p[7]
                source = os.listdir(destinationf)
                for files in source:
                    if files.endswith('.mp4'):
                        shutil.move(os.path.join(destinationf,files), os.path.join(destination,files))
            os.remove( dir_path + "/resolved.csv")
            os.rename( dir_path + "/temp/resolved"+randnum+".csv", dir_path + "/resolved.csv")
            KissDownloader.init()

    def read_config():

        # reset temp folder
        if os.path.exists(dir_path + "/temp"):
            shutil.rmtree(dir_path + "/temp")
        os.mkdir(dir_path + "/temp")

        reader = csv.reader(open( dir_path + "/resolved.csv","r"),delimiter=",")
        newfile = open( dir_path + "/temp/resolved"+randnum+".csv", "a")
        writer = csv.writer(newfile)
        br = 0
        for row in reader:
            try:
                if row:
                    #print(row)
                    if(br==0):
                        title = row[0]
                        url = row[1]
                        episode_max = row[2]
                        mal = row[3]
                        br = 1
                        newrow=[row[0],row[1],row[2],row[3],1]
                        pass
                    else:
                            writer.writerows([row])
            except IndexError:
                print("EndIndex")
            except Exception:
                print("Exception")
        '''
        writer.writerows([newrow])
        '''
        
        newfile.close()

        mapping = { ' ':'_', '-':'_', '`':'_', '@':'_', '#':'_', '$':'_', '%':'_', '^':'_', '&':'_', '*':'_', '(':'_', ')':'_', '[':'_', ']':'_', '|':'_', '+':'_', '=':'_', ':':'_', ';':'_', '~':'_', '___':'_', '__':'_'}
        for k, v in mapping.items():
            title = title.replace(k, v)
        episode_min = "0"
        print('Initiate... [' + title + ']')
        return website,user_name,user_password,title,url,mal,episode_min,episode_max,destination

    def run_download(self):
        # 0 website, 1 user_name,2 user_password, 3 title, 4 url, 5 mal, 6 episode_min, 7 episode_max, 8 destination
        if self[8] == "":
            if not os.path.exists(dir_path + "/downloads"):
                os.mkdir(dir_path + "/downloads")
            destination = dir_path + "/downloads"
        else:
            destination_folder = self[8].replace("\\", "/")
            if destination_folder.endswith('/'):
                destination = destination_folder + self[3] + "/"
            else:
                destination = destination_folder + "/" + self[3] + "/"
            '''destination = destination_folder + "/"'''
        params = [self[1], self[2], self[3], self[4], self[5], self[6], self[7], destination, self[0]]
        #print(params)
        KissDownloader(params)

    def init():
        # 0 website, 1 user_name,2 user_password, 3 title, 4 url, 5 mal, 6 episode_min, 7 episode_max, 8 destination
        website,user_name,user_password,title,url,mal,episode_min,episode_max,destination = KissDownloader.read_config()
        KissDownloader.run_download([website,user_name,user_password,title,url,mal,episode_min,episode_max,destination])
        episodes_list = []
        for tup in episodes_list:
            url = tup[0]
            filename = tup[1]
            destination = tup[2]
            KissDownloader.download_video(KissDownloader, url, filename, destination, episode)

if __name__ == "__main__":
    KissDownloader
    KissDownloader.init()

