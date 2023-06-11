# webtextextractor
Copy Stories from Literotica.com into easy to use/save .txt files. Can copy multiple works and save into a single text file. Right now this is the default operation. All links on the left will be saved as a single file. I plan to fix that so it will only save files that are the same series as a single file. Allowing users to easily select a bunch of url's to download quickly.

Why: Basically I was using the Literotica App on my phone but I found out if you are offline you can only look at stories that are saved to your cache/temp files. And being stuck in a location with no internet service for several months means I dont get to read any stories I favorited. So I started manually coping the text out of the website into a text file, but that proccess is slow and annoying, though i did it several hundred times before I decided to figure out how too automate it. I made sure to keep the origonal link and author name in the file. Its important to me so if I ever want to look up a story to see if they made the next part, or want to check out other great stories by the same author.

Update:
Im working on re-writing the whole GUI. Its looks pretty lame. But since I have a functioning version I am gonna be really lazy about it. If anyone wants to enhance the GUI, Im all for it.

The Vision:
I dont know what I want this to be. I didnt think it would be so easy to parse and find links. Though parts of that do need a little bit of love, it messes up some links, but overall it works. I think my ideal version will have this become a replacement, at least for me, to the Literotica App. I want to design it to be able to browse the Literotica website smoothly. And be able to save any story/series to txt format, maybe other formats later. TXT format is important to me because I want it to work in ANY READER. The biggest problem Im having is figuring out what I want the GUI to look like.

Im already re-written some of the GUI to have some better layout, but I havent pushed it because I'm thinking I want to re-design again to work on mobile devices. Python is new to me, not that Im an expert in any language, but maybe I will even change languages.

Issues:
-It finds some links and adds them to list incorrectly
(I messed up a few lines of code.)
-It has trouble finding parts of stories if you start on the last part of the story
(This will be address/fixed when I work on possible network abuses.)
-The interface looks lame.
(Working on it)
-The author is a script kiddie.
(No fix possible.)
-Obvious netork abuse possible.
(Plan to make it work from cache if its less than 24 hours old.)
-Make code look and act clean
(Its very dirty. Refer to issue 4)
