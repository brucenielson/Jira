# A program to collect all the blocking issues and prioritize them based on how many cards they are blocking
from jira import JIRA
import logging
import getpass
import os
import time
from collections import defaultdict
from datetime import datetime

# from importlib import reload

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


def make_priority_list(jira, list):
    blocked_by_list = []
    if list == []:
        return

    # Check each item on the block list
    for card in list:
        links = card.fields.issuelinks
        if len(links) == 0:
            logging.info('Card ' + str(card.key) + ' has no links. It should not have been in the list.')
            print 'Card ' + str(card.key) + ' has no links. It should not have been in the list.'
            continue

        # Create a list of links blocking this card
        blocked_by_cards = [link.inwardIssue.key for link in links if link.type.name == 'Blocks' and hasattr(link, "inwardIssue") and
                           not (link.inwardIssue.fields.status.name == 'Ready For Test' or link.inwardIssue.fields.status.name == 'Done')]

        print str(card.key) + ': ' + str(blocked_by_cards)
        # Create final list of IDs of cards blocking other cards and a count of how many times it was found to be blocking another card
        # Final Format is {'CSI-1234': 3}
        blocked_by_list += blocked_by_cards

    # Make count in a dictionary
    issue_count = defaultdict(int)
    for id in blocked_by_list:
        issue_count[id] += 1

    # Create final matrix - convert dict to list
    return issue_count.items()


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



# Main Program Flow

# Give user name and password
user = raw_input('User Name: ')
password = getpass.getpass(prompt='Password: ')

# Login to Jira
jira = connect_jira('https://jira.youngliving.com/', user, password)

# Get current sprint
current_sprint, start = get_current_sprint(jira)

# Check all links the moved cards blocked and see if any can be unblocked
blocked_list = jira.search_issues('project = CSI AND Flagged = Impediment and sprint = "' + current_sprint + '" ORDER BY key ASC', maxResults=250)
blocked_by_list = make_priority_list(jira, blocked_list)
# Sort count in the tuple
blocked_by_list.sort(key=lambda tup: tup[1], reverse=True)  # sorts in place

thefile = open('Blocked By List.txt', 'w')
for item in blocked_by_list:
    #print "%s: %d\n" % (item[0], item[1])
    thefile.write("%s: %d\n" % (item[0], item[1]))

thefile.close()

raw_input("Press Enter to continue...")
