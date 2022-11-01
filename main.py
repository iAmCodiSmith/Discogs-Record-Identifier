import requests

from user import *
from release import *
from gui import *
import discogs_client
import tkinter as tk
import webbrowser
# import urllib.error
# from urllib.error import HTTPError
from discogs_client.exceptions import HTTPError

def main():
    def open_authorization_link():
        webbrowser.open_new(d.get_authorize_url()[2])

    def login():
        verification_key = verification_key_field.get()
        root.destroy()
        try:
            token = d.get_access_token(verification_key)
            d.set_token(token[0], token[1])
            GUI(d)
            quit()
        except HTTPError as err:
            if str(401) in str(err):
              print(err)
        except:
            quit()
            print('Login Failed')



    def close():
        root.destroy()
        root.quit()

    global count
    d = discogs_client.Client('ExampleApplication/0.1', consumer_key='pqDFyUIGhdTlocdTPydh',
                              consumer_secret='GWQSLkJrnDEqTKZTSCDAAIXtzpnUCggU',
                              user_token='mUsNaktgcCFiQCvHqBfReytIxbJwSHxBtwzMFlTF'
                              )
    root = Tk()
    root.geometry('200x200')
    root.title('Discogs Record Identifier')


    login_frame=LabelFrame(root, borderwidth=5, padx=10, pady=10)
    open_authorization_link_button = Button(login_frame, text='Authorization Link', borderwidth=5, padx=10, pady=10, command=open_authorization_link)

    verification_frame = LabelFrame(root, text='Verification', borderwidth=5, padx=10, pady=10)
    verification_key_field = Entry(verification_frame, borderwidth=5)
    login_button = Button(verification_frame, text='Login', borderwidth=5, padx=10, pady=10, command=login)

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    login_frame.grid(row=0, column=0,sticky=NSEW)
    login_frame.rowconfigure(0, weight=1)
    login_frame.columnconfigure(0, weight=1)

    open_authorization_link_button.grid(row=0, column=0, sticky=NSEW)
    open_authorization_link_button.rowconfigure(0, weight=1)
    open_authorization_link_button.columnconfigure(0, weight=1)

    verification_frame.grid(row=1, column=0, sticky=EW)
    verification_frame.columnconfigure(0, weight=1)
    verification_frame.rowconfigure(0, weight=1)

    verification_key_field.grid(row=0, column=0, sticky=EW)

    login_button.grid(row=1, column=0)
    root.protocol("WM_DELETE_WINDOW", close)
    root.mainloop()

main()