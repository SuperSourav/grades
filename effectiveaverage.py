import csv
import re
import itertools


def keygen(fname, scoretype):
  Scores = []
  maxscore = []
  bonuskeys = []
  bonusmaxscore = []
  conceptkeys = []
  conceptmaxscore = []
  with open(fname) as csvfile:
    reader = csv.DictReader(csvfile)
    keys = reader.fieldnames
    for k in keys:
      if (scoretype == "Lab"):
        if (re.search('^%s'%("Concept"), k)):# or (re.search('^%s'%("Lab Bonus"), k)):
          conceptkeys.append(k)
          conceptmaxscore.append(0) #concept as true bonus
        elif (re.search('^%s'%("Lab Bonus"), k)):
          bonuskeys.append(k)
          bonusmaxscore.append(0)
        else: 
          m = re.search('^%s [0-9] '%(scoretype), k)
      else:
        m = re.search('^%s'%(scoretype), k)
      if m: 
        Scores.append(k)
        maxscore.append(int(re.search('\[(\d+)\]$', k).group(1)))
      scoreexclude = scoretype
      if (scoretype == "Homework"): scoreexclude = "HW"
      if re.search('^Aextras-Excused-%s-count'%(scoreexclude), k): Excused = k
  Scores = Scores + conceptkeys + bonuskeys
  maxscore += conceptmaxscore + bonusmaxscore
  return Scores, maxscore, Excused

def keygen_midterm(fname):
  Scores = []
  maxscore = []
  with open(fname) as csvfile:
    reader = csv.DictReader(csvfile)
    keys = reader.fieldnames
    for k in keys:
      m = re.search('^%s'%("Midterm"), k)
      m1 = re.search('^%s'%("FinalExam"), k)
      if m: 
        Scores.append(k)
        maxscore.append(int(re.search('\[(\d+)\]$', k).group(1)))
      if m1:
        Scores.append(k)
        maxscore.append(int(re.search('\[(\d+)\]$', k).group(1))*0.5)
  return Scores, maxscore

def keygen_final(fname):
  Scores = []
  maxscore = []
  with open(fname) as csvfile:
    reader = csv.DictReader(csvfile)
    keys = reader.fieldnames
    for k in keys:
      m1 = re.search('^%s'%("FinalExam"), k)
      if m1: 
        Scores.append(k)
        maxscore.append(int(re.search('\[(\d+)\]$', k).group(1)))
  return Scores, maxscore

def r(y):
  r_temp = [0,0]
  for n,d in y:
    r_temp[0] += n
    r_temp[1] += d
  return r_temp[0]*1./r_temp[1]

#def exclude_average_labs1(testscores, excount, maxscore):
#  x = list(itertools.izip(testscores, maxscore))
#  bonus_x = x[-3:]
#  bonus_y = [(1.) for n,d in bonus_x]
#  x = x[:-3]
#  y = [(n*1./d) for n,d in x]
#  y_x = list(itertools.izip(y,x))
#  y_bonus_x = list(itertools.izip(bonus_y,bonus_x))
#  y_x = sorted(y_x)
#  y_x = y_x[excount:] + y_bonus_x
#  x_fin = list(itertools.izip(*y_x))[1]
#  return r(x_fin)
#
def exclude_average_labs(testscores, excount, maxscore, bonus_inc):
  x = list(itertools.izip(testscores, maxscore))
  bonus_x = x[-3:] #concept as true bonus
  x = x[:-3] #concept as true bonus
  perms = itertools.combinations(x, len(x)-excount)
  r_list = [( r(list(y)+bonus_x) if bonus_inc else r(list(y)) ) for y in perms]
  r_opt = max(r_list)
  return min(1, r_opt)

def exclude_average_rest(testscores, excount, maxscore):
  x = list(itertools.izip(testscores, maxscore))
  perms = itertools.combinations(x, len(x)-excount)
  r_list = [r(list(y)) for y in perms]
  r_opt = max(r_list)
  return r_opt
#
#def exclude_average(testscores, excount):
#  testscores.sort()
#  print excount
#  effscores = testscores[excount:]
#  return sum(effscores)*1./len(effscores)
#
def main_average(fname, scoretype, fixedoffset, switch_drop):
  if (scoretype == "Midterm"):
    tests, maxscore = keygen_midterm(fname)
  elif (scoretype == "FinalExam"):
    tests, maxscore = keygen_final(fname)
  else: 
    tests, maxscore, excused = keygen(fname, scoretype)
    print excused
  print tests
  print maxscore
