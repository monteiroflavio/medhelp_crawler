from scipy.spatial.distance import braycurtis, canberra, chebyshev, cityblock, correlation, cosine, dice, euclidean, hamming, jaccard, kulsinski, mahalanobis, matching, minkowski, rogerstanimoto, russellrao, seuclidean, sokalmichener, sokalsneath, sqeuclidean, wminkowski, yule
import numpy

def exec_similarity(dct, algorithm):
    if validate_similarity_algorithms(dct, algorithm):
        return {}
    if algorithm == 'braycurtis':
        return [answer.update({algorithm:braycurtis(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'canberra':
        return [answer.update({algorithm:canberra(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'chebyshev':
        return [answer.update({algorithm:chebyshev(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'cityblock':
        return [answer.update({algorithm:cityblock(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'correlation':
        return [answer.update({algorithm:correlation(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'cosine':
        return [answer.update({algorithm:cosine(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'euclidean':
        return [answer.update({algorithm:euclidean(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'mahalanobis':
        return [answer.update({algorithm:mahalanobis(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    #elif algorithm is 'minkowski':
        #return [answer.update({algorithm:minkowski(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'seuclidean':
        return [answer.update({algorithm:seuclidean(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'sqeuclidean':
        return [answer.update({algorithm:sqeuclidean(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'wminkowski':
        return [answer.update({algorithm:wminkowski(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'dice':
        return [answer.update({algorithm:dice(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'hamming':
        return [answer.update({algorithm:hamming(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'jaccard':
        return [answer.update({algorithm:jaccard(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'kulsinski':
        return [answer.update({algorithm:kulsinski(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'rogerstanimoto':
        return [answer.update({algorithm:rogerstanimoto(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'russellrao':
        return [answer.update({algorithm:russellrao(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'sokalmichener':
        return [answer.update({algorithm:sokalmichener(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'sokalsneath':
        return [answer.update({algorithm:sokalsneath(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]
    elif algorithm == 'yule':
        return [answer.update({algorithm:yule(ndarray_dict(dct['tf_idf']), ndarray_dict(answer['tf_idf']))}) for answer in dct['answers']]

def validate_similarity_algorithms(dct, algorithm):
    if algorithm in ['correlation', 'cosine']:
        if sum(ndarray_dict(dct['tf_idf']).tolist()[0]) == 0 or any([sum(ndarray_dict(answer['tf_idf']).tolist()[0]) == 0 for answer in dct['answers']]):
            return True
    if algorithm in ['seuclidean', 'yule']:
        if 0 in ndarray_dict(dct['tf_idf']).tolist()[0] or any([0 in ndarray_dict(answer['tf_idf']).tolist()[0] for answer in dct['answers']]):                                                                                                                                 
            return True
    return False
    
def ndarray_dict(dictionary):
    return numpy.array(list(dictionary.values())).reshape(1,-1)
