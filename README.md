# Online-library
Lab for Uni - Site for maintaining DB of books in libraries

Site for maintaining book list in libraries and usage by customers and librarians
Interface language - English/Ukrainian (can be changed)
Written in PyCharm
Contains Docker file

Interface (buttons):

Registration/Login - registration and login forms, for registration email verification is required 

Site contains admin and user parts:
Admin:
My profile - navigates to Django admin site, gives acces to full DB
Likes - list of liked books
Diagrams - diagrams of data about books, authors, genres
Export - export of books data into Excel and Word documents
Import - import of data from Excel file (with validation)

User:
My profile - navigates to user profile page with Status and list of Collections
Liked - list of liked books
Update profile - avigates to updating page, where user can update Status or Collections (Delete, Rename or furthermore delete books from collections)

Same for both:
Logout - logout from profile, all data will be saved and stored
Search - search of books by name, author or genre
Catalog - contains navigation to pages with all books and authors data, books can be liked or added to collections, also comments can be written