#  f = open('average%s.txt'%(scoretype), 'w')
  listf = {}
  Scorelist = []
  with open(fname) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
       excount = fixedoffset
       if (scoretype != "Midterm") and (scoretype != "FinalExam"):
         if (row[excused].strip() != ''): excount =  excount + int(row[excused])
       testscores = []
       for test in tests:
         score = 0
         if (row[test].strip() != ''): 
           score = float(row[test])
           if (scoretype == "Midterm"): score = score*(0.5 if re.search('^FinalExam', test) else 1.0)
         testscores.append(score)
       print row['Student Name'] + "\t", testscores, excount
       print ">>>>", testscores, (excount if switch_drop else 0), maxscore
       if (scoretype == "Lab"): meantestscore = exclude_average_labs(testscores, (excount if switch_drop else 0), maxscore, bonus_inc)
       else: meantestscore = exclude_average_rest(testscores, (excount if switch_drop else 0), maxscore)
#       meantestscore1 = exclude_average_labs1(testscores, excount, maxscore)
       listf[row['Student Name']] = meantestscore*100
       #f.write("%s\t%s\t%f\n"%(row['Student ID'], row['Student Name'], meantestscore))
  return listf

def letter_grade(fin_score):
  index = 0
  if (fin_score >= gradeboundary[0]): grade = letter[0]
  for i in range(1,len(letter)):
    if (fin_score >= gradeboundary[i]) and (fin_score < gradeboundary[i-1]):
      grade = letter[i]
      index = i
  return grade, index
   
def main():
  global bonus_inc
  switch_drop = True
  bonus_inc = True
  fname = 'gradebook-physics141-fall2017.csv'
  scoretype = ['Midterm', 'FinalExam', 'Homework', 'Lab', 'Quiz']
  fixedoffset = [1, 0, 1, 1, 2]
  weights = [0.35, 0.25, 0.15, 0.1, 0.15]
  f = open("average.txt", 'w')
  f.write("%20s"%"Student Name"+" "*10 + (" "*10).join(scoretype) + (" "*10) + "Course score" + (" "*10) + "Letter grade\n")
  dictA = []
  global gradeboundary
  global letter
  gradeboundary = [96.9, 93, 89.8, 86.85, 83, 80, 73, 67, 58.6, 57, 53, 50, -0.1]
  letter = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"]
  freqGrade = [0]*len(letter)
  for i in range(len(scoretype)):
    dictA.append(main_average(fname, scoretype[i], fixedoffset[i], switch_drop))
  names = sorted(dictA[-1].keys())
  finscorelist = []
  nameslist = []
  linelist = []
  dictsortscore = {}
  for name in names:
    fin_score = 0
    line = ''
    for j in range(len(scoretype)):
      fin_score += weights[j]*dictA[j][name]
      line += "%10.2f\t"%(dictA[j][name])
    gradeletter, index = letter_grade(fin_score)
    freqGrade[index] += 1
    finscorelist.append(fin_score)
    nameslist.append(name)
    linelist.append("%30s"%name + "%5s%5.2f%5s\n"%(line, fin_score, gradeletter))
    dictsortscore[(fin_score, name)] = linelist[-1]
    f.write(linelist[-1])
  sortedscorekeys = sorted(list(itertools.izip(finscorelist, nameslist)), reverse=True)
  fsorted  = open("average_scoresorted.txt", 'w')
  fsorted.write("%20s"%"Name" +" "*10 + (" "*10).join(scoretype) + (" "*10) + "Score" + (" "*10) + "Grade\n")
  for sortkey in sortedscorekeys:
    fsorted.write(dictsortscore[sortkey])
  freqGradefrac = []
  den = sum(freqGrade)
  for k in range(len(freqGrade)):
    freqGradefrac.append("%.1f"%(freqGrade[k]*100./den)+"%")
  hist = list(itertools.izip(letter, freqGrade, freqGradefrac, gradeboundary))
  print hist
  f.write("\n"+(" "*5).join(["grade", "freq", "rel freq", "threshold"])+"\n")
  fsorted.write("\n" + (" "*5).join(["grade", "freq", "rel freq", "threshold"])+"\n")
  for h in hist:
    f.write((" "*10).join([str(e) for e in h]) + "\n")
    fsorted.write((" "*10).join([str(e) for e in h]) + "\n")
  fsorted.close()
  f.close()
  return 

if __name__ == '__main__':
  main()
