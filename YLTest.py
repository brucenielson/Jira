from jira import JIRA
import logging


def connect_jira(log, jira_server, jira_user, jira_password):
    '''
    Connect to JIRA. Return None on error
    '''
    try:
        log.info("Connecting to JIRA: %s" % jira_server)
        jira_options = {'server': jira_server}
        jira = JIRA(options=jira_options,
                    # Note the tuple
                    basic_auth=(jira_user,
                                jira_password))
        return jira
    except Exception,e:
        log.error("Failed to connect to JIRA: %s" % e)
        return None



user = raw_input('User Name: ')
password = raw_input('Password: ')

jira = connect_jira(logging, 'https://jira.youngliving.com/', user, password)

issue = jira.issue('CSI-1490')
print issue.id
print issue.fields.project.key
print issue.fields.issuetype.name
print issue.fields.reporter.displayName
print issue.fields.summary
links = issue.fields.issuelinks
print links

for subissue in links:
    print subissue

len(links)


rank_order = jira.search_issues('project = CSI AND status = "Ready For Test" ORDER BY cf[10000] ASC')
print rank_order[0].key

for link in links:
    if hasattr(link, "outwardIssue"):
        outwardIssue = link.outwardIssue
        print("\tOutward: " + outwardIssue.key)
    if hasattr(link, "inwardIssue"):
        inwardIssue = link.inwardIssue
        print("\tInward: " + inwardIssue.key)







#issuecopy = jira.issue(15669)
#print issuecopy

#issuecopy = jira.issue(16943)
#print issuecopy


review_complete = jira.search_issues('project = CSI AND status = "Review Complete" ORDER BY key ASC, summary ASC')
print [issue.key for issue in review_complete]

update_issue = jira.issue(review_complete[0].key)
print update_issue.fields.status

transitions = jira.transitions(update_issue)
print [(t['id'], t['name']) for t in transitions]

#jira.transition_issue(update_issue, 61)

#print update_issue.fields.status

