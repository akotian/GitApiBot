import calendar
import requests

from datetime import datetime


USERNAME = ''
TOKEN = ''
REPO_NAME = ''
BASE_URL = 'https://api.github.com/repos/{0}/'.format(REPO_NAME)
BEGIN_MONTH = '2015-{0}-01'.format(datetime.now().month)
# BEGIN_MONTH = '2015-10-01'
now = datetime.now()
CURRENT_MONTH, LAST_DAY = calendar.monthrange(now.year, now.month)
END_MONTH = datetime(now.year, now.month, LAST_DAY)
PARAMS = {'since': BEGIN_MONTH}

report = {'issues': {'open': {}, 'closed': {}},
          'pulls': {'open': {}, 'closed': {}}}


def update_report(issue_data, data_type,
                  issue_state,  user_key, date_key):
    issue_date = issue_data.get(date_key)
    issue_date = datetime.strptime(issue_date, '%Y-%m-%dT%H:%M:%SZ')
    begin_month = datetime.strptime(BEGIN_MONTH, '%Y-%m-%d')
    if (issue_date >= begin_month
        and issue_date <= END_MONTH):
        user = issue_data.get(user_key) and \
            issue_data.get(user_key).get('login') or {}
        user_counts = report[data_type][issue_state]
        if user_counts.get(user):
            user_counts[user] += 1
        else:
            user_counts[user] = 1


def parse_issue(issue_data, data_type):
    issue_state = issue_data.get('state')
    if issue_state == 'open':
        user_key, comparison_date = 'user', 'created_at'
        update_report(issue_data, data_type, issue_state,
                      user_key='user', date_key='created_at')
    elif issue_state == 'closed':
        # For reporter
        update_report(issue_data, data_type, issue_state='open',
                      user_key='user', date_key='created_at')
        # For assignee
        update_report(issue_data, data_type, issue_state,
                      user_key='assignee', date_key='closed_at')


def print_report(key, data):
    print "---{0}---".format(key)
    for key, value in data.items():
        print "### {0}".format(key)
        values = sorted(value, key=value.get, reverse=True)
        for key in values:
            print "{0} --> {1}".format(key, value.get(key))



def display_report(report):
    print 'PULLS--####'
    pulls = report.get('pulls')
    issues = report.get('issues')
    open_pulls = pulls.get('open')
    print_report("Pulls", pulls)
    print_report("Issues", issues)



def get_issues():
    issues_url = BASE_URL + 'issues'
    print issues_url
    PARAMS['state'] = 'all'
    print PARAMS
    r = requests.get(
            issues_url, auth=(USERNAME, TOKEN), params=PARAMS)
    for issue in r.json():
        if issue.get('pull_request'):
            parse_issue(issue_data=issue, data_type='pulls')
        else:
            parse_issue(issue_data=issue, data_type='issues')
    print 'We should be done--'
    display_report(report)



def get_report():
    get_issues()


get_report()
