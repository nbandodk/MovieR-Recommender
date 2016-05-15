"""
Main driver program.

"""

import pymongo
import sys  
from math import sqrt
reload(sys)  
sys.setdefaultencoding('utf8')

from flask import Flask, render_template, redirect, url_for, request, session, flash

connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.raters

users = database.users
movlist = database.movlist
simitems = database.simitems

# Returns the Pearson similarity score
def pearson_score(people, p1, p2):
    si = {}
    for item in people[p1]:
        if item in people[p2]:
            si[item] = 1
            
    n = len(si)
    
    if n == 0:
        return 0
        
    # Add up all the preferences
    sum1=sum([people[p1][it] for it in si])
    sum2=sum([people[p2][it] for it in si])
    
    # Sum up the squares
    sum1Sq=sum([pow(people[p1][it],2) for it in si])
    sum2Sq=sum([pow(people[p2][it],2) for it in si])
    
    # Sum up the products
    pSum=sum([people[p1][it]*people[p2][it] for it in si])
    
    # Calculate Pearson score
    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    
    if den==0: return 0
    
    r = num/den
    
    return r


def topMatches(people, target_person, n = 5):
    scores = [(pearson_score(people, target_person, person), person) for person in people if person != target_person]
    
    scores.sort()
    scores.reverse()
    return scores[0:n]
    
    

#use weighted averages to give recommendations
def recommend(people, person):
    totals = {}
    similarity_sum = {}
    for other in people:
        if other == person:
            continue
            
        sim = pearson_score(people, person, other)
        
        if sim <= 0:
            continue
            
        for item in people[other]:
            
            #only score for the movies which the person has not seen
            if item not in people[person] or people[person][item] == 0:
                
                # total of all the (review score * smiliarity) 
                totals.setdefault(item, 0)
                totals[item] += people[other][item] * sim 
                
                # sum of the similarities
                similarity_sum.setdefault(item, 0)
                similarity_sum[item] += sim

    #create normalized list of recommendation rankings
    rankings = [(total/similarity_sum[item], item) for item, total in totals.items()]
    
    rankings.sort()
    rankings.reverse()
    return rankings
    
def transformData(people):
    result = {}
    for person in people:
        for item in people[person]:
            result.setdefault(item, {})
            
            result[item][person] = people[person][item]
            
    return result

    

def getRecommendedItems(prefs,itemMatch,user):
    userRatings=prefs[user]
    scores={}
    totalSim={}

    # Loop over items rated by this user
    for (item,rating) in userRatings.items( ):
        # Loop over items similar to this one
        for (similarity,item2) in itemMatch[item]:
            # Ignore if this user has already rated this item
            if item2 in userRatings: continue

            # Weighted sum of rating times similarity
            scores.setdefault(item2,0)
            scores[item2]+=similarity*rating
            # Sum of all the similarities
            totalSim.setdefault(item2,0)
            totalSim[item2]+=similarity


    # Divide each total score by total weighting to get an average
    rankings=[(score/totalSim[item],item) for item,score in scores.items( )]

    # Return the rankings from highest to lowest
    rankings.sort( )
    rankings.reverse( )
    return rankings


def getData():
    d = {}
    for person in users.find():
        d[person['id']] = person['ratings']
    return d

def getMov():
    l = []
    for movie in movlist.find():
        l.append(movie['movie'])
        
    return l
 
def getSim():
    d = {}
    for mov in simitems.find():
        d[mov['movie']] = mov['similars']
    return d
    
    
app = Flask(__name__)

app.secret_key = 'my prec'



@app.route('/')
def loadMovieLens():
    getRecuu.start = 0    
    getRecuu.end = 10
    getRecii.start = 0
    getRecii.end = 10
    return render_template('index.html')
    
   
@app.route('/rate/<alg>', methods=['GET', 'POST'])
def rate(alg):
    global l
    
    if request.method == 'POST':
        
        select = request.form.get('option')
        rating = request.form.get('inlineRadioOptions')
        
        if(select == None or rating == None):
            the_message = "Please select the movie and provide its rating"
            flash(the_message)
            return render_template('rate.html', option_list = l, alg = alg, cat='error')
        
        ratings[select] = int(rating)
        
        if select in l : l.remove(select)
        if rate.counter > 0 :
            the_message = "<---------- Rating submitted for the movie: %s ---------->  (%d more needed)" % (select, rate.counter)
        else:
            the_message = "<---------- Rating submitted for the movie: %s ---------->" % (select)
        flash(the_message)
        rate.counter -= 1
        
        return render_template('rate.html', option_list = l, alg = alg, cat='normal')
    
    
        
    return render_template('rate.html', option_list = l, alg = alg)
    
rate.counter = 9

   
@app.route("/getrecuu", methods=['GET', 'POST'])
def getRecuu():
    global ratings
    global l
    global reclist
    if request.method == 'POST':
        
        getRecuu.start = getRecuu.end
        getRecuu.end += 10
        
        if getRecuu.end <= len(reclist):
            return render_template('fin.html', list=reclist[getRecuu.start:getRecuu.end])
        else:
            getRecuu.start = 0
            getRecuu.end = 10
            return render_template('fin.html', list=reclist[getRecuu.start:getRecuu.end])
    
    users.insert({'id':669, 'ratings': ratings}, check_keys = False)
    critics = getData()
    reclist = recommend(critics, 669)
    users.delete_one({'id':669})
    ratings = {}
    rate.counter = 9
    l = getMov()
    return render_template('fin.html', list=reclist[getRecuu.start:getRecuu.end])

getRecuu.start = 0    
getRecuu.end = 10

@app.route("/getrecii", methods=['GET', 'POST'])
def getRecii():
    global ratings
    global l
    global reclist
    if request.method == 'POST':
        
        getRecii.start = getRecii.end
        getRecii.end += 10
        
        if getRecii.end <= len(reclist):
            return render_template('fin.html', list=reclist[getRecii.start:getRecii.end])
        else:
            getRecii.start = 0
            getRecii.end = 10
            return render_template('fin.html', list=reclist[getRecii.start:getRecii.end])
            
    users.insert({'id':669, 'ratings': ratings}, check_keys = False)
    critics = getData()
    itemsim = getSim()
    reclist = getRecommendedItems(critics, itemsim, 669)
    users.delete_one({'id':669})
    ratings = {}
    rate.counter = 9
    l = getMov()
    return render_template('fin.html', list=reclist[getRecii.start:getRecii.end])    

getRecii.start = 0
getRecii.end = 10    
   
if __name__ == '__main__':
    global l
    l = getMov()
    global ratings
    ratings = {}
    app.run(debug=True)