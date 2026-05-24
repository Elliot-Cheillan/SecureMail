# We have all the json imports and the sets/dict of theses json in the files
import json
import os
from feature_engineering.config import DATA_DIR

# "with open" is useful to close connection to json just after getting the datas
with open(os.path.join(DATA_DIR, "spamwords_list.json"), encoding="utf-8") as f :
    spamwords_dict = json.load(f)

with open(os.path.join(DATA_DIR, "mail_extensions_list.json"), encoding="utf-8") as f:
    mail_extensions_dict = json.load(f)

with open(os.path.join(DATA_DIR, "XMailers_list.json"), encoding="utf-8") as f:
    Xmailer_dict = json.load(f)

with open(os.path.join(DATA_DIR, "public_identities.json"), encoding="utf-8") as f:
    public_identities_dict = json.load(f)

with open(os.path.join(DATA_DIR, "spoofing_substitutions.json"), encoding="utf-8") as f:
    spoofing_substitutions_dict = json.load(f)

with open(os.path.join(DATA_DIR, "domains_list.json"), encoding="utf-8") as f:
    domains_dict = json.load(f)

with open(os.path.join(DATA_DIR, "site_extensions_list.json"), encoding="utf-8") as f:
    site_extensions_dict = json.load(f)

with open(os.path.join(DATA_DIR, "file_extensions.json"), encoding="utf-8") as f:
    file_extensions_dict = json.load(f)


# here are the conversion of json in the good formats, sets or dict depending on the json structure
# but i choose set for nearly all of theses cause we need to search if elements are on these files
# in this case sets are perfect, it's quite instant to search if something is in a set
spamwords_set = set()

safe_mail_extensions = set()
common_mail_extensions = set()
suspect_mail_extensions = set()

common_XMailer = set()
suspect_Xmailer = set()

public_identities = set()

safe_domains = set()
common_domains = set()
suspect_domains = set()

safe_site_extensions = set()
common_sites_extensions = set()
suspect_sites_extensions = set()

# here theses are dict cause they have multiple categories (file extension and the ranges of bytes they usually uses)
# so I can not change them into set
executable_file_extensions = dict()
safe_file_extensions = dict()
common_file_extensions = dict()
suspect_file_extensions = dict()


# below here we adding all the elements to the sets/dict :

# spamwords
for lang in spamwords_dict.values():
    for word in lang:
        spamwords_set.add(word)

# extensions
for extension in mail_extensions_dict["safe"]:
    safe_mail_extensions.add(extension)

for extension in mail_extensions_dict["common"]:
    common_mail_extensions.add(extension)

for extension in mail_extensions_dict["suspect"]:
    suspect_mail_extensions.add(extension)

# XMailer
for name in Xmailer_dict:
    common_XMailer.add(name)

for name in Xmailer_dict["suspect"]:
    suspect_Xmailer.add(name)

# public identities
for category in public_identities_dict.values():
    for identity in category:
        public_identities.add(identity)

# domain names
for name in domains_dict["safe"]:
    safe_domains.add(name)

for name in domains_dict["neutral"]:
    common_domains.add(name)

for name in domains_dict["dangerous"]:
    suspect_domains.add(name)

# site extensions
for name in site_extensions_dict["safe"]:
    safe_site_extensions.add(name)

for name in site_extensions_dict["neutral"]:
    common_sites_extensions.add(name)

for name in site_extensions_dict["suspicious"]:
    suspect_sites_extensions.add(name)

# file extensions
for k, v in file_extensions_dict["executable"].items():
    executable_file_extensions[k] = v

for k, v in file_extensions_dict["safe"].items():
    safe_file_extensions[k] = v

for k, v in file_extensions_dict["common"].items():
    common_file_extensions[k] = v

for k, v in file_extensions_dict["suspicious"].items():
    suspect_file_extensions[k] = v

file_extensions = (
    executable_file_extensions
    | safe_file_extensions
    | common_file_extensions
    | suspect_file_extensions
)
