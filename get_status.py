from github import Github
from datetime import datetime, date, timedelta
import pandas as pd
import os
import argparse


prefix_keys = ["previous week", "new", "closed", "current remaining"]

def get_report(apikey):
    github = Github(apikey)
    repo_names =['ckan', 'dst-era5-weather-data-tools', 'dse-utility-library']
    today = date.today()
    this_monday = (today + timedelta(days=-today.weekday()))
    start_date = (this_monday + timedelta(days=-7)).strftime("%Y-%m-%d")
    end_date = this_monday.strftime("%Y-%m-%d")
    html ="<h1>Github Status Report  {}<h1> <br>".format(end_date)
    for repo_name in repo_names:
        fullname = 'InstituteforDiseaseModeling/{}'.format(repo_name)
        repo = [r for r in github.get_user().get_repos() if r.full_name == fullname][0]
        milestones = [m for m in repo.get_milestones(state='open')]
        for milestone in milestones:
            labels = [ l for l in repo.get_labels()]
            all_issues = repo.get_issues(milestone=milestone, state="all")
            active_labels = ['not labeled']
            buckets = count_issues(all_issues, start_date, end_date, labels, active_labels)
            html = print_html(buckets, html, active_labels, "{} - {}".format(repo.name, milestone.title))
        # get items without milestone, a.k.a. untriaged issues
        untriaged_issues = repo.get_issues(milestone='none', state='open')
        html += "<hr><h2>{} - Untriaged: {} </h2>".format(repo.name, str(untriaged_issues.totalCount))
        html += '<hr style="border-top: 3px solid red;">'
    save(html)

def add_to_bucket(prefix, issue, issues_bucket, labels, active_labels):
    key_total = prefix + "total"
    if key_total in issues_bucket:
        issues_bucket[key_total] += 1
    else:
        issues_bucket[key_total] = 1
    if len(issue.labels) == 0:
        key = prefix + 'not labeled'
        if key in issues_bucket:
            issues_bucket[key] += 1
        else:
            issues_bucket[key] = 1
    for l in labels:
        key = prefix + l.name
        if l in issue.labels:
            if l.name not in active_labels:
                active_labels.append(l.name)
            if key in issues_bucket:
                issues_bucket[key] += 1
            else:
                issues_bucket[key] = 1

def highlight(x):
    focus = ["bug", "priority: must-fix", "total"]
    return ['background-color: yellow' if x.name in focus else '' for v in x]

def print_html(issues_bucket, html, active_labels, header):
    df = pd.DataFrame(index=prefix_keys, columns=['total'] + active_labels)
    for i in sorted(issues_bucket.keys()):
        key = i.split('_')[0]
        label = i.split('_')[1]
        df[label][key]= issues_bucket[i]
    df_report = df.fillna(0).transpose()
    new_html = html + " <hr> "
    new_html += "<h2>{}</h2>".format(header)
    new_html += df_report.style.set_properties(**
                                          {'border-style': 'solid',
                                           'color': 'black'}).apply(highlight, axis=1).render()
    return new_html


def save(html):
    f = open("report.html", "w")
    f.write(html)
    #html = df_report.to_html('report.html')
    os.system("start report.html")

def count_issues (all_issues, start_date, end_date, labels, active_labels):
    issues_bucket = {}
    for issue in all_issues:
        if issue.created_at >= datetime.strptime(start_date, '%Y-%m-%d') and issue.created_at < datetime.strptime(end_date, '%Y-%m-%d'):
            prefix ="new_"
            add_to_bucket(prefix, issue, issues_bucket, labels, active_labels)
        if issue.created_at < datetime.strptime(start_date, '%Y-%m-%d') and \
                (issue.closed_at is None or  issue.closed_at >= datetime.strptime(start_date, '%Y-%m-%d')):
            prefix ="previous week_"
            add_to_bucket(prefix, issue, issues_bucket, labels, active_labels)
        if issue.closed_at is not None and \
            issue.closed_at >= datetime.strptime(start_date, '%Y-%m-%d'):
            prefix = "closed_"
            add_to_bucket(prefix, issue, issues_bucket, labels, active_labels)
        if issue.closed_at is None:
            prefix = "current remaining_"
            add_to_bucket(prefix, issue, issues_bucket, labels, active_labels)
    return issues_bucket

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apikey", help="your github api key")
    args = parser.parse_args()
    get_report(args.apikey)


