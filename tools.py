from collections import Counter
	




def rp(grades):
	h1dict = {'A':10,'B':8.75,'C':7.5,'D':6.25,'E':5,'S':2.5,'U':0}
	h2dict = {'A':20,'B':17.5,'C':15,'D':12.5,'E':10,'S':5,'U':0}
	total_rp = 0

	for ele in grades[:3]:
		total_rp+=h2dict[ele]
	for ele in grades[3:6]:
		total_rp+=h1dict[ele]
	return total_rp

def avg_rp(rp_lst):
	if len(rp_lst)==0:
		return
	#if only 1 record in grades
	if len(rp_lst)==1:
		return rp_lst[0]
	#if more than 1 record in grades
	n = len(rp_lst)
	total = 0
	for ele in rp_lst:
		total += ele[0]
	return round((total/n),2)



def modal_grade(gradelst):
    if len(gradelst) == 0:
        return None  # or raise an exception if appropriate
    if len(gradelst) == 1:
        return gradelst[0]

    # Count the occurrences of each grade
    grade_counts = Counter(gradelst)
    
    # Find the grade(s) with the highest count
    max_count = max(grade_counts.values())
    modal_grades = [grade for grade, count in grade_counts.items() if count == max_count]

    return modal_grades


print(avg_rp([54]))

