"""
Load the list of movies and their ids into mongodb
"""

import pymongo

#connections
connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)

#connect to database 'raters'
database = connection.raters

#create a new collection in database 'raters' called 'movlist'
movlist = database.movlist



#function to return a dict which has movies and their ids
def loadMovieLens(path = 'data'):
    
    movies = {}
    for line in open(path+'/movies.csv'):
        (id, title) = line.split(',')[0:2]
        movies[id] = title
        
    return movies
    
#get the dict
movies = loadMovieLens()

#load the dict as a collection into the collection 'movlist'
for movie in movies:
    movlist.insert({'id':movie, 'movie':movies[movie]}, check_keys = False)