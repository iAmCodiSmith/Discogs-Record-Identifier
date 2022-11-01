from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk

import record_identifier
import user
from user import *
from release import *
from record_identifier import getArtistAlbum, getRecordColor, theTrueSearch
import webbrowser
from visualization_gui import Visualization
from maitenence_gui import Maitenence


# root layer
class GUI:
    def __init__(self, d):
        def run_cover_identifier():
            the_common_words = getArtistAlbum(cover_file_path.get())
            return the_common_words

        def runMediaIdentifier():
            identified_color, prediction_accuracy = getRecordColor(media_file_path.get())
            win = tk.Toplevel()
            win.geometry('400x100')
            win.wm_title("Prediction Evaluation")
            win.columnconfigure(0, weight=1)
            win.rowconfigure(0, weight=1)
            win.grab_set()
            prediction_entry = Entry(win,)
            prediction_entry.insert(0, prediction_accuracy)
            prediction_entry.grid(row=0,column=0, sticky=NSEW)
            return identified_color

        def runDiscogsFinder():
            if cover_file_path.get() != '' and media_file_path.get() != '':
                common_words = run_cover_identifier()
                identified_color = runMediaIdentifier()
                query, master_image, first_choice, this_search = theTrueSearch(common_words, identified_color,
                                                                               self._cover_preview_image,
                                                                               self._media_preview_image,
                                                                               self._d)
                the_data.saveSearch(this_search)
                getAlbumArt(master_image)
                if first_choice:
                    updateInformationBox(first_choice)
                    update_search_results(this_search.found_releases(), this_search.search_query())
                else:
                    win = tk.Toplevel()
                    win.geometry('400x100')
                    win.wm_title("No Discogs Release Entries Found")
                    win.columnconfigure(0, weight=1)
                    win.rowconfigure(0, weight=1)
                    win.grab_set()
                    prediction_entry = Entry(win, )
                    prediction_entry.insert(0, "No Discogs Release Entries Found")
                    prediction_entry.grid(row=0, column=0, sticky=NSEW)

        def add_to_collection():
            def add_this_release():
                allfolders = d.user(d.identity().username).collection_folders
                for folder in allfolders:
                    if folder.name == 'Uncategorized':
                        folder_index = allfolders.index(folder)
                        try:
                            allfolders[folder_index].add_release(release.release_number())
                            self._current_user_collection.append(release)
                            self._current_user_collection = sorted(self._current_user_collection, key=lambda x: x.artist_name(), reverse=True)
                            updateUserCollection()
                            the_data.current_user.getCollectionReleaseNumbers().append(release.release_number())
                            win.destroy()
                        except Exception as e:
                            print(e)
            selection = self._search_results_listbox.curselection()
            if selection:
                release_number = self._search_results_listbox.get(selection[0])[
                                 self._search_results_listbox.get(selection[0]).index("Number: ") + 8:]

                if release_number not in the_data.current_user.getCollectionReleaseNumbers():
                    release = the_data.getRelease(release_number)
                    win = tk.Toplevel()
                    win.geometry('500x200')
                    win.wm_title("Cannot Add")
                    win.grab_set()
                    release_to_add_frame = LabelFrame(win, text="Adding Release...")
                    release_to_add_buttons_frame = Frame(win)

                    adding_art_placeholder = Label(release_to_add_frame)
                    master_image = release.master_image()
                    img_width, img_height = master_image.size
                    while img_width > 150 or img_height > 150:
                        master_image = master_image.resize(size=(int(img_width / 2), int(img_height / 2)))
                        img_width, img_height = master_image.size
                    master_image = master_image.resize(size=(150, 150))
                    album_art_image = ImageTk.PhotoImage(master_image)
                    adding_art_placeholder.configure(image=album_art_image)
                    adding_art_placeholder.image = album_art_image
                    status_field = Listbox(release_to_add_frame, borderwidth=5, )
                    items = [f'Artist: {release.artist_name()}', f'Album: {release.album_name()}',
                             f'Release Number: {release.release_number()}'
                        , f'Master Release: {release.master_release_number()}', f'Media Color: {release.media_color()}',
                             f'Media Format: {release.media_format()}']
                    for item in reversed(items):
                        if item != None:
                            remove_char = ["_", "<", ">"]
                            for each_char in remove_char:
                                item = item.replace(each_char, " ")
                            item = item.title()
                            status_field.insert(0, item)
                    status_field.configure(state=DISABLED)
                    exit_button = Button(release_to_add_buttons_frame, text='Cancel', command=win.destroy)
                    add_button = Button(release_to_add_buttons_frame, text='Add Release', command=add_this_release)
                    win.columnconfigure(0, weight=1)
                    win.rowconfigure(0, weight=1)
                    release_to_add_frame.grid(row=0, column=0, sticky=NSEW)
                    release_to_add_frame.columnconfigure(1, weight=1)
                    release_to_add_frame.rowconfigure(0, weight=1)
                    release_to_add_buttons_frame.grid(row=1, column=0)
                    adding_art_placeholder.grid(row=0, column=0)
                    status_field.grid(row=0, column=1, sticky=NSEW)
                    status_field.columnconfigure(1, weight=1)
                    status_field.rowconfigure(0, weight=1)
                    exit_button.grid(row=0, column=0, sticky=EW)
                    add_button.grid(row=0, column=1, sticky=EW)
                else:
                    win = tk.Toplevel()
                    win.geometry('300x100')
                    win.resizable(width=False, height=False)
                    win.wm_title("Cannot Add")
                    win.grab_set()
                    already_label = Label(win, text="Release Already In Collection")
                    exit_button = Button(win, text='Cancel', command=win.destroy)
                    win.columnconfigure(0, weight=1)
                    win.rowconfigure(0, weight=1)
                    already_label.grid(row=0, column=0, sticky=NSEW)
                    already_label.columnconfigure(0, weight=1)
                    already_label.rowconfigure(0, weight=1)
                    exit_button.grid(row=1, column=0, sticky=EW)

        def update_search_results(found_releases, query):
            query = query.replace('"Discogs"', "")
            query = query.replace('vinyl', "")

            search_results_frame = LabelFrame(preview_frame, padx=20, pady=20, text=f'Current Search: {query}')
            search_results_listbox = Listbox(search_results_frame, width=50, borderwidth=5)
            self._search_results_listbox = search_results_listbox
            search_results_buttons_frame = Frame(search_results_frame)
            past_search_window_button = Button(search_results_buttons_frame, text='Open Past Searches',
                                               command=openPastSearches)
            add_release_button = Button(search_results_buttons_frame, text='Add To Collection',
                                        command=add_to_collection)
            for release in reversed(found_releases):
                info = f'{release.artist_name()} - {release.album_name()}, ' \
                       f'{release.media_color()} {release.media_format()}, ' \
                       f'|| Release Number: {release.release_number()}'
                remove_char = ["_", "<", ">"]
                for each_char in remove_char:
                    info = info.replace(each_char, " ")
                    info = info.title()
                search_results_listbox.insert(0, info)
                if release.release_number() not in the_data.allReleaseNumbers():
                    the_data.allReleases().append(release)
            search_results_listbox.bind("<<ListboxSelect>>", callback)
            search_results_frame.grid(row=2, column=0, )
            search_results_listbox.grid(row=0, column=0, )
            search_results_buttons_frame.grid(row=1, column=0)
            search_results_buttons_frame.columnconfigure(0, weight=1)
            past_search_window_button.grid(row=0, column=0, sticky=EW)
            add_release_button.grid(row=0, column=1, sticky=EW)

        def getAlbumArt(master_image):
            if master_image != None:
                img_width, img_height = master_image.size
                while img_width > 150 or img_height > 150:
                    master_image = master_image.resize(size=(int(img_width / 2), int(img_height / 2)))
                    img_width, img_height = master_image.size
                    master_image = master_image.resize(size=(150, 150))
                album_art_image = ImageTk.PhotoImage(master_image)
                album_art_image_placeholder.configure(image=album_art_image)
                album_art_image_placeholder.image = album_art_image
                album_art_image_placeholder.grid(row=0, column=0)

        def callback(event):
            selection = event.widget.curselection()
            if selection:
                release_number = event.widget.get(selection[0])[event.widget.get(selection[0]).index("Number: ") + 8:]
                this_release = the_data.getRelease(release_number)
                updateInformationBox(this_release)

        def updateInformationBox(release):
            if release != None:
                status_field = Listbox(current_release_frame, width=80, borderwidth=5, )
                items = [f'Artist: {release.artist_name()}', f'Album: {release.album_name()}',
                         f'Release Number: {release.release_number()}'
                    , f'Master Release: {release.master_release_number()}', f'Media Color: {release.media_color()}',
                         f'Media Format: {release.media_format()}']
                for item in reversed(items):
                    if item != None:
                        remove_char = ["_", "<", ">"]
                        for each_char in remove_char:
                            item = item.replace(each_char, " ")
                        item = item.title()
                        status_field.insert(0, item)
                status_field.configure(state=DISABLED)
                status_field.grid(row=0, column=1, sticky=NSEW)
                getAlbumArt(release.master_image())

        def unique(list1):
            # initialize a null list
            unique_list = []
            # traverse for all elements
            for x in list1:
                # check if exists in unique_list or not
                if x not in unique_list:
                    unique_list.append(x)
            return unique_list

        def updateUserCollection():
            search_string = self._search_field.get()
            user_collection_frame = LabelFrame(path_and_info_frame, padx=20, pady=20, text='User Collection',
                                               height=110, width=130)
            search_frame = Frame(user_collection_frame)
            search_button = Button(search_frame, text='Search', width=10, padx=5, pady=5, borderwidth=5, command=search_update_collection)
            search_field = Entry(search_frame, borderwidth=5, width=105,)
            search_field.delete(0, END)
            search_field.insert(0, search_string)
            self._search_field = search_field
            user_collection_list_frame = Frame(user_collection_frame)
            user_collection_list = Listbox(user_collection_list_frame, width=120, borderwidth=5, selectmode=SINGLE)
            user_collection_list.bind("<<ListboxSelect>>", callback)
            user_collection_x_scrollbar = Scrollbar(user_collection_list_frame, orient='horizontal', )
            user_collection_y_scrollbar = Scrollbar(user_collection_list_frame, orient='vertical', )

            for release in to_order:
                info = f'{release.artist_name()} - {release.album_name()}, ' \
                       f'{release.media_color()} {release.media_format()}, ' \
                       f'|| Release Number: {release.release_number()}'
                remove_char = ["_", "<", ">"]
                for each_char in remove_char:
                    info = info.replace(each_char, " ")
                info = info.title()
                user_collection_list.insert(0, info)

            user_collection_frame.grid(row=2, column=0, columnspan=4)
            search_frame.grid(row=0, column=0, sticky=EW, columnspan=3)
            search_frame.grid_columnconfigure(0, weight=1)
            search_button.grid(row=0, column=0, sticky=W)
            search_field.grid(row=0, column=1, sticky=EW, columnspan=2)
            user_collection_list_frame.grid(row=1, column=0, )
            user_collection_y_scrollbar.grid(row=0, column=0, columnspan=1, sticky=N + S)
            user_collection_list.grid(row=0, column=1, )
            user_collection_x_scrollbar.grid(row=1, column=1, columnspan=1, sticky=E + W)

            user_collection_list.config(xscrollcommand=user_collection_x_scrollbar.set)
            user_collection_x_scrollbar.config(command=user_collection_list.xview)
            user_collection_list.config(yscrollcommand=user_collection_y_scrollbar.set)
            user_collection_y_scrollbar.config(command=user_collection_list.yview)

        def search_update_collection():
            search_string = self._search_field.get()
            user_collection_frame = LabelFrame(path_and_info_frame, padx=20, pady=20, text='User Collection',
                                               height=110, width=130)
            search_frame = Frame(user_collection_frame)
            search_button = Button(search_frame, text='Search', width=10, padx=5, pady=5, borderwidth=5, command=search_update_collection)
            search_field = Entry(search_frame, borderwidth=5, width=105,)
            search_field.delete(0, END)
            search_field.insert(0, search_string)
            self._search_field = search_field
            user_collection_list_frame = Frame(user_collection_frame)
            user_collection_list = Listbox(user_collection_list_frame, width=120, borderwidth=5, selectmode=SINGLE)
            user_collection_list.bind("<<ListboxSelect>>", callback)
            user_collection_x_scrollbar = Scrollbar(user_collection_list_frame, orient='horizontal', )
            user_collection_y_scrollbar = Scrollbar(user_collection_list_frame, orient='vertical', )


            if len(self._current_user_collection) != 0:
                found = []
                for release in self._current_user_collection:
                    if search_string.lower() in release.artist_name().lower():
                        found.append(release)

                for release in found:
                        info = f'{release.artist_name()} - {release.album_name()}, ' \
                               f'{release.media_color()} {release.media_format()}, ' \
                               f'|| Release Number: {release.release_number()}'
                        remove_char = ["_", "<", ">"]
                        for each_char in remove_char:
                            info = info.replace(each_char, " ")
                        info = info.title()
                        user_collection_list.insert(0, info)
                    # else:
                    #     user_collection_list.insert(0, release_number)
                user_collection_frame.grid(row=2, column=0, columnspan=4)
                search_frame.grid(row=0, column=0, sticky=EW, columnspan=3)
                search_frame.grid_columnconfigure(0, weight=1)
                search_button.grid(row=0, column=0, sticky=W)
                search_field.grid(row=0, column=1, sticky=EW, columnspan=2)
                user_collection_list_frame.grid(row=1, column=0, )
                user_collection_y_scrollbar.grid(row=0, column=0, columnspan=1, sticky=N + S)
                user_collection_list.grid(row=0, column=1, )
                user_collection_x_scrollbar.grid(row=1, column=1, columnspan=1, sticky=E + W)

                user_collection_list.config(xscrollcommand=user_collection_x_scrollbar.set)
                user_collection_x_scrollbar.config(command=user_collection_list.xview)
                user_collection_list.config(yscrollcommand=user_collection_y_scrollbar.set)
                user_collection_y_scrollbar.config(command=user_collection_list.yview)

        def open_search_release_link():
            selection = self._search_results_listbox.curselection()
            if selection:
                release_number = self._search_results_listbox.get(selection[0])[
                                 self._search_results_listbox.get(selection[0]).index("Number: ") + 8:]
                url = 'www.discogs.com/release/'+release_number
                webbrowser.open_new(url)

        def openPastSearches():
            def get_selected_past_release():
                selection = past_search_list_box.curselection()
                if selection:
                    date = past_search_list_box.get(selection[0])
                    date = date[:date.index(' - ')]
                    for past_search in the_data.pastSearches():
                        if date == past_search.search_date():
                            current_past_search = past_search
                            update_search_results(current_past_search.found_releases(),
                                                  current_past_search.search_query())
                            cover_image = ImageTk.PhotoImage(current_past_search.cover_art())
                            cover_preview_image_placeholder.configure(image=cover_image)
                            cover_preview_image_placeholder.image = cover_image

                            media_image = ImageTk.PhotoImage(current_past_search.media_art())
                            media_preview_image_placeholder.configure(image=media_image)
                            media_preview_image_placeholder.image = media_image
                            media_file_path.configure(state=NORMAL)
                            media_file_path.delete(0, "end")
                            media_file_path.configure(state=DISABLED)
                            cover_file_path.configure(state=NORMAL)
                            cover_file_path.delete(0, "end")
                            cover_file_path.configure(state=DISABLED)
                win.destroy()

            win = tk.Toplevel()
            win.geometry('300x300')
            win.wm_title("Window")
            win.grab_set()
            past_search_frame = Frame(win, borderwidth=5)
            past_search_list_box = Listbox(past_search_frame)
            past_search_select_button = Button(past_search_frame, text='Select', command=get_selected_past_release)
            for past_search in the_data.pastSearches():
                query = past_search.search_query()
                query = query.replace('"Discogs"', "")
                query = query.replace('vinyl', "")
                past_search = past_search.search_date() + ' - ' + query
                past_search_list_box.insert(0, past_search)
            win.columnconfigure(0, weight=1)
            win.rowconfigure(0, weight=1)
            past_search_frame.grid(row=0, column=0, sticky=NSEW)
            past_search_frame.columnconfigure(0, weight=1)
            past_search_frame.rowconfigure(0, weight=1)
            past_search_list_box.grid(row=0, column=0, sticky=NSEW)
            past_search_select_button.grid(row=1, column=0, sticky=EW)

        def open_visualizations():
            all_releases = []
            all_artists = []
            to_remove = []
            to_fix = []
            all_artists_with_count = []
            for release in self._current_user_collection:
                all_releases.append(release)
                all_artists.append(release.artist_name())
            all_artists = unique(all_artists)
            all_artists = sorted(all_artists, key=lambda x: x, reverse=True)

            for artist in all_artists:
                if "<Artist" in artist or "Artist>" in artist or "'>" in artist:
                    to_remove.append((artist))
            for artist in to_remove:
                all_artists.remove(artist)

            for artist in all_artists:
                if '>' in artist:
                    to_fix.append(artist)
            for artist in to_fix:
                all_artists.remove(artist)
                artist = artist.replace('>', '')
                artist = artist.replace('"', '')
                all_artists.append(artist)

            for artist in all_artists:
                all_artists_with_count.append(Artist(artist))
            all_artists = all_artists_with_count

            for i in range(len(all_artists)):
                for release in all_releases:
                    if all_artists[i].artist_name() in release.artist_name():
                        all_artists[i].appearance_counter(all_artists[i].appearance_counter() + 1)

            all_artists = sorted(all_artists, key=lambda x: x.appearance_counter(), reverse=True)
            self._root.withdraw()
            Visualization(all_artists, the_data.pastSearches())
            self._root.deiconify()

        def open_maitenence_tool():
            self._root.withdraw()
            Maitenence(record_identifier.imgur_client(), record_identifier.get_serp_params(), self._d.identity())
            self._root.deiconify()

        def getCoverFilePath():
            Tk().withdraw()
            cover_filename = askopenfilename(initialdir="test_files/",
                                             title="Select Cover File",
                                             filetypes=[
                                                 ('image files', ('.png', '.jpg', '.jpeg')),
                                             ])  # show an "Open" dialog box and return the path to the selected image
            cover_file_path.configure(state=NORMAL)
            cover_file_path.delete(0, "end")
            cover_file_path.insert(0, cover_filename)
            cover_file_path.configure(state=DISABLED)
            try:
                cover_preview_image = Image.open(cover_filename)
                img_width, img_height = cover_preview_image.size
                while img_height > 250 or img_width > 250:
                    cover_preview_image = cover_preview_image.resize(size=(int(img_width / 2), int(img_height / 2)))
                    img_width, img_height = cover_preview_image.size
                self._cover_preview_image = cover_preview_image.resize(size=(150, 150))

                cover_image = ImageTk.PhotoImage(cover_preview_image)
                cover_preview_image_placeholder.configure(image=cover_image)
                cover_preview_image_placeholder.image = cover_image
                cover_preview_image_placeholder.grid(row=1, column=0)
            except:
                print()

        def get_media_filepath():
            Tk().withdraw()
            media_filename = askopenfilename(
                initialdir="test_files/",
                title="Select Media File",
                filetypes=[
                           ('image files', ('.png', '.jpg', '.jpeg')),
                           ])
            media_file_path.configure(state=NORMAL)
            media_file_path.delete(0, "end")
            media_file_path.insert(0, media_filename)
            media_file_path.configure(state=DISABLED)
            try:
                media_preview_image = Image.open(media_filename)
                img_width, img_height = media_preview_image.size
                while img_width > 150 or img_height > 150:
                    media_preview_image = media_preview_image.resize(size=(int(img_width / 2), int(img_height / 2)))
                    img_width, img_height = media_preview_image.size
                self._media_preview_image = media_preview_image.resize(size=(150, 150))
                media_image = ImageTk.PhotoImage(media_preview_image)
                media_preview_image_placeholder.configure(image=media_image)
                media_preview_image_placeholder.image = media_image
                media_preview_image_placeholder.grid(row=3, column=0)
            except:
                print()

        def close():
            self._root.destroy()
            self._root.quit()

        self._root = Tk()
        self._d = d
        the_data = DataStructure(d)
        self._username = d.identity().username
        self._root.title('Record Indentifier')
        self._cover_preview_image = None
        self._media_preview_image = None
        self._current_past_search = None
        self._media_filename = ''
        self._search_results_listbox = None
        self._current_user_collection = None
        release_numbers = the_data.current_user.getCollectionReleaseNumbers()
        if release_numbers != None:
            to_order = []
            for release_number in unique(release_numbers):
                if release_number in the_data.allReleaseNumbers():
                    release = the_data.getRelease(release_number)
                    to_order.append(release)
            to_order = sorted(to_order, key=lambda x: x.artist_name(), reverse=True)
            self._current_user_collection = to_order


        self._search_field = None

        # Create Widgets for GUI
        preview_frame = LabelFrame(self._root, padx=20, pady=20, )
        preview_frame.grid_rowconfigure(0, minsize=200)
        preview_frame.grid_columnconfigure(0, minsize=200)
        # preview_frame.geometry("250X520")
        path_and_info_frame = LabelFrame(self._root, padx=20, pady=20, )
        path_frame = LabelFrame(path_and_info_frame, padx=20, pady=20, text="PATH FRAME")
        # results_frame = LabelFrame(path_and_info_frame, padx=20, pady=20, text='RESULTS FRAME', height=120, width=140)

        album_info_frame = LabelFrame(self._root, padx=20, pady=20, text='ALBUM INFO FRAME')

        # cover_frame = LabelFrame(preview_frame, padx=20, pady=20)
        cover_preview_frame = LabelFrame(preview_frame, text="Cover Preview", padx=10, pady=10)
        cover_preview_image_placeholder = Label(cover_preview_frame, )
        cover_preview_image = Image.open('application_files/image_unavailable.png')
        img_width, img_height = cover_preview_image.size
        while img_height > 250 or img_width > 250:
            cover_preview_image = cover_preview_image.resize(size=(int(img_width / 2), int(img_height / 2)))
            img_width, img_height = cover_preview_image.size
        cover_preview_image = cover_preview_image.resize(size=(150, 150))
        cover_image = ImageTk.PhotoImage(cover_preview_image)
        cover_preview_image_placeholder.configure(image=cover_image)
        cover_preview_image_placeholder.image = cover_image
        cover_file_path_frame = LabelFrame(path_frame, text="Cover File Path", font=("bold"), )
        cover_file_path = Entry(cover_file_path_frame, borderwidth=5, )
        cover_file_path.configure(state=DISABLED)
        cover_select_button = Button(cover_file_path_frame, text="Select File", padx=20, borderwidth=5,
                                     command=getCoverFilePath)

        media_preview_frame = LabelFrame(preview_frame, text="Media Preview", padx=10, pady=10)
        media_preview_image_placeholder = Label(media_preview_frame, )
        media_preview_image = Image.open('application_files/image_unavailable.png')
        img_width, img_height = media_preview_image.size
        while img_width > 150 or img_height > 150:
            media_preview_image = media_preview_image.resize(size=(int(img_width / 2), int(img_height / 2)))
            img_width, img_height = media_preview_image.size
        media_preview_image = media_preview_image.resize(size=(150, 150))
        media_image = ImageTk.PhotoImage(media_preview_image)
        media_preview_image_placeholder.configure(image=media_image)
        # media_preview_image_placeholder.image = media_preview_image
        media_file_path_frame = LabelFrame(path_frame, text="Media File Path", font=("bold"))
        media_select_button = Button(media_file_path_frame, text="Select File", padx=20, borderwidth=5,
                                     command=get_media_filepath)
        media_file_path = Entry(media_file_path_frame, borderwidth=5, )
        media_file_path.configure(state=DISABLED)

        # Past Search LabelFrame
        search_results_frame = LabelFrame(preview_frame, padx=20, pady=20, text='Current Search:')
        search_results_listbox = Listbox(search_results_frame, width=50, borderwidth=5)
        self._search_results_listbox = search_results_listbox
        search_results_buttons_frame = Frame(search_results_frame)
        past_search_window_button = Button(search_results_buttons_frame, text='Open Past Searches',
                                           command=openPastSearches)
        add_release_button = Button(search_results_buttons_frame, text='Add To Collection')
        # Visualization Button
        tool_buttons_frame = LabelFrame(path_and_info_frame, padx=20, pady=20)
        visualizations_button = Button(tool_buttons_frame, text='Visualizations', padx=20, pady=20,
                                       command=open_visualizations)
        maitenence_tool_button = Button(tool_buttons_frame, text='Maitenence Tool', padx=20, pady=20,
                                        command=open_maitenence_tool)
        # Maitenence Button

        # Current Release Frame
        current_release_frame = LabelFrame(path_and_info_frame, text='Current Release Info')
        album_art_frame = LabelFrame(current_release_frame, text="Album Art", padx=10, pady=10)
        album_art_image_placeholder = Label(album_art_frame, )
        album_art_image = Image.open('application_files/image_unavailable.png')
        img_width, img_height = album_art_image.size
        while img_width > 150 or img_height > 150:
            album_art_image = album_art_image.resize(size=(int(img_width / 2), int(img_height / 2)))
            img_width, img_height = album_art_image.size
        album_art_image = album_art_image.resize(size=(150, 150))
        album_art_image = ImageTk.PhotoImage(album_art_image)
        album_art_image_placeholder.configure(image=album_art_image)
        album_art_image_placeholder.image = media_preview_image

        # text field
        status_field_label = Label(current_release_frame, text="Information", font="bold", justify=LEFT)
        status_field = Entry(current_release_frame, width=50, borderwidth=5)
        status_field.delete(0, "end")
        status_field.insert(0, ".....")
        status_field.configure(state=DISABLED)

        # Collection
        user_collection_frame = LabelFrame(path_and_info_frame, padx=20, pady=20, text='User Collection', height=110,
                                           width=130)
        search_frame = Frame(user_collection_frame)
        search_button = Button(search_frame, text='Search', padx=5, pady=5, borderwidth=5, command=search_update_collection)
        search_field = Entry(search_frame, borderwidth=5,)
        self._search_field = search_field
        user_collection_list_frame = Frame(user_collection_frame)
        user_collection_list = Listbox(user_collection_list_frame, width=120, borderwidth=5, selectmode=SINGLE)
        user_collection_list.bind("<<ListboxSelect>>", callback)
        user_collection_x_scrollbar = Scrollbar(user_collection_list_frame, orient='horizontal', )
        user_collection_y_scrollbar = Scrollbar(user_collection_list_frame, orient='vertical', )

        program_buttons_frame = LabelFrame(preview_frame, padx=20, pady=20)

        link_button = Button(program_buttons_frame, text="Link", padx=15, borderwidth=5, command=open_search_release_link)
        run_button = Button(program_buttons_frame, text="Run", padx=15, borderwidth=5, command=runDiscogsFinder)
        exit_button = Button(program_buttons_frame, text="Exit", padx=15, borderwidth=5, command=close)


        # Grid
        preview_frame.grid(row=0, column=0, padx=10, pady=10, sticky=NSEW)
        cover_preview_frame.grid(row=0, column=0, padx=10, pady=10, )

        cover_preview_image_placeholder.grid(row=0, column=0)

        media_preview_frame.grid(row=1, column=0, padx=10, pady=10, )
        media_preview_frame.columnconfigure(0, weight=1)
        media_preview_image_placeholder.grid(row=0, column=0)

        # Path and Info Frame
        # Path Frame
        path_and_info_frame.grid(row=0, column=1, padx=10, pady=10, sticky=NSEW)
        path_frame.grid(row=0, column=0, sticky=EW)
        path_frame.columnconfigure(0, weight=1)
        cover_file_path_frame.grid(row=0, column=0, sticky=EW)
        cover_file_path_frame.columnconfigure(0, weight=1)
        cover_file_path.grid(row=0, column=0, sticky=EW)
        cover_select_button.grid(row=0, column=1)
        media_file_path_frame.grid(row=1, column=0, sticky=EW)
        media_file_path_frame.columnconfigure(0, weight=1)
        media_file_path.grid(row=0, column=0, sticky=EW)
        media_select_button.grid(row=0, column=1)

        search_results_frame.grid(row=2, column=0, )
        search_results_listbox.grid(row=0, column=0, )
        search_results_buttons_frame.grid(row=1, column=0)
        search_results_buttons_frame.columnconfigure(0, weight=1)
        past_search_window_button.grid(row=0, column=0, sticky=EW)
        add_release_button.grid(row=0, column=1, sticky=EW)

        tool_buttons_frame.grid(row=3, column=0, sticky=EW)
        tool_buttons_frame.columnconfigure(0, weight=1)
        tool_buttons_frame.columnconfigure(1, weight=1)
        visualizations_button.grid(row=0, column=0, sticky=EW)
        maitenence_tool_button.grid(row=0, column=1, sticky=EW)

        # Results Frame
        # results_frame.grid(row=1, column=0)
        current_release_frame.grid(row=1, column=0, sticky=EW)
        current_release_frame.columnconfigure(1, weight=1)

        # User Collection List
        user_collection_frame.grid(row=2, column=0)
        search_frame.grid(row=0, column=0, sticky=W + E)
        search_button.grid(row=0, column=0, )
        search_field.grid(row=0, column=1, sticky=W + E)
        user_collection_list_frame.grid(row=1, column=0, )
        user_collection_y_scrollbar.grid(row=0, column=0, sticky=N + S)
        user_collection_list.grid(row=0, column=1, )
        user_collection_x_scrollbar.grid(row=1, column=1, sticky=E + W)
        user_collection_list.config(xscrollcommand=user_collection_x_scrollbar.set,
                                    yscrollcommand=user_collection_y_scrollbar.set)
        user_collection_x_scrollbar.config(command=user_collection_list.xview)
        # user_collection_list.config()
        user_collection_y_scrollbar.config(command=user_collection_list.yview)

        # Album Art Frame
        album_info_frame.grid(row=0, column=0)
        album_art_frame.grid(row=0, column=0, padx=10, pady=10)
        album_art_image_placeholder.grid(row=0, column=0)

        # status_field_label.grid(row=0, column=1)
        status_field.grid(row=0, column=1, sticky=NSEW)

        # User Collection List Box

        # Buttons Frame
        program_buttons_frame.grid(row=3, column=0, sticky=NSEW)
        program_buttons_frame.columnconfigure(0, weight=1)
        program_buttons_frame.columnconfigure(1, weight=1)
        program_buttons_frame.columnconfigure(2, weight=1)
        link_button.grid(row=0, column=0, sticky=NSEW)
        run_button.grid(row=0, column=1, sticky=NSEW)
        exit_button.grid(row=0, column=2, sticky=NSEW)
        # Fill user collection at launch
        updateUserCollection()

        # Set program to terminate when window is closed.
        self._root.protocol("WM_DELETE_WINDOW", close)
        self._root.mainloop()