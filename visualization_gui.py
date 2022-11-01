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

class Visualization:
    def __init__(self, artist_data, past_searches):
        def visualization_one():
            vis_1_data=[]
            vis_1_artist_labels=[]
            for artist in reversed(artist_data):
                vis_1_data.append(artist.appearance_counter())
                vis_1_artist_labels.append(artist.artist_name())

            ind = np.arange(0,len(vis_1_artist_labels),1)
            fig, ax = plt.subplots(figsize=(4, 4),)
            x = ind
            y = vis_1_data
            N = 15

            def bar(pos):
                pos = int(pos)
                ax.clear()
                if pos + N > len(x):
                    n = len(x) - pos
                else:
                    n = N
                X = x[pos:pos + n]
                Y = y[pos:pos + n]
                ax.barh(X, Y, align='edge', ecolor='black')
                label_list=[]
                for i, txt in enumerate(Y):
                    ax.annotate(txt, (Y[i], X[i]))
                    label_list.append(vis_1_artist_labels[X[i]])
                if len(label_list) != 0:
                    ax.set_xticks(np.arange(max(vis_1_data)))
                    ax.axes.xaxis.set_visible(False)
                    ax.yaxis.set_major_locator(ticker.FixedLocator(X))
                    ax.set_yticklabels(label_list, fontsize=8)

            barpos = plt.axes([0, 0, 0.01, 1], facecolor="skyblue")
            slider = Slider(barpos, 'Barpos', 0, len(y) - N, valinit=100, orientation="vertical")
            self._slider = slider
            slider.on_changed(bar)
            bar(99)
            # plt.show()

            vis_1_canvas = FigureCanvasTkAgg(fig, visualization_one_frame,)
            vis_1_canvas.draw()
            vis_1_canvas.get_tk_widget()
            vis_1_canvas.get_tk_widget().grid(row=0, column=0, sticky=NSEW)
            vis_1_canvas.get_tk_widget().rowconfigure(0, weight=1)
            vis_1_canvas.get_tk_widget().columnconfigure(0, weight=1)

        # Visualization 2
        def visualization_two():
            appearances = set()
            for artist in artist_data:
                appearances.add(artist.appearance_counter())
            appearances_data = []
            appearances_list = []
            for appearance in appearances:
                appearances_data.append(0)
                appearances_list.append(appearance)
            for artist in artist_data:
                appearances_data[appearances_list.index(artist.appearance_counter())] += 1

            f = Figure(figsize=(4, 4), dpi=150)
            canvas = FigureCanvasTkAgg(f, visualization_two_frame, )
            ax = f.add_subplot(111)
            data = appearances_data
            ind = np.arange(len(appearances_data))
            width = .5
            ax.bar(ind, data, width)
            ax.set_xticks(np.arange(len(appearances_list)))
            ax.set_xticklabels(appearances_list,)
            ax.set_xlabel('Appearances')
            ax.set_ylabel('Artists With Appearance Count')
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0,padx=5, pady=5, sticky=NSEW)
            canvas.get_tk_widget().rowconfigure(0, weight=1)
            canvas.get_tk_widget().columnconfigure(0, weight=1)

        # Visualization 3
        def visualization_three():
            self._past_searches = []
            past_search_labels = set()
            explode = []
            for past_search in past_searches:
                past_search_labels.add(past_search.identified_color())
                self._past_searches.append(past_search)

            temp_labels = []
            for label in past_search_labels:
                temp_labels.append(label)
            past_search_labels = temp_labels
            past_search_count = []
            for i in range(len(past_search_labels)):
                past_search_count.append(0)
                explode.append(0)
            for past_search in past_searches:
                if past_search.identified_color() in past_search_labels:
                    past_search_count[past_search_labels.index(past_search.identified_color())] += 1

            labels = past_search_labels
            sizes = past_search_count
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            ax1.axis('equal')

            canvas = FigureCanvasTkAgg(fig1, visualization_three_frame)
            canvas.draw()
            canvas.get_tk_widget().rowconfigure(0, weight=1)
            canvas.get_tk_widget().columnconfigure(0, weight=1)
            canvas.get_tk_widget().grid(row=0, column=0,)

        def close():
            self._root.destroy()
            self._root.quit()

        self._root = Tk()
        self._root.title('Visualizations')
        self._root.geometry('800x800')
        self._root.grab_set()
        self._root.rowconfigure(0, weight=1)
        self._root.columnconfigure(0, weight=1)
        self._vis_1_canvas = None
        self._slider = None
        exit_button = Button(self._root, text='Exit', width=20, command=close)
        tabControl = ttk.Notebook(self._root)

        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tab3 = ttk.Frame(tabControl)

        tabControl.add(tab1, text='Release Amount Per Artist')
        tabControl.add(tab2, text='Artist Appearances')
        tabControl.add(tab3, text='Color Identification Result Frequency')

        visualization_one_frame = LabelFrame(tab1,padx=5, pady=5, borderwidth=5)
        visualization_two_frame = LabelFrame(tab2, padx=5, pady=5, borderwidth=5)
        visualization_three_frame = LabelFrame(tab3, padx=5, pady=5, borderwidth=5)

        tabControl.grid(row=0, column=0, sticky=NSEW)
        exit_button.grid(row=1, column=0, sticky=E)
        tabControl.rowconfigure(0, weight=1)
        tabControl.columnconfigure(0, weight=1)
        tab1.rowconfigure(0, weight=1)
        tab1.columnconfigure(0, weight=1)
        tab2.rowconfigure(0, weight=1)
        tab2.columnconfigure(0, weight=1)
        tab3.rowconfigure(0, weight=1)
        tab3.columnconfigure(0, weight=1)

        visualization_one_frame.grid(row=0, column=0, sticky=NSEW)
        visualization_one_frame.rowconfigure(0, weight=1)
        visualization_one_frame.columnconfigure(0, weight=1)
        visualization_two_frame.grid(row=0, column=0,)
        visualization_two_frame.rowconfigure(0, weight=1)
        visualization_two_frame.columnconfigure(1, weight=1)
        visualization_three_frame.grid(row=0, column=0,)
        visualization_three_frame.rowconfigure(0, weight=1)
        visualization_three_frame.columnconfigure(1, weight=1)

        visualization_one()
        visualization_two()
        visualization_three()

        self._root.protocol("WM_DELETE_WINDOW", close)
        self._root.mainloop()