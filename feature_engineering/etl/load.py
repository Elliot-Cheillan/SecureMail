import pandas as pd
import sqlite3
from feature_engineering.featuring import *
from feature_engineering.config import DATABASE_FEATURES_PATH, DATABASE_MAILS_PATH
import logging

logger = logging.getLogger(__name__)


# This time I used pandas, I don't know if it's more rapid than just sqlite3 requests but it's more logical
# and reminds kaggle projects
def load_source_dataframes():
    with sqlite3.connect(DATABASE_MAILS_PATH) as conn:
        mails_df = pd.read_sql_query("SELECT * FROM Mails", conn)
        links_df = pd.read_sql_query("SELECT * FROM Links", conn)
        attachments_df = pd.read_sql_query("SELECT * FROM Attachments", conn)
    return mails_df, links_df, attachments_df


def load_new_mails_dataframes():
    with sqlite3.connect(DATABASE_MAILS_PATH) as conn:
        mails_df = pd.read_sql_query("SELECT * FROM Mails", conn)
        links_df = pd.read_sql_query("SELECT * FROM Links", conn)
        attachments_df = pd.read_sql_query("SELECT * FROM Attachments", conn)

    # Get only the new mails on the database
    with sqlite3.connect(DATABASE_FEATURES_PATH) as conn:
        existing_mail_ids = pd.read_sql_query("SELECT ID FROM Mails_Features", conn)[
            "ID"
        ].tolist()

    new_mails_df = mails_df[~mails_df["ID"].isin(existing_mail_ids)]
    new_links_df = links_df[~links_df["Mail_Number"].isin(existing_mail_ids)]
    new_attachments_df = attachments_df[
        ~attachments_df["Mail_Number"].isin(existing_mail_ids)
    ]

    return new_mails_df, new_links_df, new_attachments_df


def build_mails_features(Mails_df):
    df = pd.DataFrame()
    df["ID"] = Mails_df["ID"]
    df["Is_Date_Coherent"] = Mails_df["Date"].apply(is_date_coherent)
    df["Is_Time_Coherent"] = Mails_df["Time"].apply(is_time_coherent)
    df["Is_Mail_Extension_Suspect"] = Mails_df["Sender_Email"].apply(
        is_mail_extension_suspect
    )
    df["Is_Reply_To_Suspect"] = Mails_df.apply(
        lambda row: is_reply_to_suspect(row["Sender_Email"], row["Reply_To_Email"]),
        axis=1,
    )
    df["Is_SPF_Result_Unapplicable"] = Mails_df["Date"].apply(
        is_spf_result_unapplicable
    )
    df["Is_SPF_Result_Suspect"] = Mails_df["SPF_Result"].apply(is_spf_result_suspect)
    df["Is_DKIM_Result_Unapplicable"] = Mails_df["Date"].apply(
        is_dkim_result_unapplicable
    )
    df["Is_DKIM_Result_Suspect"] = Mails_df["DKIM_Result"].apply(is_dkim_result_suspect)
    df["Count_Spam_Words_In_Mail"] = Mails_df.apply(
        lambda row: count_spam_words_in_mail(row["Subject"], row["Content"]), axis=1
    )
    df["Ratio_Spam_Words_In_Mail"] = Mails_df.apply(
        lambda row: ratio_spam_words_in_mail(row["Subject"], row["Content"]), axis=1
    )
    df["Number_Of_Words_Content"] = Mails_df["Content"].apply(number_of_words_content)
    df["Is_XMailer_Result_Unapplicable"] = Mails_df["X_Mailer"].apply(
        is_XMailer_result_unapplicable
    )
    df["Is_XMailer_Result_Suspect"] = Mails_df["X_Mailer"].apply(
        is_XMailer_result_suspect
    )
    df["Is_Display_Name_Suspect"] = Mails_df["Sender_Display_Name"].apply(
        is_display_name_suspect
    )
    df["Label"] = Mails_df["Label"].apply(is_spam)
    return df


