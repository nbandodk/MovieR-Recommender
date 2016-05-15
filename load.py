"""
Load the ratings dataset into mongodb
"""

import pymongo

#connections to mongodb
connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)

#create the database called raters
database = connection.raters

#create a collection called users which will hold the ratings given by movielens users
users = database.users

#function which returns a dict containing the ratings given by movielens users for all the movies they have rated
def loadMovieLens(path = 'data'):
    
    movies = {}
    for line in open(path+'/movies.csv'):
        (id, title) = line.split(',')[0:2]
        movies[id] = title
        
    people = {}
    for line in open(path+'/ratings.csv'):
        (user, movie_id, rating, ts) = line.split(',')
        people.setdefault(user, {})
        people[user][movies[movie_id]] = float(rating)
        
    return people

#get the dict    
people = loadMovieLens()


#insert the dict as a collection into the collection 'users'
for person in people:
    users.insert({'id':int(person), 'ratings':people[person]}, check_keys = False)
    #users.insert({person:people[person]}, check_keys = False)