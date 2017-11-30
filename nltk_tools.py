from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from nltk.stem.wordnet import WordNetLemmatizer
from fuzzywuzzy import fuzz
from math import log
from distance_measures import exec_similarity
import nltk.data
import json
import pprint
import os

#checks whether a set of words exists in a text
def dictionary_matcher(tokens, synonyms):
    for token in tokens:
        for synonym in synonyms:
            if fuzzy_comparison(token, synonym, 100):
                return True
    return False

#checks whether a set of ngrams exists in a text
def ngram_matcher(tokens, grams, n):
    if n == 1:
        return dictionary_matcher(tokens, grams)
    for token in ngrams(tokens, n):
        for gram in grams:
            flag = True
            for x, y in zip(token, gram):
                if not fuzzy_comparison(x, y, 100):
                    flag = False
            if flag is True:
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

def fuzzy_comparison(w1, w2, threshold):
    return fuzz.ratio(WordNetLemmatizer().lemmatize(w1),
                      WordNetLemmatizer().lemmatize(w2)) >= threshold

#counts how many times a term occurs in a set of words
def count_term(term, bag, gram_length):
    if gram_length == 1:
        return sum([1 if fuzzy_comparison(term, word, 100) else 0 for word in bag])
    return sum([1 if False not in [False if not fuzzy_comparison(x, y, 100) else True for x, y in zip(term, gram)] else 0 for gram in ngrams(bag, gram_length)])

#checks the existence of terms in a sentence, returning the frequency of those which occurs
def term_frequency_counter(sentence, terms):
    frequency_list = {}
    for key_term in terms.keys():
        for term in terms[key_term]:
            frequency_list.update({term : count_term(term, lowerize_words(extract_stopwords(word_tokenizer(sentence))), int(key_term))})
    return frequency_list

#checks the existence of terms in a sentence, returning the frequency of those which occurs
def concept_frequency_counter(sentence, dictionary):
    frequency_list = {}
    for concept in dictionary.keys():
        frequency_counter = 0
        for key_term in dictionary[concept].keys():
            for term in dictionary[concept][key_term]:
                frequency_counter += count_term(term, lowerize_words(extract_stopwords(word_tokenizer(sentence))), int(key_term))
        frequency_list.update({concept : frequency_counter})
    return frequency_list

#verifies whether a set of terms occurs in a sentence
def check_sentence_terms(sentence, terms):
    for key_term in terms.keys():
        if ngram_matcher(lowerize_words(extract_stopwords(word_tokenizer(sentence))), terms[key_term], int(key_term)):
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
        filtered_senteces = merge_dictionaries(filtered_sentences, concept_frequency_counter(sentence, terms))
    return filtered_sentences

#verifies whether a set of terms occurs in a text
def check_text_terms(text, terms):
    for sentence in sentence_tokenizer(text):
        if check_sentence_terms(sentence, terms):
            return True
    return False

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
            gram_length = 1 if type(term) is str else len(term)
            term_frequency += count_term(term, word_tokenizer(file['question']+' '+file['title']), gram_length)
            term_frequency += sum([count_term(term, word_tokenizer(answer['answer']), gram_length) for answer in file['answers']])
    return term_frequency

#moves .json files not containing preeclampsia-related terms on their title and question
def remove_not_related_questions(directory):
    terms = json.load(open('terms.json', 'r'))['synonyms']
    if not os.path.exists(os.path.join(os.path.join(os.getcwd(), directory), 'not_related_question')):
        os.makedirs(os.path.join(os.path.join(os.getcwd(), directory), 'not_related_question'))
    for filename in os.listdir(directory):
        if not os.path.isdir(os.path.join(directory, filename)):
            file = json.load(open(os.path.join(os.path.join(os.getcwd(), directory), filename), 'r'))
            if not (check_text_terms(file['question'], terms) or check_text_terms(file['title'], terms)):
                os.rename(os.path.join(os.path.join(os.getcwd(), directory), filename), os.path.join(os.path.join(os.path.join(os.getcwd(), directory), 'not_related_question'), filename))

