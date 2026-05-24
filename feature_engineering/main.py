from .cli import run_features

if __name__ == "__main__":
    run_features()

# The feature_engineering part returns 2 databases but only one is useful, I used a transition database (features database)
# where there is 1 row per link/attachments (useful to see some links problems or if features works)
# but the final db is "Final_datas" where the links/attachments are groupby Mail_ID and the features are gather
# in sum and mean of links features of the mails (necessary cause the model take one table, not 3)

# the features show a big problem of the project, the training dataset is old, and recent dataset, with threat,
# label and various attacks are nearly impossible to find, so model is training on old mails but I can not do anything else
# since I not have a good amount of useful datas
