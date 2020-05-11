import pymongo 
import pandas as pd 
import numpy as np
import random
import json 
import dns

from active_learning_utils import ActiveLearner
from active_learning_utils import EgalLearner
from active_learning_utils import random_sampling, uncertainty_sampling 

pd.options.mode.chained_assignment = None

client = pymongo.MongoClient('mongodb+srv://eoghan:Ailbhe123@fypcluster-cqcwt.mongodb.net/test?retryWrites=true&w=majority')
db = client.beta_db
comments = db.comments

# load all labelled comments and downsample the positive comments to 
# balance the dataset
labelled_comments = list(comments.find({"label" : { "$exists" : "true"}}))
df = pd.DataFrame(labelled_comments)
#df = pd.concat([df[df['label'] == 0].sample(125, random_state = 1),df[df['label'] == 1]])
#df = df.reset_index()
#
outfile = 'uncertainty_sampling_larger_batch_size.csv'

def active_learning_experiment(classifier, sampling_func, n_iterations = 10, batch_size = 1, labelled_pool_size = 10, labelled_pool_limit = 250):

    results = pd.DataFrame()
    results['size'] = list(range(labelled_pool_size,labelled_pool_limit))
    results = results.set_index('size')
    suffixes = ['_a','_b','_c','_d','_e','_f','_g','_h','_i','_j']

    for i in range(1, n_iterations + 1):

        if sampling_func == 'egal': 
            learner = EgalLearner(df = df, labelled_pool_size = 10, 
                    classifier = classifier, rand_state = i,
                    batch_size = batch_size)
            sampling = sampling_func+'_'+classifier
        else : 
            learner = ActiveLearner(df = df, labelled_pool_size = 11, 
                    classifier = classifier, rand_state = i,
                    batch_size = batch_size, sampling_func = sampling_func)
            sampling = sampling_func.__name__+'_'+classifier

        performance = []
        while len(learner.labelled) < labelled_pool_limit: 
            print(sampling)
            print("experiment {}, {}".format(i,len(learner.labelled)))
            perf = {'BAS' : learner.predict(), 'size': len(learner.labelled)}
            performance.append(perf)
            learner.iterate()
        
        exp = pd.DataFrame(performance).set_index('size')
        results = results.join(exp, rsuffix = suffixes[i-1])
    results['sampling'] = sampling
    results['batch_size'] = batch_size
    return results


#active_learning_experiment('svm', random_sampling, batch_size = 10).to_csv(outfile) 
#active_learning_experiment('svm', uncertainty_sampling, batch_size = 10).to_csv(outfile, mode = 'a', header = False) 
#active_learning_experiment('svm', 'egal').to_csv(outfile, mode = 'a', header = False)       
#active_learning_experiment('random_forest', random_sampling, batch_size = 10).to_csv(outfile, mode = 'a', header = False) 
active_learning_experiment('random_forest', uncertainty_sampling, batch_size = 20).to_csv(outfile) 
#active_learning_experiment('random_forest', 'egal').to_csv(outfile, mode = 'a', header = False)       

active_learning_experiment('random_forest', uncertainty_sampling, batch_size = 30).to_csv(outfile, mode = 'a', header = False) 
active_learning_experiment('random_forest', uncertainty_sampling, batch_size = 40).to_csv(outfile, mode = 'a', header = False) 
active_learning_experiment('random_forest', uncertainty_sampling, batch_size = 50).to_csv(outfile, mode = 'a', header = False) 
