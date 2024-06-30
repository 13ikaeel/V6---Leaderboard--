from csv import *

file = open('h2-subjects.csv')
subjects = []
for subject in file:
    subjects.append(subject.strip())

subjects = sorted(subjects)

for ele in subjects:
    print(ele)