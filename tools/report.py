import csv
import datetime
import io
import pickle
import enum

import numpy as np
import matplotlib.pyplot as plt
import json
import jinja2
import sys
import os

import matplotlib
matplotlib.use("svg")

print(sys.argv)

# with open("fragen.json") as f:
#     question_info = json.load(f)['fragen']
# name_to_types = {info['name']: info['typ'] for info in question_info}




def generate_report(answers, survey_info, date):

    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        bundle_dir = os.path.dirname(sys.executable)
    else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    print(bundle_dir)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(bundle_dir), autoescape=jinja2.select_autoescape)

    template = env.get_template('report.html.jinja')


    VOTE_RATE_GRADE_DICT = {2: 2, 1: 3, 0: 4, 3: 3, 5: 1, 4: 5}
    # VOTE_GROUP_DICT = {2: "Gruppe 1", 3: "Gruppe 5", 0: "Gruppe 3", 5: "Gruppe 2", 4: "Gruppe 4"}
    VOTE_GROUP_INT_DICT = {2: 1, 3: 5, 0: 3, 5: 2, 4: 4}
    VOTE_GENDER_DICT = {3: "männlich", 1: "weiblich"}

    def decode(answers):
        decoded = {}
        for q in answers:
            cube_answers = {}
            for c in answers[q]:
                answer = answers[q][c]
                if q == 'Geschlecht':
                    dec_ans = VOTE_GENDER_DICT[answer]
                elif q == 'Gruppe':
                    dec_ans = VOTE_GROUP_INT_DICT[answer]
                else:
                    dec_ans = VOTE_RATE_GRADE_DICT[answer]
                cube_answers[c] = dec_ans
            decoded[q] = cube_answers
        return decoded

    dec = decode(answers)
    print(dec)


    def filter_rate_only(dec_answers):
        filtered = {}
        for q in dec_answers:
            if q != 'Gruppe' and q != 'Geschlecht':
                filtered[q] = dec_answers[q]
        return {q: dec_answers[q] for q in dec_answers if q != 'Gruppe' and q != 'Geschlecht'}

    def average_per_question(dec_answers):
        avgs = {}
        rate_only = filter_rate_only(dec_answers)
        for q, ans in rate_only.items():
            rates = list(ans.values())
            if len(rates) == 0:
                continue
            avg = sum(rates)/len(rates)
            avgs[q] = avg
        return avgs


    def answers_from_gender(dec_answers, gender):
        gender_answers = dec_answers['Geschlecht']
        gender_cubes = {c for c, ans in gender_answers.items() if ans == gender}
        return {q: {c: a for c, a in ans.items() if c in gender_cubes} for q, ans in dec_answers.items()}

    def answers_from_group(dec_answers, group):
        group_answers = dec_answers['Gruppe']
        group_cubes = {c for c, ans in group_answers.items() if ans == group}
        return {q: {c: answers[q][c] for c in a.items() if c in group_cubes} for q, a in dec_answers.items()}
            

    avgs = average_per_question(dec)

    female_ans = answers_from_gender(dec, "weiblich")
    female_avgs = average_per_question(female_ans)

    male_ans = answers_from_gender(dec, "männlich")
    male_avgs = average_per_question(male_ans)


    stream = io.BytesIO()
    fig = plt.figure(figsize=(10, 8))
    y = [avgs[q] for q in avgs]
    labels = [q for q in avgs]
    plt.bar(labels, y)
    plt.grid()
    plt.xlabel('Frage')
    plt.ylabel('Bewertung')
    plt.xticks(rotation = 45)
    plt.ylim(0, 5)
    plt.subplots_adjust(bottom=0.3)
    fig.savefig(stream, format='svg')
    svg = stream.getvalue().decode()

    stream = io.BytesIO()
    fig = plt.figure(figsize=(10, 8))
    y = list(female_avgs.values())
    labels = list(female_avgs.keys())
    plt.bar(labels, y)
    plt.grid()
    plt.xlabel('Frage')
    plt.ylabel('Bewertung')
    plt.xticks(rotation = 45)
    plt.ylim(0, 5)
    plt.subplots_adjust(bottom=0.3)
    fig.savefig(stream, format='svg')
    female_avg_svg = stream.getvalue().decode()

    stream = io.BytesIO()
    fig = plt.figure(figsize=(10, 8))
    y = list(male_avgs.values())
    labels = list(male_avgs.keys())
    plt.bar(labels, y)
    plt.grid()
    plt.xlabel('Frage')
    plt.ylabel('Bewertung')
    plt.xticks(rotation = 45)
    plt.ylim(0, 5)
    plt.subplots_adjust(bottom=0.3)
    fig.savefig(stream, format='svg')
    male_avg_svg = stream.getvalue().decode()


    html = template.render(date=date, avg_svg=svg, female_avg_svg=female_avg_svg, male_avg_svg=male_avg_svg)
    with open(os.path.join(bundle_dir, f'report-{date}.html'), 'w', encoding='utf-8') as f:
        f.write(html)

    header = ['ID'] + list(dec.keys()) + ['Schule', 'Klasse']
    cubes = {c for ans in dec.values() for c in ans}
    flatten_answer = []
    for c in cubes:
        row = [c]
        for q in dec:
            ans = dec[q]
            if c in ans:
                row.append(ans[c])
            else:
                row.append(None)
        row += [survey_info['school_type'], survey_info['grade']]
        flatten_answer.append(row)
    # flatten_answer = {c: {q: dec[q][c] for q in dec} for c in cubes}
    with open(os.path.join(bundle_dir, f'report-{date}.csv'), 'w', encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(header)
        writer.writerows(flatten_answer)
        
if len(sys.argv) > 1:
    survey_file = sys.argv[1]
    with open(survey_file, "rb") as f:
        data = pickle.load(f)
    answers = data['answers']
    survey_info = data['survey_info']
    filename = os.path.basename(survey_file).split('.')[0]
    i = filename.find('-')
    date = filename[i+1:]
    generate_report(answers, survey_info, date)
    
else:
    print("Usage: python report.py <survey_file>")