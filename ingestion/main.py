from ingestion.pipeline import setup_ingestion_logger
from cli import run_ingestion

if __name__ == "__main__":
    setup_ingestion_logger()
    run_ingestion()

# Before running it put eml files in mailbox/inbox, NOT IN MAILBOX cause it will compute the mails if they're not in 'inbox' directory

# WARNING : the parsing is not long, but the requests for domain age and redirect url is very very long. It's must take
# some time for many mails

# the run will make an advertissment in console (there is no spam and hame file or something like that)
# it's normal I deleted theses files cause it can confused someone who use it

# If you want to do a new training dataset, go in mailbox, create 'ham' directory, 'spam' directory, and add the eml in theses
# the label columns will be fused with the name of the directory you put the eml in
