from InstagramAPI import InstagramAPI
import urllib.request
import json
import glob
import time
import os
import nltk.tokenize
import datetime
from datetime import timezone
from random import randint
import csv

locations_toronto = ['Toronto, ON', 'Toronto, Ontario', 'Toronto', 'Union Square']
location_coordinates_toronto = [['43.6', '43.8'], ['-79.2', '-79.6']]#lat, lng

def top_post(username, locations, location_coordinates, number_of_days=7, without_location=False):
    time.sleep(60)
    recent_posts = []
    api.searchUsername(username)
    username_id = api.LastJson['user']['pk']
    api.getUserFeed(username_id)
    info = api.LastJson

    #Checking the location and choosing only fresh(1 week) posts
    """ Today is skiped, and looking for the previous day"""
    today_midnight = datetime.datetime(*datetime.datetime.now().timetuple()[:3])
    week_ago_date = today_midnight - datetime.timedelta(days=number_of_days)
    week_ago_timestamp = week_ago_date.replace(tzinfo=timezone.utc).timestamp()
    today_midnight = today_midnight.replace(tzinfo=timezone.utc).timestamp()

    for i in range(len(info["items"])):
        if "location" in info["items"][i]:
            location_name_check = any(x in info["items"][i]["location"]["city"] for x in locations) or any(x in info["items"][i]["location"]["name"] for x in locations) or any(x in info["items"][i]["location"]["short_name"] for x in locations)
            location_coordinates_check = (float(info["items"][i]["location"]["lat"]) >= float(location_coordinates[0][0])) and (float(info["items"][i]["location"]["lat"]) <= float(location_coordinates[0][1])) and (float(info["items"][i]["location"]["lng"]) <= float(location_coordinates[1][0])) and (float(info["items"][i]["location"]["lng"]) >= float(location_coordinates[1][1]))
            #print('"location" in info["items"][{}]  ----------- '.format(i) + str(location_name_check))
            #print("location_name_check: " + str(location_name_check))
            #print("location_coordinates_check: " + str(location_coordinates_check))
            #print("longitude: " + str(info["items"][i]["location"]['lng']))
            #print("latitude: " + str(info["items"][i]["location"]['lat']))


        if without_location==True:
            location_name_check=True
            location_coordinates_check=True

        created_at_timestamp = info["items"][i]["taken_at"]
        if location_name_check or location_coordinates_check:
            if float(info["items"][i]["taken_at"]) >= float(week_ago_timestamp) and float(info["items"][i]["taken_at"]) <= float(today_midnight):
                recent_posts.append(info["items"][i])

    print("Number of suitable posts: " + str(len(recent_posts)))
    #Choosing the top post
    if len(recent_posts) != 0:
        top_recent_post = recent_posts[0]
        for i in range(len(recent_posts)):
            if recent_posts[i]['like_count'] > top_recent_post['like_count']:
                top_recent_post = recent_posts[i]
        return top_recent_post
    else:
        print("No posts found")
        return None


def tokenizing_this_shitcaption(caption):
    punctuations = '''!()-[]{};:'"\,<>./?#$%^&*_~'''
    almost_final_answer = ""
    for char in caption:
        if char not in punctuations:
            almost_final_answer = almost_final_answer + char

    tokenizer = nltk.tokenize.TweetTokenizer()
    final_answer = tokenizer.tokenize(almost_final_answer)
    return final_answer


def find_tyler_the_creator(top_post):
    tyler_caption=None
    tyler_tagged=None
    triggered_caption = False
    #if credit in caption:
    if 'caption' in top_post:
        tokenized_caption = tokenizing_this_shitcaption(top_post['caption']['text'].lower())
        list_of_triggers = ["Credits", "credit", '📷','CREDIT','shot by',  '📸']

        print(tokenized_caption)
        for i in range(len(tokenized_caption)):
            if tokenized_caption[i] in list_of_triggers:
                triggered_caption = True
                tokenized_caption = tokenized_caption[i+1:]
                break

        if triggered_caption == True:
            for token in tokenized_caption:
                if token[0] =="@":
                    tyler_caption = token
                    break

    #if credit in usertag:
    if 'usertags' in top_post:
        if top_post['usertags'] != None and top_post['usertags'] != {}:
            tyler_tagged = top_post['usertags']['in'][0]['user']['username']


    if tyler_caption==None and tyler_tagged==None:
        return None
    if tyler_caption!=None:
        return str(tyler_caption)
    if tyler_tagged!=None:
        return str(tyler_tagged)



api = InstagramAPI("olivia.richardson1", "richardson")
api.login()


list_of_channels = ["torontontario", "torontosworld", "torontogrvm", "torontoison", "torontopixel"]

if not os.path.exists("content"):
    os.makedirs("content")


for channel in list_of_channels:
    print("looking for top post in ")
    print(str(channel))
    post = top_post(username=channel, locations=locations_toronto, location_coordinates=location_coordinates_toronto)
    if post != None:
        if 'image_versions2' in post:
            url = post['image_versions2']['candidates'][0]['url']
        elif 'carousel_media' in post:
            url = post['carousel_media'][0]['image_versions2']['candidates'][0]['url']
        tyler = find_tyler_the_creator(post)
        if tyler != None:
            print("-------------NEW CONTENT------------")
            file_name = "content/" + tyler[1:] + "-from-" + channel +"_"+str(randint(0, 100000)) + "_"+ ".jpg"
            urllib.request.urlretrieve(url, file_name)
            print("creator: " + str(tyler))
            print("file_path = " + str(file_name))
