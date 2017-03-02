from jira import JIRA
import logging
import getpass
import os
import time

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


def get_top_card(jira):
    # Get top card
    rank_order = jira.search_issues('project = CSI AND status = "Ready For Test" ORDER BY cf[10000] ASC')
    return rank_order[0]


def get_bottom_card(jira):
    # Get top card
    rank_order = jira.search_issues('project = CSI AND status = "Ready For Test" ORDER BY cf[10000] ASC')
    return rank_order[len(rank_order)-1]



def move_to_ready_for_test(jira, list):

    if list == []:
        return

    top_card = get_top_card(jira)

    # Get Ready For Test ID
    trans_id = 0

    card = list[0]
    transitions = jira.transitions(card)
    for t in transitions:
        if (t['name'] == "Ready For Test"):
            trans_id = t['id']
            break

    for card in list:
        jira.transition_issue(card, trans_id)
        logging.info("Moved: " + str(card) + " to Ready for Test")
        print "Moved: " + str(card) + " to Ready for Test"
        # Rank to top of column
        jira.rank(card.key, top_card.key)



def remove_block_flag(card):
    logging.info('Removed flag for Card ' + str(card.key))
    card.update(fields={u'customfield_10300': None})


def add_block_flag(card):
    logging.info('Added flag for Card ' + str(card.key))
    card.update(fields={'customfield_10300': [{'value': 'Impediment'}]})


def unblock_cards(jira, list):
    if list == []:
        return

    top_card = get_top_card(jira)
    # Check each item on the block list and see if its unblocked
    for card in list:
        links = card.fields.issuelinks
        if len(links) == 0:
            logging.info('Card ' + str(card.key) + ' has no links. It should not have been in the list.')
            print 'Card ' + str(card.key) + ' has no links. It should not have been in the list.'
            remove_block_flag(card)
            continue

        # Check each link on this card and keep track if any are not completed
        is_unblocked = True
        for link in links:
            if link.type.name == 'Blocks' and hasattr(link, "inwardIssue"):
                # Is this link now Ready for Test or Done, if so, it won't block this card any more
                linked_issue = jira.issue(link.inwardIssue.key)
                status = linked_issue.fields.status.name
                if not (status == 'Ready For Test' or status == 'Done'):
                    is_unblocked = False
                    break
        # Did we find any links that were not Ready for Test or Done? If not, remove flag
        if is_unblocked:
            print 'Card ' + str(card.key) + ' has been unblocked.'
            logging.info('Card ' + str(card.key) + ' has been unblocked.')
            remove_block_flag(card)
            jira.rank(card.key, top_card.key)



def flag_blocked_cards(jira):
    review_complete = jira.search_issues(
        'project = CSI AND status = "Ready For Test" AND ("Epic Link" = null or "Epic Link" in (CSI-902, CSI-1025, CSI-1143, CSI-1446) ) and Flagged = null ORDER BY key ASC, summary ASC',
        maxResults=250)

    bottom_card = get_bottom_card(jira)
    # Check each item on the block list and see if its unblocked
    for card in review_complete:
        links = card.fields.issuelinks

        # skip everything if there are no linnks on this card as there is no way is should be blocked if it has no links
        if len(links) > 0:

            # Check each link on this card and if we find a blocking link, flag it and move on
            for link in links:
                if link.type.name == 'Blocks' and hasattr(link, "inwardIssue"):
                    # Is this link NOT Ready for Test or Done, if so, it will block this card
                    linked_issue = jira.issue(link.inwardIssue.key)
                    status = linked_issue.fields.status.name
                    if not (status == 'Ready For Test' or status == 'Done'):
                        add_block_flag(card)
                        #jira.rank(bottom_card.key, card.key)
                        print 'Card ' + str(card.key) + ' has been blocked.'
                        logging.info('Card ' + str(card.key) + ' has been blocked.')
                        break;



# Main Program Flow
# Give user name and password
user = raw_input('User Name: ')
password = getpass.getpass(prompt='Password: ')

# Login to Jira
jira = connect_jira('https://jira.youngliving.com/', user, password)


# Get list of cards read to move to ready to test
review_complete = jira.search_issues('project = CSI AND status = "Review Complete" AND ("Epic Link" = null or "Epic Link" in (CSI-902, CSI-1025, CSI-1143, CSI-1446, CSI-1155, CSI-1025) ) ORDER BY key ASC, summary ASC', maxResults=250)

# Move each card to Ready for Test and put at top of column
move_to_ready_for_test(jira, review_complete)

# Check all links the moved cards blocked and see if any can be unblocked
blocked_list = jira.search_issues('project = CSI AND Flagged = Impediment ORDER BY key ASC', maxResults=250)
unblock_cards(jira, blocked_list)
flag_blocked_cards(jira)

raw_input("Press Enter to continue...")



