# only schemes for the database, no insert functions in it (compared to the first version of the file)
def _create_mails_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS Mails")
    cursor.execute(
        """CREATE TABLE Mails (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Sender_Display_Name TEXT,
                        Sender_Email TEXT,
                        Reply_To_Email TEXT,
                        Date TEXT,
                        Time TEXT,
                        Subject TEXT,
                        X_Mailer TEXT,
                        SPF_Result TEXT,
                        DKIM_Result TEXT,
                        Content TEXT,
                        Filename TEXT,
                        Label TEXT)"""
    )


def _create_links_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS Links")
    cursor.execute(
        """CREATE TABLE Links (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Mail_Number INTEGER,
                        URL TEXT,
                        Domain TEXT,
                        Mail_Date TEXT,
                        Domain_Creation_Date TEXT,
                        Redirect_URL TEXT,
                        FOREIGN KEY (Mail_Number) REFERENCES Mails(ID))"""
    )


def _create_attachments_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS Attachments")
    cursor.execute(
        """CREATE TABLE Attachments (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Mail_Number INTEGER,
                        Filename TEXT,
                        Extension TEXT,
                        File_Size_Bytes INTEGER,
                        File_Hash TEXT,
                        Magic_Number TEXT,
                        FOREIGN KEY (Mail_Number) REFERENCES Mails(ID))"""
    )


def initialize_database(cursor):
    _create_mails_table(cursor)
    _create_links_table(cursor)
    _create_attachments_table(cursor)
