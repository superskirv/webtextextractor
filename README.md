# webtextextractor
Copy Stories from Literotica.com into easy to use/save .txt files. Can copy multiple works and save into a single text file. Right now the default operation only saves the first story. Click the checkbox to have it look for and download all the stories in the series.

Why: Basically I was using the Literotica App on my phone but I found out if you are offline you can only look at stories that are saved to your cache/temp files. And being stuck in a location with no internet service for several months means I don't get to read any stories I favorited. So I started manually coping the text out of the website into a text file, but that process is slow and annoying, though I did it several hundred times before I decided to figure out how too automate it. I made sure to keep the original link and author name in the files because it is important to me. If I ever want to look up a story to see if they made the next part, or want to check out other great stories by the same author I can. I have also found that sometimes users will delete their accounts and all their stories for some reason. So I was happy to know that I continue to have a offline copy with the author's name in it. Some users have published their works in to books, which is fantastic.

Update v2:
I have re-written nearly every line of code from the ground up. The new interface still needs some loving, but it is much better than before. I removed the config file options and link discovery for now. I plan to re-add these in the future. There is also a "options" field for individual jobs. As of right now the only user change is weather or not to download the whole series, which I cant figure out why you wouldn't.

The Vision:
I plan to change how the parsing of text is search/found/extracted works. I have learned a new ways to do it. I just didn't want to delay completing my re-write with learning and implementing a new method right in the middle of it. I will make the changes, especially as the website updates and breaks the way I'm currently looking for text bits.

Some Known Issues:

1. Allow users to config more options.
   - (One option that isnt currently configurable is the file extension.)
2. No way to delete jobs, even if they are completed.
3. Status messages could be more clear.
4. No scroll bar on the message log for jobs.
   - (You can use your mouse wheel.)
5. Message logs do not auto update
   - (You have to select/click the job again to force it to update.)
6. The author is a script kiddie.
   - (No fix possible at this time.)
7. The interface looks lame.
   - (Less lame than before, but still working on it)
8. Obvious network abuses possible.
   - (Plan to make it work from cache, adding delays on downloading html)
9. Make code look and act clean
   - (Its dirty. Refer to issue 6)