#moves .json files not whose all answers received no vote
def remove_irrelevant_answers(directory):
    terms = json.load(open('terms.json', 'r'))['synonyms']
    if not os.path.exists(os.path.join(os.path.join(os.getcwd(), directory), 'irrelevant_answers')):
        os.makedirs(os.path.join(os.path.join(os.getcwd(), directory), 'irrelevant_answers'))
    for filename in os.listdir(directory):
        if not os.path.isdir(os.path.join(directory, filename)):
            file = json.load(open(os.path.join(os.path.join(os.getcwd(), directory), filename), 'r'))
            if sum(int(answer['votes']) for answer in file['answers']) == 0:
                os.rename(os.path.join(os.path.join(os.getcwd(), directory), filename), os.path.join(os.path.join(os.path.join(os.getcwd(), directory), 'irrelevant_answers'), filename))

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
def save_term_idf(directory, term, total_documents):
    if not os.path.exists(os.path.join(os.getcwd(), directory)):
        return 0
    idf_frequencies = json.load(open('term_idf.json', 'r')) if os.path.isfile('term_idf.json') else {}
    term_idf = {}
    if type(term) is str and not term in idf_frequencies.keys():
        term_idf = {term : idf(total_documents, get_document_frequency(term, directory))}
    elif (type(term) is list or type(term) is tuple) and not '_'.join(term) in idf_frequencies.keys():
        term_idf = {"_".join(term) : idf(total_documents, get_document_frequency(term, directory))}
    idf_frequencies.update(term_idf)
    with open('term_idf.json', 'w') as file:
        file.write(json.dumps(idf_frequencies, sort_keys=True, indent=4))
    return term_idf

def get_concept_idf(directory, terms, total_documents):
    frequency = 0
    for key in terms.keys():
        for term in terms[key]:
            frequency += get_document_frequency(term, directory)
    return idf(total_documents, frequency)

def save_concept_idf(directory, terms, concept, total_documents):
    if not os.path.exists(os.path.join(os.getcwd(), directory)):
        return 0
    concept_idf_frequencies = json.load(open('concept_idf.json', 'r')) if os.path.isfile('concept_idf.json') else {}
    if concept not in concept_idf_frequencies.keys():
        concept_idf = {concept : get_concept_idf(directory, terms, total_documents)}
    concept_idf_frequencies.update(concept_idf)
    with open('concept_idf.json', 'w') as file:
        file.write(json.dumps(concept_idf_frequencies, sort_keys=True, indent=4))
    return concept_idf

#returns calculated idfs they have been calculated, empty python dictionary otherwise
def retrieve_term_idfs():
    return json.load(open('term_idf.json', 'r')) if os.path.isfile('term_idf.json') else {}

def retrieve_concept_idfs():
    return json.load(open('concept_idf.json', 'r')) if os.path.isfile('concept_idf.json') else {}

#calculates tf-idf for all terms found on a document
def tf_idf_for_document(text, terms):
    document_frequencies = concept_frequency_counter(text, terms)
    tf_idf_results = {}
    total_documents = get_total_documents('downloaded_pages')
    calculated_idfs = retrieve_concept_idfs()
    for concept in terms.keys():
        concept_idf = calculated_idfs[concept] if concept in calculated_idfs.keys() else save_concept_idf('downloaded_pages', terms[concept], concept, total_documents)
        tf_idf_results.update({concept : tf_idf(tf(document_frequencies[concept], len(word_tokenizer(text))), concept_idf)})
    return tf_idf_results

def get_tf_idf_matrix(file, terms):
    file.update({'tf_idf' : tf_idf_for_document(file['title']+' '+file['question'], terms)})
    [answer.update({'tf_idf' : tf_idf_for_document(answer['answer'], terms)}) for answer in file['answers']]
    return file

def rank_algorithm(dict_list, algorithm):
    if algorithm not in dict_list[0]:
        return {}
    sorted_list = sorted([value[algorithm] for value in dict_list], reverse=True)
    for answer in dict_list:
        for rank in sorted_list:
            if answer[algorithm] == rank:
                answer.update({'rank_'+algorithm:sorted_list.index(rank)+1})
    return dict_list

def rank_votes(dict_list):
    sorted_list = sorted([answer['votes'] for answer in dict_list])
    for answer in dict_list:
        for rank in sorted_list:
            if answer['votes'] == rank:
                answer.update({'rank_votes':sorted_list.index(rank)+1})
    return dict_list

def compare_to_votes(answers, algorithm):
    if 'rank_'+algorithm not in answers[0].keys():
        return {}
    sorted_votes = sorted([value['rank_votes'] for value in answers])
    sorted_algorithm = sorted([value['rank_'+algorithm] for value in answers])
    ranking = {algorithm:[], 'votes':[]}
    checked = []
    for answer in answers:
        for rank in sorted_votes:
            if answer['rank_votes'] == rank and answer not in checked:
                ranking['votes'].append({'answer':answer['answer'],'id':answer['post_id'],'rank':answer['rank_votes']})
                checked.append(answer)
    checked = []
    for answer in answers:
        for rank in sorted_algorithm:
            if answer['rank_'+algorithm] == rank and answer not in checked:
                ranking[algorithm].append({'answer':answer['answer'],'id':answer['post_id'],'rank':answer['rank_'+algorithm]})
                checked.append(answer)
    return ranking

