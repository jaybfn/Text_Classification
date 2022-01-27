#!/usr/bin/env python
# coding: utf-8

# # Importing all the necessary libraries for scraping lyrics
try:

    import requests
    from requests.exceptions import ConnectionError
    from bs4 import BeautifulSoup
    import pprint
    import re
    import os
    import pandas as pd
    import argparse
    from argparse import ArgumentParser
    import sys

    # ## Defining a function to extract song names

    def get_song_name(List):
        
        """ This function has multiple parts:
            It need an input 'List'is a list of all table row tags from an artists page.
            steps:
            1. extracts text from the tag which contains song name
            2. removes any text which is enclosed in '()' and '[]' 
            3. removes any special characters within the text
            4. Concatinates'.txt' as a file extension to song name
            5. Removes duplicate filenames form the file
            """
        
        song_name = []
        for name in List:
            name = name.get_text() 
            song_name.append(name)
        # regex pattern to extract parenthesis and square bracket with texts store in them
        Song_Name_pattern = '[\(\[].*?[\)\]]'   
        file_names_list =[]
        for i in song_name:
            file_names = re.sub(pattern=Song_Name_pattern, string= i, repl=""  )
            file_names_list.append(file_names)
        
        # to remove special character from the text    
        character = '[^0-9a-zA-Z]' 
        final_file_name = []
        for i in file_names_list:
        
            file_names_final = re.sub(pattern=character, string= i, repl=""  )
            final_file_name.append(file_names_final)
        
        # generating a list of filename with .txt extension
        filenames = [] 
        for name in final_file_name:
            filename =name+'.txt'
            filenames.append(filename)

        # removes duplicate songs.
        #filenames = list(set(filenames))
        return filenames

    # ## Lyrics Extraction from Lyrics.com and save each lyrics into individual 'songname.txt'

    parser = ArgumentParser(description='this program returns all the lyrics for given artist') # initialization

    header = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
    URL = 'https://www.lyrics.com/' #to scrap lyrics from this page
    page = requests.get(URL, headers=header)

    #************************************************************************
    # this part of codes prompts user to input 2 parameters:
    # 1. how many artist lyrics he wants to scrap.
    # 2. Entering the artist names as shown in the webpage of lyrics.com.
    # Also the user can control the number of artist he want to scrap even after entering a particular number during 
    # the first prompt. 
        # eg: A user wish to enter 5 artist name, so he types in 5 during the first prompt, then the program starts asking the user
            # to enter the artist name one by one, in case he wants to only have 3 artist lyrics to be scraped while entering the 
            # artist's name, then he can type 'x' on the next prompt to exit the loop
    #*************************************************************************       


    #parser.add_argument('number_of_artist',help="enter number of artist lyrics to be scraped")
#
    parser.add_argument("quantity",default = 1, help="enter number of artist lyrics to be scraped",type=int) # now --quantity is optional
    parser.add_argument("list_Artist", nargs="+", default=['Akon'])
    args = parser.parse_args()

    number_of_artists = args.quantity
    artistlist = args.list_Artist
    
    search = 'artist'    

    #artistlist = ['CKay','Curtis-Mayfield']#input the artist names as metioned in the lyrics.com
    artistlist_path =['/'+ item for item in artistlist]#concatinates '/'to the artist names for accessing the html page

    #********************************************************************************
    #number_of_artists = (int(input(f'How many artists lyrics you want to scrap:')))

    # artistlist = []
    # for i in range(number_of_artists):
    #     j = i+1
    #     name = str(input(f'Artist_{j}:'))
    #     if name != 'x':
    #         artistlist.append(name)
    #     else:
    #         break

    #artistname_folder = [ch.replace("/", "") for ch in artistlist]#
    #********************************************************************************

    # for loop for extracting all the lyrics links for artist names
    for folder_path, folder_name in zip(artistlist_path, artistlist):
        #*****************************************************************************
        # this part of the code makes a directory with artist names and also checks if directory already exists or not
        
        if os.path.isdir(folder_name):
            path = os.getcwd()+folder_path 
            os.chdir(path)
            #pass
        else:
            directory = os.mkdir(folder_name) #creates a folder with artist name
            path = os.getcwd()+folder_path 
            os.chdir(path)
        #*****************************************************************************
        
        response = requests.get(URL+search+folder_path, headers=header)
        get_a_tag = response.text # extract text from the html file
        cont = response.content
        soup = BeautifulSoup(cont, 'html.parser') # to soupout all the content 
        tag = soup.find_all('td', {'class':'tal qx'}) # to extract a particular tag from a html page which contains the link to the lyrics
        
        # regex for extracting the link
        pattern = '\/lyric\/\w+[^"]+' 
        links = re.findall(pattern=pattern,string=get_a_tag,flags=re.IGNORECASE ) # function to find all the links in the html content
        
        #**********************************************************
        # this part of code removes duplicate lyrics
        final_file_names = [] #initilizing file names as .txt 
        for i in get_song_name(tag):
            final_file_names.append(i.lower())#.lower() #i.lower will make the filename lowercase and remove duplicates further
        Links_df = pd.DataFrame(zip(final_file_names,links), columns=['final_file_names','links'] )
        Links_df.drop_duplicates(subset ="final_file_names",keep = False, inplace = True)
        #print(Links_df)
        #os.chdir('../')

        #**********************************************************
        
    # for loop to strip all the lyrics (only texts) and save them into a individual file.
        # get_song_name() is a custom function to extrac song names from html table cell tag.
        print(f'Extracting lyrics from {folder_name}')
        for lnk ,name in zip(Links_df['links'],Links_df['final_file_names']):#links,get_song_name(tag)

            URL_lyrics = URL+lnk
            lyrics_responce = requests.get(URL_lyrics, headers=header)
            lyric_cont = lyrics_responce.content
            lyric_soup = BeautifulSoup(lyric_cont, 'html.parser')
            lyric = lyric_soup.find_all('pre', {'id':'lyric-body-text'})

            for txt in lyric:
                full_text = txt.get_text()
                file = open(name,"w", encoding= 'utf-8')    
                file.write(full_text)    
                file.close()
            print(name)
        os.chdir('../')
        print()
        print()
        print(f'Extracted {Links_df.links.shape[0]} lyrics from {folder_name}')
        print()
        print()

except KeyboardInterrupt:

    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

except ConnectionError as e:    # This is the correct syntax
   print (e)
   r = "No response"
# In[ ]:




