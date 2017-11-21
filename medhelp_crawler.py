from bs4 import BeautifulSoup as bs
from url_fetcher import handle_req_tries
from question import Question
from answer import Answer
from topic import Topic
from subtopic import Subtopic
import math

class MedHelpCrawler:
    #number max of tries in request
    max_tries = 1
    #base url of MedHelp
    url_base = 'http://www.medhelp.org'
    #constructor
    def __init__(self, max_tries):
        self.set_max_tries(max_tries)
    #sets number max of tries
    def set_max_tries(self, max_tries):
        self.max_tries = max_tries
    def extract_topics(self):
        try:
            web_page = handle_req_tries(self.url_base+'/forums/list', self.max_tries)
        except ConnectionError:
            raise ConnectionError('unable to connect to '+url)
        else:
            souped_page = bs(web_page, 'html.parser')
            topics = []
            for group in souped_page.find('div', {'id' : 'tier_one_forums'}).findAll('div', {'class' : 'forum_group'}):
                subtopics = []
                for subtopic in group.findAll('div', {'class' : 'forums_link'}):
                    subtopics.append(Subtopic(self.concatenate_string_array(subtopic.find('a').contents)
	                , subtopic.find('a')['href']))
                    topics.append(Topic(self.concatenate_string_array(group.find('div', {'class' : 'forum_group_title'}).contents)
		        , subtopics))
            return topics
    #returns all links present on a max number of pages of questions for a disease topic
    def extract_questions(self, url):
        page = 1
        links_list = []
        try:
            max_pages = math.ceil(int(self.extract_max_pages(url)) / 20)
        except ConnectionError:
            raise ConnectionError('couldn\'t check max pages')
        while page <= max_pages:
            try:
                web_page = handle_req_tries(self.url_base+url+'?page='+str(page), self.max_tries)
            except ConnectionError:
                raise ConnectionError('unable to connect to '+url)
            else:
                souped_page = bs(web_page, 'html.parser')
                for link in souped_page.findAll('div', {'class' : 'fonts_resizable_subject subject_title hn_16b'}):
                    links_list.append(link.find('a')['href'])
                page+=1
                return links_list
    #returns all links for a question
    def extract_search_questions(self, search):
        page = 1
        links_list = []
        try:
            max_pages = math.ceil(int(self.extract_max_pages_search('/search?cat=posts&query='+search)) / 20)
        except ConnectionError:
            raise ConnectionError('unable to connect to '+url)
        else:
            while page <= max_pages:
                try:
                    web_page = handle_req_tries(self.url_base+'/search?cat=posts&query='+search+'&page='+str(page), self.max_tries)
                except ConnectionError:
                    raise ConnectionError('unable to conclude the search '+search)
                else:
                    souped_page = bs(web_page, 'html.parser')
                    for link in souped_page.find_all('div', {'class' : 'fonts_resizable_subject subject_title hn_16b'}):
                        links_list.append(link.find('a')['href'])
                finally:
                    page+=1
            return links_list
    def extract_answers(self, url):
        page = 1
        answers = []
        try:
            max_pages = int(self.extract_max_answers_pages(url))
        except ConnectionError:
            raise ConnectionError('unable to connect to url'+url)
        else:
            while page <= max_pages:
                try:
                    web_page = handle_req_tries(self.url_base+url+'?page='+str(page), self.max_tries)
                except ConnectionError:
                    raise ConnectionError('unable to retrieve all answers')
                else:
                    souped_page = self.remove_br_tags(bs(web_page, 'html.parser'))
                    for answer in souped_page.find('div', {'id' : 'post_answer_body'}).findAll('div', {'class' : 'post_entry_right'}):
                        post_id = answer.find('div', {'class' : 'post_message'})['data-post_id']
                        answers.append(Answer(answer.find('a')['id']
                            , answer.find('a')['href']
                            , self.concatenate_string_array(self.convert_a_tags(answer.find('div', {'class', 'post_message'})).contents)
                            , answer.find('time', {'class', 'mh_timestamp'})['data-timestamp']
                            , int(answer.find('span', {'id' : 'user_rating_count_Post_'+post_id}).contents[0])
                            , post_id))
                        page+=1
                    return answers
    #returns a object of type question containing data available in given question url
    def extract_question_page(self, url):
        try:
            web_page = handle_req_tries(self.url_base+url, self.max_tries)
            answers = self.extract_answers(url)
        except ConnectionError:
            raise ConnectionError('unable to connect to '+url)
        else:
            souped_page = self.remove_br_tags(bs(web_page, 'html.parser'))
            return Question(''.join(x.strip() for x in souped_page.find('div', {'class': 'question_title hn_16b'}).contents)
                , souped_page.find('div', {'class', 'subj_user os_12'}).find('a')['id']
    	        , souped_page.find('div', {'class', 'subj_user os_12'}).find('a')['href']
    	        , self.concatenate_string_array(self.convert_a_tags(souped_page.find('div', {'class', 'post_message'})).contents)
	        , answers
	        , souped_page.find('time', {'class', 'mh_timestamp'})['data-timestamp']
                , souped_page.find('div', {'class', 'post_message'})['data-post_id'])
    def extract_max_answers_pages(self, question_url):
        try:
            web_page = handle_req_tries(self.url_base+question_url, self.max_tries)
        except ConnectionError:
            raise ConnectionError('unable to connect to url'+question_url)
        else:
            souped_page = bs(web_page, 'html.parser')
            return self.concatenate_string_array(souped_page.find('div', {'class' : 'page_count'}).contents).split(' ')[3]
    def extract_max_pages(self, subtopic_url):
        try:
            web_page = handle_req_tries(self.url_base+subtopic_url, self.max_tries)
        except ConnectionError:
            raise ConnectionError('unable to connect to '+url)
        else:
            souped_page = bs(web_page, 'html.parser')
            return self.concatenate_string_array(souped_page.find('span', {'class' :  'forum_subject_count os_14'}).contents).split(' ')[4][:-1]
    def extract_max_pages_search(self, url):
        try:
            web_page = handle_req_tries(self.url_base+url, self. max_tries)
        except ConnectionError:
            raise ConnectionError('unable to connect to '+url)
        else:
            souped_page = bs(web_page, 'html.parser')
            return souped_page.find('div', {'class' :  'results_title'}).contents[0].split(' ')[0]
    #removes br tags from a souped page
    def remove_br_tags(self, souped_page):
        for br in souped_page.findAll('br'):
            br.extract()
        return souped_page

    def convert_a_tags(self, souped_page):
        for a in souped_page.findAll('a'):
            a.replaceWith(a['href'])
        return souped_page
    #concatenates an array of strings, also trimming each string
    def concatenate_string_array(self, array):
        return ''.join(x.strip() for x in array)
