#first attempt at a Python wrapper for the Bookshare API, found at
#http://developer.bookshare.org
#Tested on Python2.7x32 running on Window 7 x64.
#written by Alex Hall, mehgcap@gmail.com.
#You may use, modify,redistribute, and so on.
#If you use this wrapper in a project, be kind enough to credit me, but otherwise do what you want with the code.
#Send me an email with any bug reports and I will do my best to fix them.
#If you fix something, send me details and I will incorperate it into an update, crediting you for any fixes.
#I am not responsible, in any way whatsoever, for any damages that occur as a result of this program.
#Basically, use at your own risk, and don't blame me if anything whatsoever goes wrong.
#Tell me about it so I can fix it, but you may not take any legal action against me for it.
#There, that's over. Now let's get started!

import hashlib
import re
import urllib
import urllib2
import xml.etree.ElementTree as xml

#global functions:

def request(request=None, url=None, data=None, headers=None):
 #pass either a single urllib2.Request object, or a url,data,headers set to use
 if request is not None:
  return urllib2.urlopen(request)
 else:
  return urllib2.urlopen(url, data, headers)

#useful classes:

class Book(object):
 """This is a class for a given book, holding author(s), title, copyright, ISBN, and so on."""

 def __init__(self, data=None):
  self.data=data
  self.unknown="unknown"
  self.title=self.unknown
  self.authorList=[]
  self.authorStr=""
  self.categoryList=[]
  self.categoryStr=""
  self.id=self.unknown
  self.isbn=self.unknown
  self.copyright=self.unknown
  self.dateAdded=self.unknown
  self.shortSynopsis=self.unknown
  self.longSynopsis=self.unknown
  self.publisher=self.unknown
  self.quality=self.unknown
  self.pages=self.unknown
  self.brf=False
  self.daisy=False
  self.images=False
  self.language=self.unknown
  self.public=False
  self.available=False
  self.type=BookshareApi().book
  if self.data is not None: self.parse(data)

 def __str__(self):
  return self.title+" by "+self.authorStr

 def parse(self, data=None):
  #expects book info in xml format as given by the parse methods of BookshareApi or SearchResults
  #basically, just give it an element starting at the "result" level of the xml
  if data is None: data=self.data
  #xml.dump(data) #prints data to stdout for debugging
  id=data.find("content-id")
  #check that it worked since booklist results are "id" and meta results are "content-id"
  if id is None: id=data.find("id")
  if id is not None: self.id=id.text
  self.title=self.getText("title")
  self.isbn=self.getText("isbn13")
  self.copyright=self.getText("copyright")
  self.dateAdded=self.getText("publish-date")
  self.publisher=self.getText("publisher")
  self.daisy=bool(int(self.getText("daisy", failure=False)))
  self.brf=bool(int(self.getText("brf", failure=False)))
  self.images=bool(int(self.getText("images", failure=False)))
  self.language=self.getText("language")
  self.public=bool(int(self.getText("freely-available", failure=False)))
  self.available=bool(int(self.getText("available-to-download", failure=False)))
  self.shortSynopsis=self.getText("brief-synopsis")
  self.longSynopsis=self.getText("complete-synopsis")
  self.quality=self.getText("quality")
  (self.authorList, self.authorStr)=self.makeListFrom(data, "author", self.authorList, self.authorStr)
  if self.authorStr is None: self.authorStr=self.unknown
  (self.categoryList, self.categoryStr)=self.makeListFrom(data, "category", self.categoryList, self.categoryStr)
  if self.categoryStr is None: self.categoryStr=self.unknown


 def getText(self, tag, data=None, failure="unknown"):
  #set failure to "False" if you want to cast results to a bool
  if data is None: data=self.data
  txt=data.findtext(tag)
  if txt is not None: return txt
  else: return failure

 def makeListFrom(self, data, tag, l, s):
  #searches data for tag and puts the text into the list l, then makes a pretty string s from the list
  found=data.getiterator(tag)
  for f in found:
   if f is not None: l.append(f.text)
  for i in range(len(l)):
   if l[i] is None: continue
   s+=l[i]
   if i<len(l)-1 and len(l)!=2: s+=", "
   if i==len(l)-2: s+="and "
  return(l, s)



