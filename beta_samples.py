import json
import os

beta_dir = "feedback_w_beta/"
beta_samples = "beta_samples.txt"

files = []

for (dirpath, dirnames, filenames) in os.walk(beta_dir):
    for f in filenames:
        files.append(os.path.join(dirpath,f))

f = open(beta_samples, "a+") 

for log in files:   
    with open(log) as json_file:
        data = json.load(json_file)
        beta = ""
        if 'label' in data:
            if data['label'] == '1':
                beta = data['comment']+"\n\n"
    f.write(beta)
    
f.close()
