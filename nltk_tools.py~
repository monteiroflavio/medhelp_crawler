from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel, polynomial_kernel, sigmoid_kernel, rbf_kernel, laplacian_kernel, chi2_kernel
from math import log
import numpy
import nltk.data
import json
import pprint
import os

#checks whether a set of words exists in a text
def dictionary_matcher(tokens, synonyms):
    for synonym in synonyms:
        for token in tokens:
            if token == synonym:
                return True
    return False

#checks whether a set of ngrams exists in a text
def ngram_matcher(tokens, grams, n):
    if n == 1:
        return dictionary_matcher(tokens, grams)
    for gram in grams:
        text_grams = ngrams(tokens, n)
        for gr in text_grams:
            if tuple(gram) == gr:
                return True
    return False

#tokenizes a text at word-level
def word_tokenizer(text):
    return word_tokenize(text)

#tokenizes a text at sentence-level
def sentence_tokenizer(text):
    return nltk.data.load('tokenizers/punkt/english.pickle').tokenize(text)

#removes english stopwords from a set of words
def extract_stopwords(words):
    return [word for word in words if word not in stopwords.words('english')]

#turns words in lower case
def lowerize_words(words):
    return [word.lower() for word in words]

#counts how many times a term occurs in a set of words
def count_term(term, bag):
    frequency = 0
    for word in bag:
        if word == term:
            frequency+=1
    return frequency

#checks the existence of terms in a sentence, returning the frequency of those which occurs
def filter_sentence_relevance(sentence, terms):
    frequency_list = {}
    for key_term in terms.keys():
        for term in terms[key_term]:
            if int(key_term) == 1:
                counter = count_term(term, word_tokenizer(sentence))
                #if counter > 0:
                frequency_list.update({term : counter})
            else:
                counter = count_term(tuple(term), list(ngrams(word_tokenizer(sentence), int(key_term))))
                #if counter > 0:
                frequency_list.update({tuple(term) : counter})
    return frequency_list

#verifies whether a set of terms occurs in a sentence
def check_sentence_terms(sentence, terms):
    for key_term in terms.keys():
        if ngram_matcher(extract_stopwords(word_tokenizer(sentence)), terms[key_term], int(key_term)):
            return True
    return False

#merges two python dictionary objects
def merge_dictionaries(dict_1, dict_2):
    for term in dict_2.keys():
        if term in dict_1.keys():
            dict_1[term]+= dict_2[term]
        else:
            dict_1.update({term : dict_2[term]})
    return dict_1

#returns the occurrence of terms in a text
def get_text_frequencies(text, terms):
    filtered_sentences = {}
    for sentence in sentence_tokenizer(text):
        filtered_senteces = merge_dictionaries(filtered_sentences, filter_sentence_relevance(sentence, terms))
    return filtered_sentences

#verifies whether a set of terms occurs in a text
def check_text_terms(text, terms):
    for sentence in sentence_tokenizer(text):
        if check_sentence_terms(sentence, terms):
            return True
    return False

#moves .json files not containing preeclampsia-related terms on their title and question
def remove_not_related_questions():
    terms = json.load(open('preeclampsia_related_terms.json', 'r'))['preeclampsia']
    if not os.path.exists(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), 'not_related_question')):
        os.makedirs(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), 'not_related_question'))
    for filename in os.listdir('preeclampsia'):
        if not os.path.isdir(os.path.join('preeclampsia', filename)):
            file = json.load(open(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), filename), 'r'))
            if not (check_text_terms(file['question'], terms) or check_text_terms(file['title'], terms)):
                os.rename(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), filename), os.path.join(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), 'not_related_question'), filename))

#moves .json files not whose all answers received no vote
def remove_irrelevant_answers():
    terms = json.load(open('preeclampsia_related_terms.json', 'r'))['preeclampsia']
    if not os.path.exists(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), 'irrelevant_answers')):
        os.makedirs(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), 'irrelevant_answers'))
    for filename in os.listdir('preeclampsia'):
        if not os.path.isdir(os.path.join('preeclampsia', filename)):
            file = json.load(open(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), filename), 'r'))
            if sum(int(answer['votes']) for answer in file['answers']) == 0:
                os.rename(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), filename), os.path.join(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), 'irrelevant_answers'), filename))