class Periodical(Book):
 """similar to a book, but holds a periodical's information, like a newspaper or magazine"""

 def __init__(self, data=None, *args, **kwords):
  super(Periodical, self).__init__(data, *args, **kwords)
  self.edition=self.unknown
  self.revision=self.unknown
  self.revisionTime=self.unknown
  self.type=BookshareApi().periodical

 def __str__(self):
  return str(self.title)

 def parse(self, data=None):
  super(Periodical, self).parse(data)
  self.edition=self.getText("edition")
  self.revision=self.getText("revision")
  self.revisionTime=self.getText("revision-time")

class SearchResults(object):
 """A class for holding the results of a Bookshare lookup/search, including results, pages, current page, limit, and so on."""

 def __init__(self,
  data=None, #xml data
  type=None,
  url=None,
  error=None,
  message=None,
  page=0,
  pages=0,
  limit=0,
  category=None,
  grade=None,
  resultCount=0,
  results=[]):
  self.data=data
  self.type=type #should be either book or periodical, gotten from BookshareApi constants
  self.url=url
  self.error=error
  self.message=message
  self.page=page
  self.pages=pages
  self.limit=limit
  self.category=category
  self.grade=grade
  self.resultCount=resultCount
  self.results=results
  if self.data is not None: self.parse(self.data, self.type)

 def __len__(self):
  return len(self.results)

 def __iter__(self):
  #makes this class indexable instead of having to use its "results" list
  return iter(self.results)

 def __getitem__(self, i):
  return self.results[i]

 def __setitem__(self, i, item):
  self.results[i]=item

 def parse(self, data, type=None):
  #expects a parsed xml tree; pass it the root of an xml.parse() and it should be happy
  if type is None: type=self.type
  self.results=[]
  info=None
  book=BookshareApi().book
  periodical=BookshareApi().periodical
  if type==book:
   info=data.find("book/list")
   results=data.findall("book/list/result")
   for r in results:
    self.results.append(Book(r))
  elif type==periodical:
   info=data.find("periodical/list")
   results=data.findall("periodical/list/result")
   for r in results:
    self.results.append(Periodical(r))
  #get basic info about the results, if possible
  message=data.findtext("messages/string")
  page=info.findtext("page")
  limit=info.findtext("limit")
  pages=info.findtext("num-pages")
  if message is not None: self.message=message
  if page is not None: self.page=int(page)
  if pages is not None: self.pages=int(pages)
  if limit is not None: self.limit=limit
  #use the "x - y of z results" string of search results to find total results
  parser=re.compile(r'\D*\d*\D*\D*\d*\D*(\d*)')
  s=parser.search(self.message)
  if s is not None: self.resultCount=s.groups()[0]

 def getPage(self, num, jump=False):
  #gets the desired page of results, if possible
  #to get page x, pass x and set jump to True; otherwise, pass 1 or -1 and make jump False
  page=0
  if jump: page=num
  else: page=self.page+num
  if page not in range(1, self.pages+1): return False
  self.url=re.sub(r'page/\d*', "page/"+str(page), self.url)
  res=xml.parse(request(self.url))
  self.parse(res.getroot())
  return True

 def nextPage(self):
  return self.getPage(1, False)

 def prevPage(self):
  return self.getPage(-1, False)

 def getCategory(self):
  #searches self.url for the current category and returns it, if found
  cat=re.compile(r'/category/(.)(/|\?)')
  s=cat.search(self.url)
  if s:
   category=s.groups()[0]
   category=re.sub("+", " ", category)
  else: category=None
  return category

 def getGrade(self):
  #searches self.url for the current grade and returns it, if found
  g=re.compile(r'/grade/(.)/|\?')
  s=g.search(self.url)
  if s is not None:
   grade=s.groups()[0]
   grade=re.sub("+", " ", category)
  else: grade=None
  return grade

 def setCategory(self, category):
  #sets a new category for the results by changing the url
  tmp=re.sub(r'category/\D*/', "category/"+category+"/", self.url)
  if tmp==self.url: #no change was made, so tack on the category
   self.url=re.sub("?", "/category/"+category+"?", self.url)
  else: self.url=tmp






 def setGrade(self, grade):
  #sets a new grade for the results by changing the url
  tmp=re.sub(r'grade/\D*/', "grade/"+grade+"/", self.url)
  if tmp==self.url: #no change was made, so tack on the grade
   self.url=re.sub("?", "/grade/"+grade+"?", self.url)
  else: self.url=tmp

 def search(self):
  #repeats the search using self.url
  res=xml.parse(request(self.url))
  self.parse(res.getroot())



