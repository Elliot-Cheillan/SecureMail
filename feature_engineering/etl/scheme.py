# Same for the database.py in ingestion, it's only the scheme of the database don't put inserts functions in it
import sqlite3
from feature_engineering.config import DATABASE_FEATURES_PATH


def create_mails_features_table(cursor):
    cursor.execute("""DROP TABLE IF EXISTS Mails_Features""")
    cursor.execute(
        """CREATE TABLE Mails_Features (
                       ID INTEGER PRIMARY KEY,
                       Is_Date_Coherent REAL,
                       Is_Time_Coherent REAL,
                       Is_Mail_Extension_Suspect REAL,
                       Is_Reply_To_Suspect REAL,
                       Is_SPF_Result_Unapplicable REAL,
                       Is_SPF_Result_Suspect REAL,
                       Is_DKIM_Result_Unapplicable REAL,
                       Is_DKIM_Result_Suspect REAL,
                       Count_Spam_Words_In_Mail REAL,
                       Ratio_Spam_Words_In_Mail REAL,
                       Number_Of_Words_Content REAL,
                       Is_XMailer_Result_Unapplicable REAL,
                       Is_XMailer_Result_Suspect REAL,
                       Is_Display_Name_Suspect REAL,
                       Label REAL)"""
    )


def create_links_features_table(
    cursor,
):  # Mail ID was a foreign key but I turned it into integer cause it's more easy to change it or use it
    cursor.execute("""DROP TABLE IF EXISTS Links_Features""")
    cursor.execute(
        """CREATE TABLE Links_Features (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Mail_ID INTEGER,
                        Is_Link_Domain_Age_Unusable REAL,
                        Is_Link_Domain_Age_Suspect REAL,
                        Is_Redirect_Link_Unusable REAL,
                        Is_Redirect_Link_Suspect REAL,
                        Is_Link_HTTP REAL,
                        Is_Link_An_IPAdress REAL,
                        Is_Domain_Name_Suspect REAL,
                        Is_Site_Extension_Suspect REAL
                        )"""
    )


def create_attachments_features_table(
    cursor,
):  # same as the links table, the ID was foreign key but it creates some useless problem
    # (and we delete the columns Mail_ID later for the gathering of tables)
    cursor.execute("""DROP TABLE IF EXISTS Attachments_Features""")
    cursor.execute(
        """CREATE TABLE Attachments_Features (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Mail_ID INTEGER,
                        Is_Attachment_Executable REAL,
                        Is_Double_Extension REAL,
                        Is_No_Extension REAL,
                        Is_Extension_Suspect REAL,
                        Is_File_Empty REAL,
                        Is_File_Size_Suspect REAL,
                        Is_Magic_Number_Suspect REAL
                        )"""
    )


def initialize_features_database():
    with sqlite3.connect(DATABASE_FEATURES_PATH) as conn:
        cursor = conn.cursor()
        create_mails_features_table(cursor)
        create_links_features_table(cursor)
        create_attachments_features_table(cursor)
