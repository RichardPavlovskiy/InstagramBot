from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from InstagramAPI import InstagramAPI
import pandas as pd
import time
import os
import multiprocessing
from functools import partial
import sys
import glob
import time
import csv



def getFollowersList(target_username_id, maxResults):
    retUsers = []
    nextMaxId = ''
    while len(retUsers) < maxResults:
        api.getUserFollowers(target_username_id, nextMaxId)
        usersJson = api.LastJson
        try:
            for user in usersJson['users']:
                if len(retUsers) < maxResults:
                    retUsers.append([user['pk'], user['username'], user['has_anonymous_profile_picture'], user['full_name'], user['is_private']])
                else:
                    return retUsers
                    break
        except KeyError as e:
            print("KeyError occured while getFollowersList(): " + str(e))
            time.sleep(120)

        try:
            if usersJson['big_list'] == True:
                nextMaxId = usersJson['next_max_id']
            else:
                return retUsers
                break
        except KeyError as e:
            print("KeyError occured while getFollowersList(): " + str(e))
            time.sleep(120)



def close_notification(driver1):
    try:
        close_msg = driver1.find_element_by_xpath('/html/body/span/section/nav/div[2]/div/div/div[3]/div/div/div/button').click()
        print("notification closed")
        return True
    except NoSuchElementException:
        return None

def get_user_data(driver1):
    posts_number = driver1.find_element_by_xpath('/html/body/span/section/main/div/header/section/ul/li[1]/a/span').text
    posts_number = ''.join([i if i not in ['k','m',',','.'] else '000' if i == 'k' else '000000' if i == 'm' else '' for i in posts_number])


    followers_number = driver1.find_element_by_xpath('/html/body/span/section/main/div/header/section/ul/li[2]/a/span').text
    followers_number = ''.join([i if i not in ['k','m',',','.'] else '000' if i == 'k' else '000000' if i == 'm' else '' for i in followers_number])


    following_number = driver1.find_element_by_xpath('/html/body/span/section/main/div/header/section/ul/li[3]/a/span').text
    following_number = ''.join([i if i not in ['k','m',',','.'] else '000' if i == 'k' else '000000' if i == 'm' else '' for i in following_number])
    return posts_number, followers_number, following_number

def ExtandFollowersList(order,starting_number, end_number):
    k=0
    position_x=0
    position_y=0
    window_size=400

    print("Starting post processing...")
    with open('database/highgirlsclub' + str(order)+'.csv', 'r') as f:
        reader = csv.reader(f)
        users = []
        for i in reader:
            users.append(list(i))

    #headless browser setup
    options = Options()
    options.headless = True

    driver1 = webdriver.Firefox(executable_path = '/usr/local/bin/geckodriver', options=options)
    #driver1.set_window_position(position_x, position_y)
    #driver1.set_window_size(window_size, window_size)

    for i in range(len(users)):
        if i%20 == order and i//20 >= starting_number and (i//20 < end_number or end_number == -1):
            #clean all cache and cookies
            driver1.delete_all_cookies()

            k = i//20#the number  of current username
            sleep_msg = False
            error_msg = False
            timeout_msg = False
            profile_link = "https://www.instagram.com/" + str(users[i][1])+"/"
            try:
                driver1.get(profile_link)
            except TimeoutException as ex:
                print("timeout exception :)")
                timeout_msg = True
                driver1.quit()
                time.sleep(121)

                driver1 = webdriver.Firefox(executable_path = '/usr/local/bin/geckodriver', options=options)
                driver1.get(profile_link)


            notification = close_notification(driver1)

            try:
                msg = driver1.find_element_by_xpath('/html/body/div/div[1]/div/div/h2').text
                if msg == "Error":
                    sleep_msg = True
                elif msg == "Sorry, this page isn't available.":
                    error_msg = True
            except NoSuchElementException:
                sleep_msg = False
                error_msg = False

            if sleep_msg == False and error_msg == False and timeout_msg == False:
                posts_number, followers_number, following_number = get_user_data(driver1)
                users[i].extend([int(posts_number), int(followers_number), int(following_number)])
                driver1.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
                print("Agent " + str(order)+" Processed " + str(k) + " out of "+ str(len(users)//20) + " " + str(users[i][1]) +  " " + posts_number + " " + followers_number + " " + following_number)

            elif sleep_msg == True:
                print("Agent "+str(order)+": got a sleep msg")
                time.sleep(120)

                print("Agent #"+str(order)+" got out of sleep")
                driver1.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
                driver1.get(profile_link)
                notification = close_notification(driver1)

                #check if there is no error message
                try:
                    msg = driver1.find_element_by_xpath('/html/body/div/div[1]/div/div/h2').text
                    if msg == "Sorry, this page isn't available.":
                        error_msg = True
                except NoSuchElementException:
                    error_msg = False


                if  error_msg == True:
                    users[i].extend([0, 0, 0])
                    print("Agent " + str(order)+" got an ERROR " + str(k) + " out of "+ str(len(users)//20) + " " + str(users[i][1]) + " 0, 0, 0")
                    driver1.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
                else:
                    posts_number, followers_number, following_number = get_user_data(driver1)
                    users[i].extend([int(posts_number), int(followers_number), int(following_number)])
                    driver1.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
                    print("Agent " + str(order)+" Processed " + str(k) + " out of "+ str(len(users)//20) + " " + str(users[i][1]) +  " " + posts_number + " " + followers_number + " " + following_number)

            elif error_msg == True:
                users[i].extend([0, 0, 0])
                print("Agent " + str(order)+": changed USERNAME error " + str(k) + " out of "+ str(len(users)//20) + " " + str(users[i][1]) + " 0, 0, 0")

            elif timeout_msg == True:
                users[i].extend([0, 0, 0, "timeout"])
                print("Agent " + str(order)+": TIMEOUT error" + str(k) + " out of "+ str(len(users)//20) + " " + str(users[i][1]) + " 0, 0, 0")

            with open("database/highgirlsclub" + str(order) +".csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(users)

def get_final_table(order):
    with open('highgirlsclub.csv', 'r') as f:
        reader = csv.reader(f)
        toronto_table = []
        for i in reader:
            toronto_table.append(list(i))

    agents = [[] for i in range(order)]
    for i in range(order):
        with open('database/highgirlsclub'+str(i)+'.csv', 'r') as f:
            reader = csv.reader(f)
            for line in reader:
                agents[i].append(list(line))

    final_table = []
    for j in range(len(toronto_table)):
        if len(toronto_table[j]) < len(agents[j%20][j]):
            final_table.append(agents[j%20][j])
        else:
            print("not complited")
            print(agents[j%20][j])
            final_table.append([None,None,None,None,None,None])


    with open("highgirlsclub_finaltable.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(final_table)


    return final_table


"""
api = InstagramAPI("hollyweedstudios", "richardson")
api.login()

#PART 1 FIRST SCANNING
target_username = "highgirlsclub"
api.searchUsername(target_username)
target_username_id = api.LastJson["user"]["pk"]
retUsers = getFollowersList(target_username_id, 150000)



print("Number of followers: " + str(len(retUsers)))
with open("highgirlsclub.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(retUsers)

#PART 2 SECONDARY SCANNING
functions_data = [(11,4166,-1),(17,0,-1),(18,4353,-1),(19,1350,-1)]

"""
#PART 3 GETTING Final csv table
final_table = get_final_table(20)


"""
#RUN FOR PART 2 ONLY
if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=len(functions_data))
    result_list = pool.starmap(ExtandFollowersList, functions_data)
    pool.close()
    pool.join()
"""