class BookshareApi(object):
 """A class for the Bookshare api, including searches, downloads, and user preference lookup/modification."""

 def __init__(self,
  username=None,
  password=None,
  password_ready=None,
  key=None,
  limit=100):
  self.username=username
  self.password=password
  if self.password is not None and password_ready is None: self.password_ready=urllib.quote(hashlib.md5(self.password).hexdigest())
  else: self.password_ready=password_ready
  self.password_header={"X-password":self.password_ready}
  self.key=key
  self.key_str="?api_key="+str(self.key)
  self.base="https://api.bookshare.org/"
  self.limit=limit #how many results per page
  if self.limit<0: self.limit=1
  elif self.limit>250: self.limit=250
  self.downloadsRemaining=None
  self.categoryList=None
  self.gradeList=None
  self.memberList=None
  #type constants for book or periodical search and formats
  self.book="book"
  self.periodical="periodical"
  self.brf=0
  self.daisy=1
  self.bsRequest=None
  #dict of all Bookshare errors
  self.errorMessages={
   -1:"No results found",
   0:"Book not found",
   10:"Invalid character in search string",
   11:"Requested result page is out of bounds",
   12:"Invalid ID for this search",
   13:"Organizational ID does not exist",
   14:"No Members available for the Sponsors Organization",
   20:"Invalid date",
   30:"Periodical not found",
   31:"Periodical edition not found",
   32:"Periodical revision not found",
   40:"Content not available",
   41:"Content not available for this user",
   42:"Content not available in requested format",
   43:"Content not found for the given ID",
   44:"User Account has not signed the user agreement. Please contact customer support.",
   50:"Invalid or incomplete request",
   51:"Invalid output format",
   60:"Unauthorized access",
   61:"The user is not a valid sponsor for an organization",
   70:"Invalid preference field",
   71:"Invalid preference action",
   72:"Invalid value for preference action",
   73:"Invalid format for preference action",
   74:"Preferences type is invalid",
   75:"Attempting to set a read-only preference",
   80:"Organization has no download password set",
   81:"Download password cannot match user password",
   82:"The Member for whom a NIMAC title is being downloaded requires an IEP certificate. This can be set at the Bookshare.org site by the Sponsor.",
   401:"You do not have the necessary Privileges to perform this action.",
   403:"Invalid username or password. Please try again.",
   404:"The specified URL was not found.",
   500:"Internal server error: the Bookshare server is experiencing difficulties or you are not logged in. Please try again in a few minutes."
  }

 def setCreds(self, username, password):
  #user/password setter, for logging in after an api object is created
  self.username=username
  self.password=password
  self.password_ready=urllib.quote(hashlib.md5(self.password).hexdigest())
  self.password_header={"X-password":self.password_ready}

 #first, the master request function for asking for anything from the api:
 def request(self, args, category=None, grade=None, page=None, limit=None, member=None, search=True, data=None, headers={}):
  #expects a list of args with identification for the api, such as
  #["isbn", "0-0-0-...", "limit", 50]
  #ORDER MATTERS!!
  if len(args)>2 and type(args[2]).__name__=="list": #extract from this sublist
   print "parsing args list"
   args2=[]
   args2.append(args[0])
   args2.append(args[1])
   for a in args[2]: args2.append(a)
   args=args2
  #now add category, grade, and paging commands, if passed in
  if category is not None: args.append("category"); args.append(category)
  if grade is not None: args.append("grade"); args.append(grade)
  if page is not None: args.append("page"); args.append(page)
  if member is not None: args.append("member"); args.append(member)
  #if limit is not None: args.append("limit"); args.append(limit)
  if limit is not None and search: args.append("limit"); args.append(limit)
  if limit is None and search: args.append("limit"); args.append(self.limit)
  #convert to a slash separated string for use in the url
  params=""
  for i in range(len(args)):
   args[i]=urllib.quote_plus(str(args[i]), safe='/') #take care of spaces and special chars
   if args[i]==None: break #some funcs pass None. This line is probably unnecessary but doesn't hurt
   params+=str(args[i])
   if i<len(args)-1: params+="/" #divide each param with a slash
  url=self.base+params+self.key_str
  #print url
  req=urllib2.Request(url, data, headers)
  try: res=urllib2.urlopen(req)
  except urllib2.HTTPError, e:
   if e.code==500: raise ApiError(500, self.errorMessages[500])
  return res

 #now the search functions, each of which returns a ResultSet object which is initialized with the function's xml (gotten from request)

 def search_id(self, id, category=None, grade=None, page=1, limit=None, type=None, member=None):
  #if found, returns the book with the specified ID, not a booklist
  if type is None: type=self.book
  return self.parse(self.request([type, "id", id], category, grade, page, limit, member))

 def search_isbn(self, isbn, category=None, grade=None, page=1, limit=None, type=None, member=None):
  #again, returns only a single book, if found
  if type is None: type=self.book
  return self.parse(self.request([type, "isbn", isbn], category, grade, page, limit, member))

 def search_title(self, title, category=None, grade=None, page=1, limit=None, type=None, member=None):
  if type is None: type=self.book
  return self.parse(self.request([type, "searchFTS/title", title], category, grade, page, limit, member))

 def search_author(self, author, category=None, grade=None, page=1, limit=None, type=None, member=None):
  if type is None: type=self.book
  return self.parse(self.request([type, "searchFTS/author", author], category, grade, page, limit, member))

 def search_title_author(self, txt, category=None, grade=None, page=1, limit=None, type=None, member=None):
  if type is None: type=self.book
  return self.parse(self.request([type, "searchTA", txt], category, grade, page, limit, member))

 def search_since(self, date, category=None, grade=None, page=1, limit=None, type=None, member=None):
  #date must be in the form of eight numbers: mmddyyyy
  if type is None: type=self.book
  return self.parse(self.request([type+"/search/since", str(date)], category, grade, page, limit, member))

 def search_edition(self, id, category=None, grade=None, page=1, limit=None, type=None, member=None):
  if type is None: type=self.periodical
  return self.parse(self.request([type+"/id", str(id)], category, grade, page, limit, member))

 def search(self, txt, category=None, grade=None, page=1, limit=None, type=None, member=None):
  #full (author, title, book text) search
  if type is None: type=self.book
  return self.parse(self.request([type, "searchFTS", txt], category, grade, page, limit, member))


 def getBooksBy(self, author, page=1, limit=None, member=None, category=None, grade=None):
  #returns a list of books by the supplied author
  return self.parse(self.request(["book/search/author", author], page=page, limit=limit, member=member))

 def getPopular(self, page=1, limit=None, member=None, grade=None):
  #requests the most popular books on Bookshare
  return self.parse(self.request(["book/popular"], page=page, limit=limit, member=member))


 def getLatest(self, page=1, limit=None, member=None, grade=None):
  #requests the most popular books on Bookshare
  return self.parse(self.request(["book/latest"], page=page, limit=limit, member=member))

 def getBooksInCategory(self, category, page=1, limit=None, member=None, grade=None):
  #gets the books in the given category
  return self.parse(self.request(["book/searchFTS/category", category], page=page, limit=limit, member=member))

 def getPeriodicals(self, page=None, limit=None, member=None):
  #returns a list of all periodicals authorized for the current user; if unauthenticated, all periodicals are returned
  return self.parse(self.request(["periodical/list"], page=page, limit=limit, member=member))

 def getCategoryList(self, save=True):
  #returns a full list of categories
  original=self.request(["reference/category/list/limit/250"], search=False)
  original=self.findErrors(original)
  #original=xml.parse(original)
  root=original.getroot()
  catList=root.findall("category/list/result/name")
  categories=[]
  for c in catList: categories.append(c.text)
  if save: self.categoryList=categories
  return categories

 
 def getGradeList(self, save=True):
  #returns a full list of categories
  original=self.request(["reference/grade/list/limit/250"], search=False)
  original=self.findErrors(original)
  #original=xml.parse(original)
  root=original.getroot()
  gradeList=root.findall("grade/list/result/name")
  grades=[]
  for g in gradeList: grades.append(g.text)
  if save: self.gradeList=grades
  return grades

 def getMemberList(self, save=True):
  #for organizational accounts only. Returns a list of authorized members for the organization
  members=[]
  data=self.request(["user/members/list/for", self.username], limit=250, search=False, headers=self.password_header)
  data=self.findErrors(data)
  #data=xml.parse(data)
  root=data.getroot()
  if root.find("downloads-remaining") is not None: self.downloadsRemaining=root.findtext("downloads-remaining")
  memberList=root.findall("user/list/member")
  for m in memberList:
   last=m.findtext("last-name")
   first=m.findtext("first-name")
   id=m.findtext("member-id")
   members.append([first, last, id])
  if save:  self.memberList=members
  return members

 def getPrefsList(self, data=None):
  #if data is None, gets preferences from api, else parses them from data.
  #useful for use with the setPref function
  prefsList={}
  if data is None: prefs=self.request(["user/preferences/list/for", self.username], headers=self.password_header, search=False)
  else: prefs=data
  prefs=self.findErrors(prefs)
  #prefs=xml.parse(prefs)
  root=prefs.getroot()
  l=root.findall("user/list/result")
  for e in l:
   val=e.findtext("name").lower()
   prefsList[val]={}
   for field in e.findall("*"):
    if field.tag=="name": continue
    prefsList[val][field.tag]=field.text.lower()
  return prefsList

 def setPref(self, num, val, member=None):
  #sets the user preference specified by the "num" arg to the value of the "val" arg
  res=self.request(["user/preference", str(num), "set", str(val), "for", self.username], search=False, member=member, headers=self.password_header)
  return self.getPrefsList(res)

 def getUserInfo(self, data=None):
  #if data is None, gets info from api, else parses from data.
  infoList={}
  if data is None: info=self.request(["user/info/display/for", self.username], headers=self.password_header, search=False)
  else: info=data
  info=self.findErrors(info)
  root=info.getroot()
  l=root.findall("user/list/result")
  for e in l:
   val=e.findtext("name").lower()
   infoList[val]={}
   for field in e.findall("*"):
    if field.tag=="name": continue
    infoList[val][field.tag]=field.text.lower()
  return infoList

  

 #now a few utilities:

 def download(self, book, destination, format=0, extension=".bks2", member=None):
  id=book.id
  #replace characters in title that Windows won't accept
  title=re.sub(r'\\|:|"|\'|\||/|<|>', " ", book.title)
  forUser="for/"+self.username
  try: res=self.request(["download", forUser, "content", str(id), "version", str(format)], headers=self.password_header, search=False, member=member)
  except urllib2.HTTPError, e:
   if e.code==500: raise ApiError(500, self.errorMessages[500])
  local=open(destination+"\\"+title+extension, "wb")
  local.write(res.read())
  local.close()
  res.close()
  return True

 def findErrors(self, data):
  #examines xml for bookshare errors and raises the first one it sees, if any
  try: res=xml.parse(data)
  #ignore the next two errors, thrown if "data" is already parsed. There has to be a better way...
  except xml.ParseError: res=data
  except TypeError: res=data
  root=res.getroot()
  error=root.find("status-code")
  if error is not None: error=error.text
  message=root.find("messages/string").text
  if error is not None and message is None: #this error has no message from Bookshare
   message=self.errorMessages[error]
  try: url=data.url
  except AttributeError: url="unknown"
  if error is not None: raise ApiError(error, message, url)
  else: return res

 def getMetaData(self, book):
  #returns a book object with all possible info about the given book, useful for specifics on a book in a search results list
  if book.type==self.book:
   res=self.request([book.type, "id", str(book.id)], search=False)
  elif book.type==self.periodical:
   res=self.request([book.type, "id", str(book.id), "edition", str(book.edition), "revision", str(book.revision)], search=False)
  root=xml.parse(res).getroot()
  data=root.find(book.type+"/metadata")
  if book.type==self.book: return Book(data)
  else: return Periodical(data)

 def parse(self, data=None):
  #parses the xml in "data" and fills the rest of the fields with the results
  res=xml.parse(data)
  root=res.getroot()
  error=root.find("status-code")
  if error is not None: error=error.text
  message=root.find("messages/string").text
  if error is not None and message is None: #this error has no message from Bookshare
   message=self.errorMessages[error]
  if error is not None: raise ApiError(error, message, data.url)
  #now determine what to return: SearchResults, Book, or Periodical
  book=root.find("book/metadata")
  if book is not None: return Book(book)
  per=root.find("periodical/metadata")
  if per is not None: return Periodical(per)
  perSearch=root.find("periodical/list")
  if perSearch is not None and int(perSearch.findtext("num-pages"))==0: raise ApiError(-1, message, data.url)
  bookSearch=root.find("book/list")
  if bookSearch is not None and int(bookSearch.findtext("num-pages"))==0: raise ApiError(-1, message, data.url)
  if bookSearch is not None: return SearchResults(root, self.book, data.url)
  if perSearch is not None: return SearchResults(root, self.periodical, data.url)

class ApiError(Exception):
 #for use with any bad requests from Bookshare's api

 def __init__(self, number, message, url=""):
  self.number=number
  self.message=message
  self.url=url

 def __str__(self):
  return "%d: %s\nURL: %s" %(self.number, self.message, self.url)
