from github import Github
from datetime import datetime
import pandas as pd
import os


# Use your Own Github api key
github = Github("your api key")
repo_name ='ckan'
milestone_name = 'Phase 1'
start_date = '2019-09-23'
end_date = '2019-09-30'
fullname = 'InstituteforDiseaseModeling/{}'.format(repo_name)
repo = [r for r in github.get_user().get_repos() if r.full_name == fullname][0]
milestone = [m for m in repo.get_milestones(state='open') if m.title == milestone_name][0]
labels = [ l for l in  repo.get_labels()]
all_issues = repo.get_issues(milestone=milestone, state="all")
prefix_keys = ["previous week", "current remaining", "new", "closed"]
active_labels = []

issues_bucket ={}
def add_to_bucket(prefix, issue):
    key_total = prefix + "total"
    if key_total in issues_bucket:
        issues_bucket[key_total] += 1
    else:
        issues_bucket[key_total] = 1
    for l in labels:
        key = prefix + l.name
        if l in issue.labels:
            if l.name not in active_labels:
                active_labels.append(l.name)
            if key in issues_bucket:
                issues_bucket[key] += 1
            else:
                issues_bucket[key] = 1

def print_html():
    df = pd.DataFrame(index=prefix_keys, columns=['total'] + active_labels)
    for i in sorted(issues_bucket.keys()):
        key = i.split('_')[0]
        label = i.split('_')[1]
        df[label][key]= issues_bucket[i]
    html = df.fillna(0).to_html('report.html')
    os.system("start report.html")

for issue in all_issues:
    if issue.created_at >= datetime.strptime(start_date, '%Y-%m-%d') and issue.created_at < datetime.strptime(end_date, '%Y-%m-%d'):
        prefix ="new_"
        add_to_bucket(prefix, issue)
    if issue.created_at < datetime.strptime(start_date, '%Y-%m-%d') and \
            (issue.closed_at is None or  issue.closed_at >= datetime.strptime(start_date, '%Y-%m-%d')):
        prefix ="previous week_"
        add_to_bucket(prefix, issue)
    if issue.closed_at is not None and \
        issue.closed_at >= datetime.strptime(start_date, '%Y-%m-%d'):
        prefix = "closed_"
        add_to_bucket(prefix, issue)
    if issue.closed_at is None:
        prefix = "current remaining_"
        add_to_bucket(prefix, issue)

for i in sorted(issues_bucket.keys()):
    print(i, ":", str(issues_bucket[i]))

print_html()