#counts the total files in a folder
def get_total_documents(directory):
    if not os.path.exists(os.path.join(os.getcwd(), directory)):
        return 0
    count = 0
    for filename in os.listdir(directory):
        if not os.path.isdir(os.path.join(directory, filename)):
            count+=1 #+1 for title and question, which are grouped
            count+=len(json.load(open(os.path.join(os.path.join(os.getcwd(), directory), filename), 'r'))['answers'])
    return count

#counts the term frequency in all files for a given folder
def get_document_frequency(term, directory):
    if not os.path.exists(os.path.join(os.getcwd(), directory)):
        return 0
    term_frequency = 0
    for filename in os.listdir(directory):
        if not os.path.isdir(os.path.join(directory, filename)):
            file = json.load(open(os.path.join(os.path.join(os.getcwd(), directory), filename), 'r'))
            if type(term) is str:
                term_frequency += count_term(term, word_tokenizer(file['question']+' '+file['title']))
                term_frequency += sum(count_term(term, word_tokenizer(answer['answer'])) for answer in file['answers'])
            else:
                term_frequency += count_term(term, ngrams(word_tokenizer(file['question']+' '+file['title']), len(term)))
                term_frequency += sum(count_term(term, ngrams(word_tokenizer(answer['answer']), len(term))) for answer in file['answers'])
    return term_frequency

#calculates inverse document frequency for a given term
def idf(total_documents, term_frequency):
    denominator = term_frequency if term_frequency > 0 else 1
    return log(total_documents/denominator, 2)

#calculates term frequency
def tf(times_occurrence, document_length):
    return times_occurrence/document_length

#calculates tf-idf
def tf_idf(tf, idf):
    return tf * idf

#checks, for each term in a set of terms, if it exists on a .json file, if it does not, calculates its idf and store in the file
def save_idf(directory, term, total_documents):
    if not os.path.exists(os.path.join(os.getcwd(), directory)):
        return 0
    idf_frequencies = json.load(open('idf.json', 'r')) if os.path.isfile('idf.json') else {}
    term_idf = {}
    if type(term) is str and not term in idf_frequencies.keys():
        term_idf = {term : idf(total_documents, get_document_frequency(term, 'preeclampsia'))}
    elif (type(term) is list or type(term) is tuple) and not '_'.join(term) in idf_frequencies.keys():
        term_idf = {"_".join(term) : idf(total_documents, get_document_frequency(term, 'preeclampsia'))}
    idf_frequencies.update(term_idf)
    with open('idf.json', 'w') as file:
        file.write(json.dumps(idf_frequencies, sort_keys=True, indent=4))
    return term_idf

#returns calculated idfs they have been calculated, empty python dictionary otherwise
def retrieve_idfs():
    return json.load(open('idf.json', 'r')) if os.path.isfile('idf.json') else {}

#calculates tf-idf for all terms found on a document
def tf_idf_for_document(text, terms):
    document_frequencies = get_text_frequencies(text, terms)
    tf_idf_results = {}
    total_documents = get_total_documents('preeclampsia')
    calculated_idfs = retrieve_idfs()
    for term in document_frequencies.keys():
        if term in [tuple(key.split('_')) if (type(term) is tuple or type(term) is list) else key for key in calculated_idfs.keys()]:
            if type(term) is str:
                tf_idf_results.update({term : tf_idf(tf(document_frequencies[term], len(word_tokenizer(text))), calculated_idfs[term])})
            else:
                tf_idf_results.update({term : tf_idf(tf(document_frequencies[term], len(word_tokenizer(text))), calculated_idfs['_'.join(term)])})
        else:
            term_idf = save_idf('preeclampsia', term, get_total_documents('preeclampsia'))
            if type(term) is str:
                tf_idf_results.update({term : tf_idf(tf(document_frequencies[term], len(word_tokenizer(text))), term_idf[term])})
            else:
                tf_idf_results.update({term : tf_idf(tf(document_frequencies[term], len(word_tokenizer(text))), term_idf['_'.join(term)])})
    return tf_idf_results