def compare_algorithms(answers, algorithms):
    ranking = {}
    [ranking.update({algorithm : []}) for algorithm in algorithms]
    for algorithm in algorithms:
        if 'rank_'+algorithm not in answers[0].keys():
                continue
        sorted_algorithm = sorted([value['rank_'+algorithm] for value in answers])
        checked = []
        for answer in answers:
            for rank in sorted_algorithm:
                if answer['rank_'+algorithm] == rank and answer not in checked:
                    ranking[algorithm].append({'answer':answer['answer'],'id':answer['post_id'],'rank':answer['rank_'+algorithm]})
                    checked.append(answer)
    return ranking

def get_algorithms():
    return ['braycurtis'
            , 'canberra'
            , 'chebyshev'
            , 'cityblock'
            , 'correlation'
            , 'cosine'
            , 'euclidean'
            #, 'mahalanobis'
            #, 'minkowski'
            #, 'seuclidean'
            , 'sqeuclidean'
            #, 'wminkowski'
            , 'dice'
            , 'hamming'
            , 'jaccard'
            , 'kulsinski'
            , 'rogerstanimoto'
            , 'russellrao'
            , 'sokalmichener'
            , 'sokalsneath'
            #, 'yule'
    ]

def rank_answers(file, algorithms):
    terms = json.load(open('terms.json', 'r'))
    tf_idf_file = get_tf_idf_matrix(file, terms)
    for algorithm in algorithms:
        exec_similarity(tf_idf_file, algorithm)
        rank_algorithm(tf_idf_file['answers'], algorithm)
    rank_votes(tf_idf_file['answers'])
    return tf_idf_file

def get_algorithms_comparison(file, algorithms):
    return compare_algorithms(rank_answers(file, algorithms)["answers"], algorithms)

def get_votes_comparison(file, algorithms, algorithm):
    return compare_to_votes(rank_answers(file, algorithms)["answers"], algorithm)

def save_concepts_idf():
    total_documents = get_total_documents('downloaded_pages')
    terms = json.load(open('terms.json', 'r'))
    for concept in terms.keys():
        save_concept_idf('downloaded_pages', terms[concept], concept, total_documents)

def exec_corpus_comparison(directory):
    if not os.path.exists(os.path.join(os.getcwd(), directory)):
        return 0
    if not os.path.exists(os.path.join(os.getcwd(), 'comparisons')):
        os.makedirs('comparisons')
    for filename in os.listdir(directory):
        if not os.path.isdir(os.path.join(directory, filename)):
            if not os.path.exists(os.path.join(os.path.join(os.getcwd(), 'comparisons'), filename.strip('.json'))):
                os.makedirs(os.path.join('comparisons', filename.strip('.json')))
            file = json.load(open(os.path.join(os.path.join(os.getcwd(), directory), filename), 'r'))
            file = rank_answers(file, get_algorithms())
            file['answers'] = rank_votes(file['answers'])
            for algorithm in get_algorithms():
                with open(os.path.join(os.path.join('comparisons', filename.strip('.json'), algorithm+'.json')), 'w') as f:
                    f.write(json.dumps(get_votes_comparison(file, get_algorithms(), algorithm), sort_keys=True, indent=4))
        
def main():
    #remove_irrelevant_answers('downloaded_pages')
    #remove_not_related_questions('downloaded_pages')

    exec_corpus_comparison('downloaded_pages')
                          
    #for key in terms.keys():
    #    for term in terms[key]:
    #        save_term_idf('downloaded_pages', term, total_documents)
    #save_concepts_idf()

    #file = json.load(open('downloaded_pages/diabetes-and-dieting.json', 'r'))
    #file = rank_answers(file, get_algorithms())
    #file['answers'] = rank_votes(file['answers'])
    #pprint.pprint(file['answers'])
    #for algorithm in get_algorithms():
        #pprint.pprint(get_votes_comparison(file, get_algorithms(), algorithm))
    
    #pprint.pprint(compare_to_votes(tf_idf_file['answers'], 'sokalsneath'))
    #pprint.pprint(compare_algorithms(tf_idf_file['answers'], algorithms))
    #pprint.pprint(tf_idf_file)
    
if __name__ == '__main__':
    main()
