"""
This program generates a similar item dictionary to load into mongodb which is later used for item-item collaborative filtering algo.
"""




import sys
import pymongo

reload(sys)  
sys.setdefaultencoding('utf8')
connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.raters

users = database.users
simitems = database.simitems

from math import sqrt


# Euclidean similarity score for person1 and person2
def sim_distance(prefs,person1,person2):

    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item]=1

# if they have no ratings in common, return 0
    if len(si)==0: return 0
# Add up the squares of all the differences
    sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
                        for item in prefs[person1] if item in prefs[person2]])
    return 1/(1+sum_of_squares)



# Returns the Pearson similarity score
def sim_pearson(preference,preference1,preference2):

    s={}
    for item in preference[preference1]:
        if item in preference[preference2]: s[item]=1

    l=len(s)

    if l==0: return 0
    # Add up all the preferences
    sum1=sum([preference[preference1][it] for it in s])
    sum2=sum([preference[preference2][it] for it in s])
    # Sum up the squares
    sum1Sq=sum([pow(preference[preference1][it],2) for it in s])
    sum2Sq=sum([pow(preference[preference2][it],2) for it in s])
    # Sum up the products
    pSum=sum([preference[preference1][it]*preference[preference2][it] for it in s])
    # Calculate Pearson score
    num=pSum-(sum1*sum2/l)
    den=sqrt((sum1Sq-pow(sum1,2)/l)*(sum2Sq-pow(sum2,2)/l))
    if den==0: return 0
    r=num/den
    return r

#this function gives the matching entities to a given entity    
def topMatches(prefs,person,n=5,similarity=sim_pearson):
    scores=[(similarity(prefs,person,other),other)
        for other in prefs if other!=person]
    scores.sort( )
    scores.reverse( )
    return scores[0:n]

#this function flips the dict so that now the new dict will have the keys as the values of previous dict    
def transformPrefs(prefs):
    result={}
    for person in prefs:
     for item in prefs[person]:
       result.setdefault(item,{})

       # Flip item and person
       result[item][person]=prefs[person][item]
    return result


#this function generates a dict with a list of similar entities for a particular entity , which is then loaded into mongodb
def calculateSimilarItems(prefs,n=10):
    # Create a dictionary of items showing which other items they
    # are most similar to.
    result={}

    # Invert the preference matrix to be item-centric
    itemPrefs=transformPrefs(prefs)
    c=0
    for item in itemPrefs:
        # Status updates for large datasets
        c+=1
        if c%100==0: print "%d / %d" % (c,len(itemPrefs))
        # Find the most similar items to this one
        scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
        result[item]=scores
    return result

#get the rating dataset as a dict from mongodb and return as a dict
def getData():
    d = {}
    for person in users.find():
        d[person['id']] = person['ratings']
    return d


print "Starting process..."
prefs = getData()
print "Generating the similar item dataset..."
itemsim3 =  calculateSimilarItems(prefs, n=50)


print "Loading in the database..."
for mov in itemsim3:
    simitems.insert({'movie': mov, 'similars':itemsim3[mov]}, check_keys = False)
    
print "Done..."