def get_tf_idf_matrix(file, terms):
    file.update({'tf_idf' : tf_idf_for_document(file['title']+' '+file['question'], terms)})
    [answer.update({'tf_idf' : tf_idf_for_document(answer['answer'], terms)}) for answer in file['answers']]
    return file

def exec_similarity(matrix, algorithm):
    return {
        'cosine_similarity' : lambda matrix: [answer.update({'cosine_similarity':numpy.asscalar(cosine_similarity(ndarray_dict(matrix['tf_idf']),ndarray_dict(answer['tf_idf'])))}) for answer in matrix['answers']],
        'linear_kernel' : lambda matrix: [answer.update({'linear_kernel':numpy.asscalar(linear_kernel(ndarray_dict(matrix['tf_idf']),ndarray_dict(answer['tf_idf'])))}) for answer in matrix['answers']],
        'polynomial_kernel' : lambda matrix: [answer.update({'polynomial_kernel':numpy.asscalar(polynomial_kernel(ndarray_dict(matrix['tf_idf']), ndarray_dict(answer['tf_idf'])))}) for answer in matrix['answers']],
        'sigmoid_kernel' : lambda matrix: [answer.update({'sigmoid_kernel':numpy.asscalar(sigmoid_kernel(ndarray_dict(matrix['tf_idf']), ndarray_dict(answer['tf_idf'])))}) for answer in matrix['answers']],
        'rbf_kernel' : lambda matrix: [answer.update({'rbf_kernel':numpy.asscalar(rbf_kernel(ndarray_dict(matrix['tf_idf']), ndarray_dict(answer['tf_idf'])))}) for answer in matrix['answers']],
        'laplacian_kernel' : lambda matrix: [answer.update({'laplacian_kernel':numpy.asscalar(laplacian_kernel(ndarray_dict(matrix['tf_idf']), ndarray_dict(answer['tf_idf'])))}) for answer in matrix['answers']],
        'chi2_kernel' : lambda matrix: [answer.update({'chi2_kernel':numpy.asscalar(chi2_kernel(ndarray_dict(matrix['tf_idf']), ndarray_dict(answer['tf_idf'])))}) for answer in matrix['answers']]
    }[algorithm](matrix)

def ndarray_dict(dictionary):
    return numpy.array(list(dictionary.values())).reshape(1,-1)

def rank_metric(dict_list, metric):
    sorted_list = sorted([value[metric] for value in dict_list], reverse=True)
    ranking = []
    for answer in dict_list:
        for rank in sorted_list:
            if answer[metric] == rank:
                ranking.append({'answer':answer['answer'],'rank':sorted_list.index(rank)+1})
    return ranking

def rank_votes(dict_list):
    sorted_list = sorted([int(answer['votes']) for answer in dict_list])
    ranking = []
    for answer in dict_list:
        for rank in sorted_list:
            if int(answer['votes']) == rank:
                ranking.append({'answer':answer['answer'], 'rank':sorted_list.index(rank)+1})
    return ranking

def compare_results(dict_list, metric):
    return {
        'userVotes' : rank_votes(dict_list),
        metric : rank_metric(dict_list, metric)
    }
    
def main():
    file = json.load(open(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), '1st-pregnancy-severe-pre-eclampsia-what-are-my-odds-for-the-second.json'), 'r'))
    terms = json.load(open('preeclampsia_related_terms.json', 'r'))['preeclampsia']

    algorithms = ['cosine_similarity', 'linear_kernel', 'polynomial_kernel', 'sigmoid_kernel', 'rbf_kernel', 'laplacian_kernel', 'chi2_kernel']
    #tf_idf_file = get_tf_idf_matrix(file, terms)
    #tf_idf_file['answers'] = rank_votes(tf_idf_file['answers'])
    #for algorithm in algorithms:
        #exec_similarity(tf_idf_file, algorithm)
        #pprint.pprint(compare_results(tf_idf_file['answers'], algorithm), indent=4)
        
    #total_documents = get_total_documents('preeclampsia')
    #for gram_length in terms:
    #    [save_idf('preeclampsia', term, total_documents) for term in terms[gram_length]]
    
    #print(get_text_frequencies(file['title']+' '+file['question'], terms))

    #remove_not_related_questions()
    remove_irrelevant_answers()
    
    #print(check_text_terms(question, terms))

if __name__ == '__main__' : main()
