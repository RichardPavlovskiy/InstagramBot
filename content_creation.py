from PIL import Image, ImageDraw, ImageFont, ImageStat
from random import randint
from InstagramAPI import InstagramAPI
import urllib.request
import json
import glob
import time
import os, os.path
import nltk.tokenize
import datetime
from datetime import timezone
import random
import csv


def make_hashtags(hashtags):
    line = ""
    for i in hashtags:
        line += i
    return "some trash hashtags to boost my account\n"+"   ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"+line


def get_mean_color(image):
    area = image.crop((0, 0, 50, 50))
    mean = ImageStat.Stat(area).mean
    return mean


def get_complimentary_color(color, my_colors):
    dif1 = (color[0] - my_colors[0][0])**2 +  (color[1] - my_colors[0][1])**2 + (color[2] - my_colors[0][2])**2
    dif2 = (color[0] - my_colors[1][0])**2 +  (color[1] - my_colors[1][1])**2 + (color[2] - my_colors[1][2])**2
    dif3 = (color[0] - my_colors[2][0])**2 +  (color[1] - my_colors[2][1])**2 + (color[2] - my_colors[2][2])**2

    Max = dif1
    if dif2 > Max:
        Max = dif2
    if dif3 > Max:
        Max = dif3
        if dif2 > dif3:
            Max = dif2

    if Max == dif1:
        print("Max distance is: dif1")
        return my_colors[0], my_colors[2]
    elif Max == dif2:
        print("Max distance is: dif2")
        return my_colors[1], my_colors[0]
    elif Max == dif3:
        print("Max distance is: dif3")
        return my_colors[2], my_colors[0]


def preprocess_photo(name, post_number):
    (x, y) = (29, 10)
    if len(str(post_number)) == 1:
        message = '00'+str(post_number)
    elif len(str(post_number)) == 2:
        message = '0'+ str(post_number)
    else:
        message = str(post_number)
    color1 = 'rgb(132, 195, 167)' # black color
    color2 = 'rgb(195, 172, 132)'
    color2 = 'rgb(195, 132, 177)'
    my_colors = [(132, 195, 167),(195, 172, 132),(195, 132, 177)]


    image = Image.open(name)

    mean_color = get_mean_color(image)
    color_to_use = get_complimentary_color(mean_color, my_colors)
    icon = Image.new('RGB', (220, 120), color = color_to_use[0])


    draw = ImageDraw.Draw(icon)
    font = ImageFont.truetype('ChangaOne-Regular.ttf', size=90)
    draw.text((x+5, y+5), message, fill=(0,0,0), font=font)
    draw.text((x-2, y), message, fill=(132, 195, 167), font=font)

    x, y = icon.size
    image.paste(icon, (0,0,x,y))


    image.save(name[:-4]+"_preprocessed.jpg")
    os.remove(name)


def make_caption_and_comment(tyler):
    #making a list out of captions.csv file
    with open('captions.csv', 'r') as f:
        reader = csv.reader(f)
        captions_list = []
        for i in reader:
            captions_list.append(list(i)[0])

    post_counter = int(float(captions_list[0]))
    print("post_counter: " + str(post_counter+1))

    caption  = captions_list[(post_counter%30)+1]
    post_counter += 1
    captions_list[0] = str(post_counter)

    #saving a new captions.csv with updated post_counter
    with open("captions.csv", "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        for val in captions_list:
            writer.writerow([val])

    greeting = [
    "fabulous photo by {}",
    "featuring masterpiece of {}",
    "incredible photo of {}",
    "photo done by extreamly talanted {}",
    "breathtaking shot done by {}",
    "incredible shot of {}",
    "shot done by super talanted {}",
    "photo done by super talanted {}",
    "featuring perfect shot of {}",
    "incredible shot by {}",
    "photo by genious {}",
    ]
    processed_caption = caption + "   ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n" + "follow for more: @totorontos" + "   ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n" + greeting[randint(0, 11)-1].format("@"+tyler)
    comment = make_hashtags(hashtags)
    return processed_caption, comment

def make_a_post():
    root = os.getcwd()
    path = os.path.join(root, "content")
    list_of_filenames= []
    for dirName, subdirList, fileList in os.walk(path):
        for name in fileList:
            list_of_filenames.append(name)

    name = random.choice(list_of_filenames)
    tyler = ""
    for i in name:
        if i != "-":
            tyler +=i
        else:
            break

    with open('captions.csv', 'r') as f:
        reader = csv.reader(f)
        captions_list = []
        for i in reader:
            captions_list.append(list(i)[0])
    #to make a number label of a new post we add +1 to counter, before making the new post(we have+1 for counter there)
    post_counter = int(float(captions_list[0]))+1

    caption, first_comment = make_caption_and_comment(tyler)



    photo = os.path.join(path, name)
    preprocess_photo(photo, post_counter)
    photo_path = photo[:-4]+"_preprocessed.jpg"


    #post a photo
    api.uploadPhoto(photo_path, caption=caption)
    time.sleep(3)
    os.remove(photo_path)

    #make a comment
    api.searchUsername("totorontos")
    username_id = api.LastJson['user']['pk']
    api.getUserFeed(username_id)
    user_feed = api.LastJson # returns the first posts of your user
    mediaID = user_feed['items'][0]['pk'] # gives the mediaID of your recent uploaded photo
    api.comment(mediaID, first_comment)

    print("caption: " + caption)
    print("comment: " + first_comment)
    print("tyler: " + str(tyler))

hashtags = ["#totorontos", "#toronto",  "#ontario", "#torontoontario", "#canada", "#city", "#canadian", "#raptors","#torontoinsta","#thankyoutoronto","#inthesix","#6ixwalks","#torontomind","#blogto", "#urban_shots","#livelovecanada","#citygrammers","#trueto","#inside_to","#wethenorth","#streetsoftoronto","#torontospirit","#six"]

api = InstagramAPI("totorontos", "Centauri2014")
api.login()


make_a_post()