def build_links_features(Links_df):
    df = pd.DataFrame()
    df["Mail_ID"] = Links_df["Mail_Number"]
    df["Is_Link_Domain_Age_Unusable"] = Links_df["Domain_Creation_Date"].apply(
        is_link_domain_age_unusable
    )
    df["Is_Link_Domain_Age_Suspect"] = Links_df.apply(
        lambda row: is_link_domain_age_suspect(
            row["Domain_Creation_Date"], row["Mail_Date"]
        ),
        axis=1,
    )
    df["Is_Redirect_Link_Unusable"] = Links_df["Redirect_URL"].apply(
        is_redirect_link_unusable
    )
    df["Is_Redirect_Link_Suspect"] = Links_df.apply(
        lambda row: is_redirect_link_suspect(
            row["Redirect_URL"], row["Domain_Creation_Date"], row["Mail_Date"]
        ),
        axis=1,
    )
    df["Is_Link_HTTP"] = Links_df["URL"].apply(is_link_http)
    df["Is_Link_An_IPAdress"] = Links_df["URL"].apply(is_link_an_ipaddress)
    df["Is_Domain_Name_Suspect"] = Links_df["Domain"].apply(is_domain_name_suspect)
    df["Is_Site_Extension_Suspect"] = Links_df["URL"].apply(is_site_extension_suspect)
    return df


def build_attachments_features(Attachments_df):
    df = pd.DataFrame()
    df["Mail_ID"] = Attachments_df["Mail_Number"]
    df["Is_Attachment_Executable"] = Attachments_df["Extension"].apply(
        is_attachement_executable
    )
    df["Is_Double_Extension"] = Attachments_df["Filename"].apply(is_double_extensions)
    df["Is_No_Extension"] = Attachments_df["Extension"].apply(is_no_extension)
    df["Is_Extension_Suspect"] = Attachments_df.apply(
        lambda row: is_extension_suspect(row["Extension"], row["Filename"]), axis=1
    )
    df["Is_File_Empty"] = Attachments_df["File_Size_Bytes"].apply(is_file_empty)
    df["Is_File_Size_Suspect"] = Attachments_df.apply(
        lambda row: is_file_size_suspect(row["File_Size_Bytes"], row["Extension"]),
        axis=1,
    )
    df["Is_Magic_Number_Suspect"] = Attachments_df.apply(
        lambda row: is_magic_number_suspect(row["Extension"], row["Magic_Number"]),
        axis=1,
    )
    return df


def inject_mails_features(conn, replace_or_append, mails_df):
    mails_features = build_mails_features(mails_df)
    mails_features.to_sql(
        "Mails_Features", conn, if_exists=replace_or_append, index=False
    )
    logger.info(f"✓ Mails_Features injectées — {len(mails_features)} lignes")


def inject_links_features(conn, replace_or_append, links_df):
    links_features = build_links_features(links_df)
    links_features.to_sql(
        "Links_Features", conn, if_exists=replace_or_append, index=False
    )
    logger.info(f"✓ Links_Features injectées — {len(links_features)} lignes")


def inject_attachments_features(conn, replace_or_append, attachments_df):
    attachments_features = build_attachments_features(attachments_df)
    attachments_features.to_sql(
        "Attachments_Features", conn, if_exists=replace_or_append, index=False
    )
    logger.info(
        f"✓ Attachments_Features injectées — {len(attachments_features)} lignes"
    )


def inject_all_features(replace_or_append):

    if replace_or_append == "replace":
        mails_df, links_df, attachments_df = load_source_dataframes()
    else:  # append
        mails_df, links_df, attachments_df = load_new_mails_dataframes()

    logger.info(
        f"Source loaded — {len(mails_df)} mails, {len(links_df)} links, {len(attachments_df)} attachments"
    )

    if mails_df.empty and links_df.empty and attachments_df.empty:
        logger.info("Rien de nouveau à injecter !")
        return

    with sqlite3.connect(DATABASE_FEATURES_PATH) as conn:
        inject_mails_features(conn, replace_or_append, mails_df)
        inject_links_features(conn, replace_or_append, links_df)
        inject_attachments_features(conn, replace_or_append, attachments_df)
