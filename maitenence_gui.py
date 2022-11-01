from tkinter import *
from tkinter import ttk
import matplotlib
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pickle
from imgurpython import ImgurClient
from serpapi import GoogleSearch
import discogs_client

class Maitenence:
    def __init__(self, imgurClient, serp_params, discogs_connection):
        def test_imgur(imgurClient):
            try:
                ImgurClient(imgurClient.client_id, imgurClient.client_secret)
            except:
                self._imgur_health = False

        def test_serpapi(serp_params):
            results = GoogleSearch({'api_key':serp_params['api_key']}).get_dict()
            if 'Invalid API key' in results['error']:
                self._serpapi_health = False
            else:
                self._serpapi_health = True

        def test_discogs(identity):
            if str(type(identity)) in "<class 'discogs_client.models.User'>'" :
                self._discogs_health = True
            else:
                self._discogs_health = False

        def check_health():
            status_listbox.configure(state=NORMAL)
            test_imgur(imgurClient)
            if self._imgur_health:
                status_listbox.insert(0, 'Imgur API Connection: Working\n')
            else:
                status_listbox.insert(0, 'Imgur API Connection: Not Working\n')

            test_serpapi(serp_params)
            if self._serpapi_health:
                status_listbox.insert(0, '\nSerpAPI Connection: Working'+f'\n')
            else:
                status_listbox.insert(END, '\nSerpAPI Connection: Not Working\n')

            test_discogs(discogs_connection)
            if self._discogs_health:
                status_listbox.insert(END, '\n'+'Discogs API Connection: Working\n')
            else:
                status_listbox.insert(END, '\nDiscogs API Connection: Not Working\n')
            status_listbox.grid(row=0, column=0, sticky=NSEW)
            status_listbox.configure(state=DISABLED)
        def close():
            self._root.destroy()
            self._root.quit()

        self._root = Tk()
        self._root.title('Maitenence')
        self._root.geometry('300x200')
        self._root.grab_set()
        self._root.rowconfigure(0, weight=1)
        self._root.columnconfigure(0, weight=1)
        exit_button = Button(self._root, text='Exit', width=20, command=close)

        self._serpapi_health = True
        self._imgur_health = True
        self._discogs_health = True


        maitenence_frame = LabelFrame(self._root, padx=5, pady=5, text="API Connectivity", borderwidth=5)
        status_listbox = Listbox(maitenence_frame, borderwidth=10, font=10)

        maitenence_frame.grid(row=0, column=0, sticky=NSEW)
        maitenence_frame.rowconfigure(0, weight=1)
        maitenence_frame.columnconfigure(0, weight=1)
        status_listbox.grid(row=0, column=0, sticky=NSEW)
        status_listbox.configure(state=DISABLED)
        exit_button.grid(row=1, column=0, sticky=E)

        maitenence_frame.rowconfigure(0, weight=1)
        maitenence_frame.columnconfigure(0, weight=1)

        check_health()
        self._root.protocol("WM_DELETE_WINDOW", close)
        self._root.mainloop()