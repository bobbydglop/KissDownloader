from KissDownloader import *
from tkinter import *
from tkinter.ttk import *

# ----  CONFIG START ---- #

demo_data = 1 # Display sample data in insert form [set to 0 to disable]
# Please define config under KissDownloader.py

# ----  CONFIG END ---- #

class App(Frame):

    def __init__(self):
        Frame.__init__(self)
        self.master.title("KissDownloader")
        self.grid()
        self.master.geometry("450x200")

    # TODO add logic to read the username,password,destination from ini file

        self.explain_label = Label(self, text="Queue series to be processed.").grid(row=1, column=1)
        self.explain_label2 = Label(self, text="Once queued press 'Start Download'.").grid(row=1, column=2)


    # create username label and field
    #    self.user_name_label = Label(self, text="Kiss Username: ").grid(row=2, column=1)
    #    self.user_name = Entry(self, width=30)
    #    self.user_name.grid(row=2, column=2)
    # create password label and field
    #    self.user_password_label = Label(self, text="Kiss Password: ").grid(row=3, column=1)
    #    self.user_password = Entry(self, show="*", width=30)
    #    self.user_password.grid(row=3, column=2)
    # create root destination label and field
    #    self.destination_label = Label(self, text="Enter destination folder: ").grid(row=4, column=1)
    #    self.destination = Entry(self, width=30)
    #    self.destination.grid(row=4, column=2)
    # create kissanime url label and field
        self.url_label = Label(self, text="Enter series URL: ").grid(row=5, column=1)
        self.url = Entry(self, width=30)
        self.url.grid(row=5, column=2)
    # create series name label and field
        self.title_label = Label(self, text="Enter series name: ").grid(row=6, column=1)
        self.title = Entry(self, width=30)
        self.title.grid(row=6, column=2)
    # create episode total label and field
        self.episode_count_label = Label(self, text="Enter series episode count: ").grid(row=7, column=1)
        self.episode_count = Entry(self, width=30)
        self.episode_count.grid(row=7, column=2)
    # create episode min label and field
        self.episode_min_label = Label(self, text="Download from episode (min): ").grid(row=8, column=1)
        self.episode_min = Entry(self, width=30)
        self.episode_min.grid(row=8, column=2)
    # create episode max label and field
        self.episode_max_label = Label(self, text="Download to episode (max): ").grid(row=9, column=1)
        self.episode_max = Entry(self, width=30)
        self.episode_max.grid(row=9, column=2)
    # create label for quality select
        self.site_select_label = Label(self, text="Select maximum resolution: ").grid(row=10, column=1)
    # create a Combobox with quality to choose from
        self.available_quality = ["1080p", "720p", "480p", "360p"]
        self.quality_select = Combobox(self, values=self.available_quality)
        self.quality_select.grid(row=10, column=2, padx=32, pady=8)
    # queue button
        self.queue_button = Button(self, text='Queue')
        self.queue_button['command'] = self.queue_download
        self.queue_button.grid(row=11, column=1)
    # download button
        self.download_button = Button(self, text='Start Download')
        self.download_button['command'] = self.run_download
        self.download_button.grid(row=11, column=2)


        if(demo_data == 1):
            self.url.insert(0, "http://kissanime.ru/Anime/Re-Zero-kara-Hajimeru-Isekai-Seikatsu")
            self.title.insert(0, "Re Zero")
            self.episode_count.insert(0, "25")
            self.episode_min.insert(0, "0")
            self.episode_max.insert(0, "0")
        self.quality_select.set("720p")

    def queue_download(self):
        # validate
        valid = 0

        for checkurl in ["http://","https://","www."]:
            if(checkurl in str(self.url.get())):
                valid = 0
        if(valid == 1):
            print("URL invalid please check!")
        else:
            for checkint in ["episode_count","episode_min","episode_max"]:
                try_this = "self." + checkint + ".get()"
                if not eval(try_this).isdigit():
                    print(checkint + " must be number!")
                    valid = 1
            if(valid == 0):
                with open(dir_path+'/resolved.csv', 'a') as csvfile:
                    thewriter = csv.writer(csvfile, delimiter=',')
                    params = [str(self.title.get()), str(self.url.get()), '0', str(self.episode_count.get()), str(self.episode_min.get()), str(self.episode_max.get()), str(self.quality_select.get()[:-1])]
                    thewriter.writerow(params)
                print(str(params))
                print("Inserted [" + str(self.title.get()) + "] into resolved.csv!")

    def run_download(self):
        root.quit() # close window
        KissDownloader.init()

root = Tk()
app = App()
root.mainloop()
