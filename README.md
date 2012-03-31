# Bugs

* Note edit does not take blank entries, but rather enters last entry if nothing at all is entered.  Seems as though form validation is failing on any of the fields for editing or creating a note.
* need to update search to search document contents, not just title

# TODO

Need to create some basic model layouts  
Will start very simple  
User model already exists  
Will need to create a model for Manually entered notes  
So far two tables, User and Notes  
However... might need to have a linking table, study the Bookmark Data Model on pg 33 as this might be needed to link the User table to the Notes table  

**01-30-2012**
need to swap in Blueprint CSS for the CSS of this webpage

**01-31-2012**
Created notes template and user page for individual notes, implemented round about way of displaying note when clicking link to note, but needs work

**02-04-2012**
Removed Bookmarks table, created Foreign key from Note table to user, Need to fix urlconf and views and templates for new setup

**02-06-2012**
created template inheritance, need to incorporate blueprint CSS for stylesheets

**02-14-2012**
Idea for displaying individual notes, need to loop through each object in the queryset returned from "notes" and add on the note's id to the url that is attached to each iteration.  then, you can create a urlconf entry that accepts this number as in user/notes/1 and it then passes this number to the corresponding view which grabs this note out of the database and displays its "note" attribute.
