from InstagramAPI import InstagramAPI
import random
import time
import csv





# 1. each day no more the 400/500 of follows/unfollows
# 2. constant amount of followers all the time with delta(30)
# 3. give 2-3 days before moving to unfollow list
# 4. Run from 9:00 am to 9:00 pm randomly
# 5.   delta in procent from -15% to 15%
#      follow_today < delta + unfollow_today
#      follow_today + unfollow_today = randint(400,500)
#
"""
########## ALGO #############
#None - haven't been followed before, should be added to follow list
#0 - followed today, after has been added to follow_today
#1 - followed for one day,
change to either Yes(followed me back)/No(haven't followed me back)
"""

follow_today = []
following_limit = 1000



api = InstagramAPI("totorontos", "Centauri2014")
api.login()

myfollowers = []
for user in api.getTotalSelfFollowers():
    myfollowers.append(str(user['pk']))#ids of myfollowers only
"""
#PART 0: Cleaning from bots !!! TURN OFF AFTER FIRST USE !!!

database  = []
with open('toronto_notprocessed.csv', 'r') as f:
    reader = csv.reader(f)
    for i in reader:
        user = list(i)
        #if [int(user[-1]), int(user[-2]), int(user[-3])] == [0,0,0]:739
        if int(user[-1]) < following_limit and [int(user[-1]), int(user[-2]), int(user[-3])] != [0,0,0]:
            database.append(["None"]+user)

with open("toronto_processed.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(database)
"""


#PART 1: Get follow/unfollow lists
#None - haven't been followed before
#0 - followed for today
#1 - followed for one day
#2 - followed for two days - time to unfollow
#Yes/No - Yes(followed me back)/No(haven't followed me back)
follow = []
unfollow = []
database = []
options = []
with open("toronto_processed_new.csv", 'r') as f:
    reader = csv.reader(f)
    for i in reader:
        user = list(i)
        database.append(user)
        if user[0] not in options:
            options.append(user[0])
        if user[0] == "None" and user[1] not in myfollowers:
            follow.append(user)
        elif user[0] == "1":
            unfollow.append(user)
            #rewriting database
print("options")
print(options)
#print(type(myfollowers[0]))#str


#PART 2: get the numbers of follow/unfollow today
delta = 20 #delta difference between follow_today unfollow
#follow_today_number = random.randint(370, 380)
follow_today_number = 157
#unfollow_today_number = follow_today_number + random.randrange(-delta,delta)
unfollow_today_number = 382



#PART 3: get the users to follow/unfollow today
unfollow_today = []
follow_today = []
if len(unfollow) > unfollow_today_number:
    unfollow_today = random.sample(unfollow, unfollow_today_number)
    follow_today = random.sample(follow, follow_today_number)
    print("follow today: " + str(follow_today_number))
    print("unfollow today: " + str(unfollow_today_number))
    print("follow: " + str(len(follow)))
    print("unfollow: " + str(len(unfollow)))
else:
    unfollow_today = random.sample(unfollow, len(unfollow))
    follow_today = random.sample(follow, follow_today_number)
    print("follow today: " + str(follow_today_number))
    print("unfollow today: " + str(len(unfollow)))
    print("follow: " + str(len(follow)))
    print("unfollow: " + str(len(unfollow)))


todays_plan = follow_today + unfollow_today
random.shuffle(todays_plan)

with open("todays_plan_1.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(todays_plan[0:(len(todays_plan)//2)])

with open("todays_plan_2.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(todays_plan[(len(todays_plan)//2):])


#PART 4: Rewrite the table counter:
unfollow_today_ids = [unfollow_today[i][1] for i in range(len(unfollow_today))]
follow_today_ids = [follow_today[i][1] for i in range(len(follow_today))]
for i in range(len(database)):
    if database[i][1] in follow_today_ids:
        database[i][0] = "0"
        print(database[i])

    elif database[i][0] == "0":
        database[i][0] = str(int(database[i][0]) + 1)#counter
        print(database[i])

    elif database[i][0] == "1" and (database[i][1] in unfollow_today_ids):
        if database[i][1] in myfollowers:
            database[i][0] = "Yes"#followed us back
        else:
            database[i][0] = "No"#not followed us back - burn in hell
        print(database[i])


with open("toronto_processed_new.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(database)
