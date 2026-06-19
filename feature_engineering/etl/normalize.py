import pandas as pd
import sqlite3
import logging
from feature_engineering.config import DATABASE_FEATURES_PATH, DATABASE_FINAL_PATH

logger = logging.getLogger(__name__)


def load_features_dataframes():
    with sqlite3.connect(DATABASE_FEATURES_PATH) as conn:
        mails_features_df = pd.read_sql_query("SELECT * FROM Mails_Features", conn)
        links_features_df = pd.read_sql_query("SELECT * FROM Links_Features", conn)
        attachments_features_df = pd.read_sql_query(
            "SELECT * FROM Attachments_Features", conn
        )
    return mails_features_df, links_features_df, attachments_features_df


def create_final_mails_datas(
    mails_features_df,
):  # the funciont is useless but it's just for visalizing the methods more easily and gather them with the same name
    return mails_features_df


def create_final_links_data(links_features_df):
    feature_cols = [
        "Is_Link_Domain_Age_Unusable",
        "Is_Link_Domain_Age_Suspect",
        "Is_Redirect_Link_Unusable",
        "Is_Redirect_Link_Suspect",
        "Is_Link_HTTP",
        "Is_Link_An_IPAdress",
        "Is_Domain_Name_Suspect",
        "Is_Site_Extension_Suspect",
    ]
    empty_columns = (
        ["Mail_ID"]
        + [c + "_Sum" for c in feature_cols]
        + [c + "_Mean" for c in feature_cols]
        + ["Links_Count"]
    )

    if links_features_df.empty:
        return pd.DataFrame(columns=empty_columns)

    features_only = links_features_df.drop(columns=["Mail_ID"])

    df_sum = (
        features_only.groupby(links_features_df["Mail_ID"])
        .sum()
        .drop(columns="ID", errors="ignore")
    )
    df_mean = (
        features_only.groupby(links_features_df["Mail_ID"])
        .mean()
        .drop(columns="ID", errors="ignore")
    )

    df_sum.columns = [col + "_Sum" for col in df_sum.columns]
    df_mean.columns = [col + "_Mean" for col in df_mean.columns]

    df = pd.concat([df_sum, df_mean], axis=1)
    df["Links_Count"] = links_features_df.groupby("Mail_ID").size()

    return df.reset_index()


def create_final_attachments_data(attachments_features_df):
    feature_cols = [
        "Is_Attachment_Executable",
        "Is_Double_Extension",
        "Is_No_Extension",
        "Is_Extension_Suspect",
        "Is_File_Empty",
        "Is_File_Size_Suspect",
        "Is_Magic_Number_Suspect",
    ]
    empty_columns = (
        ["Mail_ID"]
        + [c + "_Sum" for c in feature_cols]
        + [c + "_Mean" for c in feature_cols]
        + ["Attachments_Count"]
    )

    if attachments_features_df.empty:
        return pd.DataFrame(columns=empty_columns)

    features_only = attachments_features_df.drop(columns=["Mail_ID"])

    df_sum = (
        features_only.groupby(attachments_features_df["Mail_ID"])
        .sum()
        .drop(columns="ID", errors="ignore")
    )
    df_mean = (
        features_only.groupby(attachments_features_df["Mail_ID"])
        .mean()
        .drop(columns="ID", errors="ignore")
    )

    df_sum.columns = [col + "_Sum" for col in df_sum.columns]
    df_mean.columns = [col + "_Mean" for col in df_mean.columns]

    df = pd.concat([df_sum, df_mean], axis=1)
    df["Attachments_Count"] = attachments_features_df.groupby("Mail_ID").size()

    return df.reset_index()


def inject_final_datas():
    mails_features_df, links_features_df, attachments_features_df = (
        load_features_dataframes()
    )
    logger.info(f"Features loaded — {len(mails_features_df)} mails to normalize")

    final_mails_datas = create_final_mails_datas(mails_features_df)
    final_links_datas = create_final_links_data(links_features_df)
    final_attachments_datas = create_final_attachments_data(attachments_features_df)

    final = final_mails_datas.merge(
        final_links_datas, how="left", left_on="ID", right_on="Mail_ID"
    ).drop(columns="Mail_ID")
    final = final.merge(
        final_attachments_datas, how="left", left_on="ID", right_on="Mail_ID"
    ).drop(columns="Mail_ID")
    final = final.fillna(0)

    cols_sorted = [  # Made this because the columns were really disordered, with label in middle columns,
        # links count and attachments counts on middle too so it was tedious to browse in the db.
        "ID",
        "Links_Count",
        "Attachments_Count",
        "Is_Date_Coherent",
        "Is_Time_Coherent",
        "Is_Mail_Extension_Suspect",
        "Is_Reply_To_Suspect",
        "Is_SPF_Result_Unapplicable",
        "Is_SPF_Result_Suspect",
        "Is_DKIM_Result_Unapplicable",
        "Is_DKIM_Result_Suspect",
        "Count_Spam_Words_In_Mail",
        "Ratio_Spam_Words_In_Mail",
        "Number_Of_Words_Content",
        "Is_XMailer_Result_Unapplicable",
        "Is_XMailer_Result_Suspect",
        "Is_Display_Name_Suspect",
        "Is_Link_Domain_Age_Unusable_Sum",
        "Is_Link_Domain_Age_Unusable_Mean",
        "Is_Link_Domain_Age_Suspect_Sum",
        "Is_Link_Domain_Age_Suspect_Mean",
        "Is_Redirect_Link_Unusable_Sum",
        "Is_Redirect_Link_Unusable_Mean",
        "Is_Redirect_Link_Suspect_Sum",
        "Is_Redirect_Link_Suspect_Mean",
        "Is_Link_HTTP_Sum",
        "Is_Link_HTTP_Mean",
        "Is_Link_An_IPAdress_Sum",
        "Is_Link_An_IPAdress_Mean",
        "Is_Domain_Name_Suspect_Sum",
        "Is_Domain_Name_Suspect_Mean",
        "Is_Site_Extension_Suspect_Sum",
        "Is_Site_Extension_Suspect_Mean",
        "Is_Attachment_Executable_Sum",
        "Is_Attachment_Executable_Mean",
        "Is_Double_Extension_Sum",
        "Is_Double_Extension_Mean",
        "Is_No_Extension_Sum",
        "Is_No_Extension_Mean",
        "Is_Extension_Suspect_Sum",
        "Is_Extension_Suspect_Mean",
        "Is_File_Empty_Sum",
        "Is_File_Empty_Mean",
        "Is_File_Size_Suspect_Sum",
        "Is_File_Size_Suspect_Mean",
        "Is_Magic_Number_Suspect_Sum",
        "Is_Magic_Number_Suspect_Mean",
        "Label",
    ]

    final = final[cols_sorted]

    logger.info(f"Final table built — {len(final)} rows x {len(final.columns)} columns")

    with sqlite3.connect(DATABASE_FINAL_PATH) as conn:
        final_mails_datas.to_sql(
            "Mails_Features_Normalized", conn, if_exists="replace", index=False
        )
        logger.info("✓ Mails_Features_Normalized injected")

        final_links_datas.to_sql(
            "Links_Features_Normalized", conn, if_exists="replace", index=False
        )
        logger.info("✓ Links_Features_Normalized injected")

        final_attachments_datas.to_sql(
            "Attachments_Features_Normalized", conn, if_exists="replace", index=False
        )
        logger.info("✓ Attachments_Features_Normalized injected")

        final.to_sql("Features_Normalized", conn, if_exists="replace", index=False)
        logger.info(f"✓ Features_Normalized injected — pipeline complete")
