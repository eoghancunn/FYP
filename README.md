This is the repo for my final year project. 

--Text Classification of UKC Comments-- 

REQUIREMENTS:
The requirements directory contains the requirements.txt files for the different aspects of the project. For example the python requirements to repeat the evaluations aspect of the project can be installed in your python environment using 
'pip install -r evalutaion_requirements.txt'

DATA COLLECTION:
All scripts and notebooks for data collection are found in the scraping folder. scraping_comments.py script downloads comments to be stored locally in a json format. populate.py iterates through these json files and populates the MongoDB database. Additional, non-textual features are collected and added to the MongoDB database with the get_additional_features.py and add_additional_features.py scripts respectively. Access to the database can be granted on request (IP address must be whitelisted) however a full version of the dataset is available for download here https://www.dropbox.com/s/bzpdpsw8iitctcr/comment_dataset.csv?dl=0. 

ANNOTATION INTERFACE:
The code for the annotation interface flask app is provided in the annotation_interface dir. At the time of submission this application is available at http://137.43.49.56/. Examiners are encouraged to login using 'temp' and try it out. A copy of the intructions that were provided to annotators is provdided in the Annotation Environment Instructions pdf

ACTIVE LEARNING: 
All the code required for active learning implementation and experimentation is provided in active_learning_utils.py. 
Our active learning experiments are in active_learning_exp.py. The script used to query our active learning samples is active_learning_implement.py

EVALUATION:
Each of the notebooks for evaluation is provided in the evaluations directory. 
