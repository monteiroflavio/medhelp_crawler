import os
import json
import random
#import matplotlib.pyplot as plt
#import numpy as np
from medhelp_crawler import MedHelpCrawler
from question import Question
import time

medhelp_crawler = MedHelpCrawler(3)
topics = []

def complex_handler(obj):
    if hasattr(obj, 'jsonable'):
        return obj.jsonable()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj)))
    
def get_topics():
    try:
        topics = medhelp_crawler.extract_topics()
    except ConnectionError:
        print('couldn\'t get topics')
        return []
    else:
        return topics
    
def get_questions_links(subtopic_url):
    try:
        question_links = medhelp_crawler.extract_questions(subtopic_url)
    except ConnectionError:
        print('couldn\'t get question links')
        return []
    else:
        return question_links
    
def save_topics(topics):
    for topic in topics:
        for subtopic in topic.subtopics:
            if not os.path.isdir(os.path.join(os.getcwd(), sanitize_name(topic.title), sanitize_name(subtopic.title))):
                os.makedirs(os.path.join(os.getcwd(), sanitize_name(topic.title), sanitize_name(subtopic.title)))
                
def save_questions_links(topic_path, subtopic_path, questions_links):
    f = open(os.path.join(os.getcwd(), topic_path, subtopic_path, 'questions_links.txt'), 'w')
    for question_link in questions_links:
        f.write(question_link+'\n')
    f.close()
    
def save_question_page(question_url):
    try:
        question = medhelp_crawler.extract_question_page(question_url)     
    except ConnectionError:
        raise ConnectionError('unable to download requested page')
    else:
        index = ''
        if os.path.isfile(question_url.split('/')[3].lower()+'.json'):
            while os.path.isfile(question_url.split('/')[3]+str(index)+'.json'):
                if index is '':
                    index = 1
                else:
                    index+=1
        f = open(question_url.split('/')[3].lower()+str(index)+'.json', 'w')
        f.write(jsonify(question))
        f.close()
        
def save_question_pages(subtopic_url):
    try:
        questions_links = get_questions_links(subtopic_url)
    except ConnectionError:
        print('couldn\'t get question links')
    else:
        for question_link in questions_links:
            save_question_page(question_link)
            
def jsonify(jsonable_obj):
    return json.dumps(jsonable_obj, sort_keys=True, indent=4, default=complex_handler)

def sanitize_name(str):
    return ''.join([c for c in str if c.isalpha() or c.isdigit() or c is ' ' or c is '.']).lower().replace(' ', '_')

def save_links(search_string):
    f = open('links.txt', 'w')
    try:
        list = medhelp_crawler.extract_search_questions(search_string)
    except ConnectionError:
        raise ConnectionError('error on gathering links for term '+search_string)
    else:
        for link in list:
            f.write(link+'\n')
    finally:
        f.close()

def save_pages():
    f = open('links.txt', 'r')
    links = f.readlines()
    for link in links:
        try:
            save_question_page(link.strip())
            links.remove(link)
            print('success at downloading '+link.strip()+' - '+str(len(links))+' remaining')
        except ConnectionError:
            raise ConnectionError('an error occurred while downloading page '+ link.strip())
        finally:
            f.close()
            f = open('links.txt','w')
            for link in links:
                f.write(link)
            f.close()

def check_pages_time_range(directory):
    latest_timestamp = time.time()
    newest_timestamp = 0
    for filename in os.listdir(directory):
        question = json.load(open(os.path.join(os.path.join(os.getcwd(), directory), filename), 'r'))
        if int(question['timestamp']) < latest_timestamp:
            latest_timestamp = int(question['timestamp'])
        if int(question['timestamp']) > newest_timestamp:
            newest_timestamp = int(question['timestamp'])
        for answer in question['answers']:
            if int(answer['timestamp']) < latest_timestamp:
                latest_timestamp = int(answer['timestamp'])
            if int(answer['timestamp']) > newest_timestamp:
                newest_timestamp = int(answer['timestamp'])
    return {'latest_timestamp' : latest_timestamp, 'newest_timestamp' : newest_timestamp}

def get_dates_list(directory):
    dates = []
    for filename in os.listdir(directory):
        question = json.load(open(os.path.join(os.path.join(os.getcwd(), directory), filename), 'r'))
        dates.append(int(question['timestamp']))
        for answer in question['answers']:
            dates.append(int(answer['timestamp']))
    return sorted(dates)

def download_links(search_string):
    try:
        save_links(search_string)
    except ConnectionError:
        print('an error occurred while collection pages')

def download_pages():
    while os.stat('links.txt').st_size > 0:
        try:
            save_pages()
        except ConnectionError:
            print('an error occurred. restarting for remaining links')

def remove_single_answer_questions():
    if not os.path.exists(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), 'single_answer')):
        os.makedirs(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), 'single_answer'))
    for filename in os.listdir('preeclampsia'):
        if not os.path.isdir(os.path.join('preeclampsia', filename)):
            question = json.load(open(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), filename), 'r'))
            if len(question['answers']) <= 1:
                os.rename(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), filename), os.path.join(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), 'single_answer'), filename))

#count = 0
#for answer in json.load(open('What-cycle-of-Clomid-are-you-on-any-side-effects.json', 'r'))['answers']:
#    count+=1
#print(count)

#save_question_page('/posts/Diabetes---Type-1/Do-you-have-questions-about-diabetes--/show/2987819')
#save_question_pages('/forums/Diabetes---Gestational/show/1950')

download_links('diabetes')
#download_preeclampsia_pages()

#date_set = check_latest_question()
#print('latest :'+time.ctime(date_set['latest_timestamp']))
#print('newest :'+time.ctime(date_set['newest_timestamp']))

#remove_single_answer_questions()
#remove_not_related_questions()
#remove_irrelevant_answers()

#for timestamp in get_dates_list():
#    print(time.ctime(timestamp))
