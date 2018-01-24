# https://mborgerson.com/creating-an-executable-from-a-python-script
# pyinstaller WorkTracker.py
from jira import JIRA
import logging
import getpass
import os
import time
from datetime import datetime

#os.path.dirname(os.path.realpath(__file__))
filename=os.getcwd()+'\\jira.log'
logging.basicConfig(filename=filename,level=logging.INFO)
logging.info("Starting Jira Automation Run on " + str(time.strftime("%c")))

def connect_jira(jira_server, jira_user, jira_password):
    '''
    Connect to JIRA. Return None on error
    '''
    try:
        logging.info("Connecting to JIRA: %s" % jira_server)
        jira_options = {'server': jira_server}
        jira = JIRA(options=jira_options,
                    # Note the tuple
                    basic_auth=(jira_user,
                                jira_password))
        return jira
    except Exception,e:
        logging.error("Failed to connect to JIRA: %s" % e)
        return None


def get_current_sprint(jira):
    boards = jira.boards()
    board = [b for b in boards if b.name == "CSI PM Board"][0]
    sprints = jira.sprints(board.id, extended=True)
    current_sprint = [s for s in sprints if s.state == 'ACTIVE' and (s.name.startswith('CSI') or s.name.startswith('Baseline'))][0]
    name = current_sprint.name
    start = current_sprint.startDate
    start_date = datetime.strptime(start, '%d/%b/%y %I:%M %p').date()
    print("Current Sprint: " + name + " -- Starting: " + str(start_date))

    return name, start_date

def print_issues(issues, start):
    for issue in issues:
        issue = jira.issue(str(issue), expand='changelog')
        changelog = issue.changelog

        print("")
        print("Issue: " + str(issue))

        for history in changelog.histories:
            date_str = history.created
            end_date_pos = unicode.rfind(date_str, 'T')
            created = date_str[:end_date_pos]
            created_date = datetime.strptime(created, '%Y-%m-%d').date()
            for item in history.items:
                if (item.field == 'status' or item.field == 'Comment') and created_date > start:
                    if item.field == 'Comment':
                        print 'Date:' + str(created_date) + ' Type: ' + str(item.field) + ' --  From:' + str(getattr(item, "from")) + '\tTo:' + str(item.to)
                    else:
                        print 'Date:' + str(created_date) + ' Type: ' + str(item.field) + ' --  From:' + str(item.fromString) + '\tTo:' + str(item.toString)

    return

#http://abhipandey.com/2016/05/getting-list-of-issues-from-jira-under-current-sprint/
# Main Program Flow
# Give user name and password
user = raw_input('User Name: ')
password = getpass.getpass(prompt='Password: ')

# Login to Jira
jira = connect_jira('https://jira.youngliving.com/', user, password)

#user = "kcrossman"
current_sprint, start = get_current_sprint(jira)
issues = jira.search_issues("project = CSI AND sprint = '" + current_sprint + "' AND assignee = '" + user + "'", maxResults=250)
print_issues(issues, start)


raw_input("Press Enter to continue...")



#review_complete = jira.search_issues('project = CSI AND status = "Review Complete" AND ("Epic Link" = null or "Epic Link" in (CSI-902, CSI-1025, CSI-1143, CSI-1446, CSI-1155, CSI-1025))  ORDER BY key ASC, summary ASC', maxResults=250)

