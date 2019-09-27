from github import Github
from datetime import datetime


# Use your Own Github api key
github = Github("your api key")
repo_name ='dst-era5-weather-data-tools'#'ckan'
milestone_name = 'ERA5 Land Data'#'Data Services Library'#'Phase 1'
start_date = '2019-09-23'
end_date = '2019-09-30'

repo = [r for r in github.get_user().get_repos() if r.name == repo_name][0]
milestone = [m for m in repo.get_milestones(state='open') if m.title == milestone_name][0]
labels = [ l for l in  repo.get_labels()]
all_issues = repo.get_issues(milestone=milestone, state="all")

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
            if key in issues_bucket:
                issues_bucket[key] += 1
            else:
                issues_bucket[key] = 1


for issue in all_issues:
    if issue.created_at >= datetime.strptime(start_date, '%Y-%m-%d') and issue.created_at < datetime.strptime(end_date, '%Y-%m-%d'):
        prefix ="new_"
        add_to_bucket(prefix, issue)
    if issue.created_at < datetime.strptime(start_date, '%Y-%m-%d') and \
            (issue.closed_at is None or  issue.closed_at >= datetime.strptime(start_date, '%Y-%m-%d')):
        prefix ="previous_"
        add_to_bucket(prefix, issue)
    if issue.closed_at is not None and \
        issue.closed_at >= datetime.strptime(start_date, '%Y-%m-%d'):
        prefix = "closed_"
        add_to_bucket(prefix, issue)
    if issue.closed_at is None:
        prefix = "remaining_"
        add_to_bucket(prefix, issue)

for i in sorted(issues_bucket.keys()):
    print(i, ":", str(issues_bucket[i]))