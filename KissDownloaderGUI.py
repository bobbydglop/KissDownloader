from KissDownloader import *

from tkinter.ttk import *
import tkinter.ttk as ttk
import tkinter as tk
from tkinter import StringVar
import csv
from collections import defaultdict
import os

if not os.path.exists(dir_path+'/resolved.csv'):
    open(dir_path+'/resolved.csv', 'a').close()

class OneVoltTen(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne):
            frame = F(container, self)

            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        controller.title("KissDownloader")

        Label(self, text="Enter series URL: ").pack()
        self.url = Entry(self, width=30)
        self.url.pack()

        Label(self, text="Enter series name: ").pack()
        self.title = Entry(self, width=30)
        self.title.pack()

        Label(self, text="Enter series episode count: ").pack()
        self.episode_count = Entry(self, width=30)
        self.episode_count.pack()

        Label(self, text="Download from episode (min): ").pack()
        self.episode_min = Entry(self, width=30)
        self.episode_min.pack()

        Label(self, text="Download to episode (max): ").pack()
        self.episode_max = Entry(self, width=30)
        self.episode_max.pack()

        Label(self, text="Select maximum resolution: ").pack()
        self.quality_select = Combobox(self, values=["1080p", "720p", "480p", "360p"], width=27)
        self.quality_select.pack()

        self.queue_button = Button(self, text='Queue', width=14, command=self.queue_download).pack()

        if(demo_data == 1):
            self.url.insert(0, "http://kissanime.ru/Anime/Re-Zero-kara-Hajimeru-Isekai-Seikatsu")
            self.title.insert(0, "Re Zero")
            self.episode_count.insert(0, "25")
            self.episode_min.insert(0, "0")
            self.episode_max.insert(0, "0")
        self.quality_select.set("720p")


        Label(self, text="Once queued series: ").pack()
        button = tk.Button(self, text="Next", width=12, command=lambda: controller.show_frame(PageOne))
        button.pack()

    def queue_download(self):
        if("https://" in str(self.url.get()) \
            or "http://" in str(self.url.get()) \
            or "www." in str(self.url.get())):
            valid = 0
            for checkint in ["episode_count","episode_min","episode_max"]:
                try_this = "self." + checkint + ".get()"
                if not eval(try_this).isdigit():
                    print(checkint + " must be number!")
                    valid = 1
            if(valid == 0):
                with open( dir_path + '/resolved.csv', 'a') as csvfile:
                    thewriter = csv.writer(csvfile, delimiter=',')
                    #print(str(params))
                    params = [str(self.title.get()), str(self.url.get()), '0', str(self.episode_count.get()), str(self.episode_min.get()), str(self.episode_max.get()), str(self.quality_select.get()[:-1])]
                    thewriter.writerow(params)
                #print("Queued", self.title.get())
        else:
            print('URL invalid')

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        button = tk.Button(self, text="Read queue", command=self.readCSV) # TODO on change to PageOne run function
        button.pack()
        self.controller=controller
        self.dir_path = dir_path=os.path.dirname(os.path.realpath(__file__))

    def readCSV(self):
        valid = 0
        columns = defaultdict(list) # each value in each column is appended to a list
        with open('resolved.csv','r') as f:
          reader = csv.reader(f,delimiter=',')
          for row in reader:
            try:
                if row[0]:
                    if valid == 0:
                        Label(self, text="Queued items:").pack()
                        valid = 1
                    new_btn = Button(self, text=row[0], command=self.btnClick(row[1]))
                    new_btn.pack()
            except IndexError as e:
                pass

        if valid == 1:
            button3 = tk.Button(self, text="Start Download", command=self.initiate)
            button3.pack()
        else:
            Label(self, text="No queued items :(").pack()

    def btnClick(self, row_url):
        # print(row_url)
        # csv where row_url in row, delete row
        pass

    def initiate(self):
        self.controller.destroy()
        KissDownloader.init()

app = OneVoltTen()
app.mainloop()

class KissDownloadGUI(tk.Tk): # TODO
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand = True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.v = tk.StringVar()
        Label(self.container, textvariable=self.v).pack()

        self.v.set("New Text!")

        self.container.mainloop()

    def update(self):
        global count
        global download_prog
        global download_list
        download_prog=False

        while(download_prog==False): # one instance
            print(1, count)
            while count > 0:
                print(2, count)
                for item in download_list:
                    print(download_list[item]) # output download progress
                    self.v.set(download_list[item])
                time.sleep(1)
            download_prog=True
        print(3)

        print(4)

    def destroy(self):
        self.container.destroy()
