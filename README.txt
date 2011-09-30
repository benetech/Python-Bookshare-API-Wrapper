To get started, create an instance of the BookshareApi class:

import pybookshare
bs=BookshareApi(username, password, api_key, limit)

*username: the user's username, usually their email address.
*password: the user's password, as plaintext (encryption to md5 is handled in the class).
*password_ready: the encrypted form of the password, useful if you store the password in a configuration file and do not want to store it as plaintext
*key: the api key of your application as issued by Bookshare.
*limit: how many books per page of search results you want. This cannot exceed 250; any value below 0 is set to 1, and above 250 is set to 250. Default is 100.

Now that we have a BookshareApi object, we can start searching and downloading. There are several types of searches you can perform, such as title, author, and so on. They all have a common format, so I will discuss that first.
*text: what you want to search for, as a string. Spaces will be replaced with plus signs (the string is run through urllib's quote function), so you do not have to do anything special to the strings to make them url-ready. This can also be a date, depending on the search type. Dates should be given as a series of eight numbers, MMDDYYYY.
*category: I recommend you use the getCategoryList() function to get valid values for this argument; any invalid value will result in a bad request.
*grade: same as category. Use getGradeList() for valid values.
*page: the page of results you want to retrieve. If you can stand to use a second api call, it is just as easy to call your search with no page argument, then call getPage(x) on the results.
*limit: if you want a limit (results per page) different from what you set when creating the BookshareApi object, specify it here.
*type: this should be set to either BookshareApi.book or BookshareApi.periodical (string constants). Specifying it will limit results to either book or periodical. If left unspecified, it is assumed that you are doing a book search.
*member: the id of the member for whom the search or download is being performed. This is unnecessary when searching, but it is there just the same if you ever need it. The id is what is returned from the getMemberList() method, in the third slot of each row in the list.

All searches wil return an object. The type of object will depend on the type of search. Generally, though, a specific search (search_id or search_isbn) will return a Book object, while any other will return a SearchResults object. Here are all the possible search types. Note that when I say "book", I am talking about either a book or a periodical, depending on whether you specify a type or not.
*search_id: look for a book with the specific id. Returns a Book object if a matching id is found.
*search_isbn: look up a book with the specified isbn. The isbn may or may not include dashes and may be 10 or 13 digits long. Returns a Book object if a book is found whose isbn matches this function's argument.
*search_title: returns a SearchResults object with title matches for the search text.
*search_author: returns a SearchResults object with books whose author matches the search text. Note that this is not the same as getting books by a specific author; use getBooksBy() for that.
*search_title_author: returns a SearchResults object with books whose titles or authors match the search text.
*search_since: expects a date as eight digits: mmddyyyy. This function returns a SearchResults object with any books added to Bookshare on or after the specified date. Note that this is not the same as the books being published on or since that date (no function exists for that).
*search: this performs a full search (matching the search text to title, author, and book content) and returns a SearchResults object of the results.
*search_edition: this is a periodical search and takes the ID of a periodical as its argument.
*getBooksBy: this gets all books by the author passed to it.
*getPopular: this takes no arguments, and returns the most popular books on Bookshare. The popularity is determined by Bookshare itself. This is not technically a search, but it returns a SearchResults object just the same.
*getLatest: this returns a list of the books most recently added to the Bookshare collection. Similar to getPopular, this returns a SearchResults object but is not actually a search function.

Any bad requests, or requests which return no results, will cause the wrapper to throw an ApiError. This error has threeattributes: number, message, and url. Generally, it is best to show your users the nessage attribute as it is almost always a message defined in Bookshare's api documentation and contains an explanation of what went wrong. Of course, you can use the number to see what happened and output your own message. Note that the message attribute is simply either gotten from the xml returned by the request or is pulled from bs.errorMessages, but either location will generally have identical messages. The official Bookshare errors start at 0. However, I have defined an additional error, -1, to be used if no results were retrieved. I felt that this was easier than having anyone who uses this wrapper have to place code to catch a SearchResults object of length 0; this way, you can just use the same try/catch I expect you will use anyway and you can still just output the error's message.

Categories and Grades
Use bs.getCategoryList() to obtain a list of valid categories from Bookshare. Once called, the BookshareApi object will have a "categoryList" attribute that you can use instead of calling the function again (and using another api call). If, for some reason, you do not want the local list updated by the function call, pass getCategoryList() an argument of False. This function will return its results.

The getGradeList() method works in exactly the same way, except that it returns a list of valid grade identifiers for use in searching.

SearchResults Object
This holds all results in a "results" list. Each book will be either a Book or Periodical object, depending on the type of search. To print all books, for example, you might do something like this:
res=bs.search_author("j k rowling")
for result in res: print result

The SearchResults object also holds any messages from Bookshare. If no error was encountered, the message will be "results m - n of o". For example, you might get a res.message that says "Results 1 - 50 of 729". Knowing this, you might do something like:

try:
 res=bs.search_title("calculus")
except pybookshare.ApiError e:
 print e.message
else:
 print res.message
 for book in res: print book

The SearchResults object will also provide information and methods for paging and other information. Using our res object, we can find out:
*what page of results we are on: res.page
*how many pages are in the set of results: res.pages
*move to the next page: res.nextPage(). Note that this will overwrite current values, so if you are storing all the books in a result, make a deep copy of the res.results list before calling this. This method takes one api call to perform, and returns False if the page is out of range.
*move to the previous page: res.prevPage(). This works the same as nextPage() but in the other direction.
*move to a specific page: res.getPage(x). Again, this works like nextPage or prevPage, so deep copy the results if you want them, and remember that this uses one api call.
*type: this will always be equal to bs.book or bs.periodical, so you may check for equality with these constants if you need to.
*resultCount: this is how many results are in the entire search, not just on the current page. Since this information is provided only in res.message and not explicitly by the api, it is possible for this functionality to break if the message format were ever changed by Bookshare (I extract it using a regular expression).
*limit: how many books per page are retrieved. This cannot be changed and is there for information only.
*url: the url used to do the search again. This is used when calling paging functions and is not meant to be changed manually. If you have to change it, please reassign the object to the result of a new search.
*len: calling len(res) will return len(res.results).
*results: a list holding the actual results of the search. However, the SearchResults class is iterable, so you can simply iterate and index it instead of having to specify the results list.

The Book Object
This is an object representing a book. It may have a little information or it may have a lot; if it is from a SearchResults object, it will have little, because the xml returned in such cases does not provide much beyond title, author, images, public, and available. If, however, the object is from a single book search (or if you run a book through BookshareApi.getMetaData(), which takes an api call), you get copyright, date added, pages, short synopsis, language, download formats, and so on. Any fields not filled in will have a value of None or SearchResults.unknown, so use something like:
for book in res:
 if book.dateAdded is None or book.dateAdded==book.unknown: continue
 print book.dateAdded
However, if you are iterating through a SearchResults object, it is a safe bet that what is None for one book will be None for them all. I have seen some different results, though, and have not yet found a pattern to them, so I let each Book object fill in everything it can.
Currently, the __str__ function for a book will return "title by author" since that is about all the useful information you are guaranteed to get. Note that "author", in this case, will be a list of all authors attached to the book, not just the first author.

The Periodical Object
This is almost identical to the Book object (in fact, it inherits Book). The main difference is that it offers edition, revision, and date in addition to all the other fields. However, it is unlikely that a periodical will ever hold most of the fields of a book (language, synopses, pages, and so on).

Downloading
To download an item, just pass it to bs.download(). This function will look at the object and download it to a file called item_title.ext. Item_title is just the title of the item being downloaded, with any unsafe characters (colons, slashes, and so on) stripped out. Parameters:
*book: the book (or periodical) object to be downloaded. Please note that you are to pass the object, not just the title or id here.
*destination: a valid path (not including a filename), such as r"c:\books". This does NOT expect trailing backslashes, so bad things would happen if you passed it r"c:\books\".
*format: 0=brf, 1=daisy. You can also just use BookshareApi.brf or BookshareApi.daisy as these are constants which are set to the appropriate numbers.
*extension: this is either .zip or .bks2 (note the use of the period - this is not added).
*member: the id (as gotten by getMemberList()) of the member for whom the download is being performed. This only applies to organizational members.

Organizational Memberships
If you run into a situation where the account is organizational instead of individual, use the getMemberList() method of the BookshareApi object to get a two-dimensional array of the members validated for the organization. This members list has one row per member, and each row has the format:
[firstName, lastName, id]
To get the first member's id, for example, you would simply do something like this:
id=bs.getMemberList()[0][2]

By default, this function sets the "memberList" attribute of the BookshareApi object to the results of the lookup as well as returning the results. This lets you do the following:
bs.getMemberList()
#we now have a "memberList" list as part of the bs object:
for member in bs.memberList: #...

If you would rather the list not be saved to the BookshareApi object, simply pass "False" to the getMemberList() function. Note that this will not clear the list of a previous call where False was not passed in, it will just not overwrite the list.

Preferences
To get a dictionary of preferences, use the getPrefsList() method. What is returned is a dictionary of dictionaries. For example:
{'adult content filtering':
 {'editable': '1',
 'id': '01',
 'value': 'false'},
'user type':
 {'editable': '0',
 'id': '02',
 'value': '1'}
}
Note that the function is set up to lowercase everything, so do not try to use an index with capital letters. I felt this was easier, in case Bookshare ever changed the capitalization scheme; your program will not break because of one changed letter case.
The preferences returned will depend on the user; see the api documentation for details.

To set a preference, use the setPref() method. This method takes the id of the preference to be set, as well as the new value. Since setting a preference causes Bookshare to return the updated preferences list, the setPref() method actually returns a list of preferences like getPrefsList() would, except that it does not require an api call (at least I do not believe it does) and it contains the updates you just made.

User Information
Similar to getPrefs(), you may use getUserInfo() to get a list of information about the user. This contains the user's "real" name, such as John Doe, and their ID. A dictionary of dictionaries is returned, just as with preferences. The main difference here is that these items are not editable, so there is no setter method for them. They are useful, though, since you can welcome your user by doing something like:
info=bs.getUserInfo()
print "Welcome, "+info['displayname']['value']

Example
Below is a simple, and somewhat incomplete, example of how to use the wrapper. It is command line, and not too fancy, but it demonstrates the essentials.

import pybookshare
import sys

key="" #your API key
username=raw_input("Please enter your Bookshare username:")
pw=raw_input("Enter your password:")
bs=pybookshare.BookshareApi(username, pw, key, 5) #searches have a limit of 5

#search options:
searchMenu=[
 "Title Search",
 "Author Search",
 "Title and Auther Search",
 "Full Search",
 "Get Books by Author",
 "get periodical list"]

txt=raw_input("Enter search terms:")
#now we have the search text, so see what kind of search to do
print "Please enter the number of your choice, or any other character to exit:"
for i in range(len(searchMenu)): print "%d: %s" %(i+1, searchMenu[i])
try:
 option=int(raw_input("Option?"))
except ValueError: #entered a non-digit, so exit
 sys.exit()

res=None #will be our results
try:
 if option==1:
  res=bs.search_title(txt)
 elif option==2:
  res=bs.search_author(txt)
 elif option==3:
  res=bs.search_title_author(txt)
 elif option==4:
  res=bs.search(txt)
 elif option==5:
  res=bs.getBooksBy(txt)
 elif option==6:
  res=bs.getPeriodicals()
 else: #digit out of range, so exit
  sys.exit()
except pybookshare.ApiError, e:
 print e #maybe print just e.message instead; printing "e" prints the url and code as well
 sys.exit()

#must have worked, so print results
print res.message
for i in range(len(res)): print "%d: %s" %(i+1, res[i])

try:
 book=int(raw_input("Enter the number of the book to work with, or any other character to exit:"))-1
except ValueError: sys.exit()
if book not in range(len(res)): sys.exit()
option=raw_input("Press i for information about the book, d to download, or any other character to exit:")
if option=="i":
 res[book]=bs.getMetaData(res[book])
 b=res[book]
 print str(b)+", copyright "+b.copyright+".\nSynopsis:\n"+b.shortSynopsis
elif option=="d":
 print "downloading..."
 bs.download(res[book], destination=r"c:\", format=bs.brf, extension=".zip")
else:
 sys.exit()