import sys
import os
import pandas as pd

sys.path.append("..")

from ingestion.services import (
    parse_email_file,
    parse_attachments,
    parse_links,
    get_redirect_url,
    get_creation_date,
)

from feature_engineering.etl import (
    build_mails_features,
    build_links_features,
    build_attachments_features,
    create_final_attachments_data,
    create_final_links_data,
    create_final_mails_datas,
)


def get_raw_infos(file_uploaded_bytes):
    # Take the bytes of a file so don't forget to take all the file bytes before using this

    msg, mail_data, content = parse_email_file(file_bytes=file_uploaded_bytes)
    link_data = parse_links(msg, mail_data)
    attachment_data = parse_attachments(msg)

    for link in link_data:
        link["domain_creation_date"] = get_creation_date(
            link["domain"], link["mail_date"]
        )
        link["redirect_url"] = get_redirect_url(link["url"])

    json_mail_infos = {
        "mail_data": mail_data,
        "links_data": link_data,
        "attachments_data": attachment_data,
    }

    return json_mail_infos, content


def normalize_mail_json(mail_json, content, filename):
    mail_datas = {
        "ID": 1,
        "Sender_Display_Name": mail_json["mail_data"]["sender_display"],
        "Sender_Email": mail_json["mail_data"]["sender_email"],
        "Reply_To_Email": mail_json["mail_data"]["reply_to_email"],
        "Date": mail_json["mail_data"]["date"],
        "Time": mail_json["mail_data"]["time"],
        "Subject": mail_json["mail_data"]["subject"],
        "X_Mailer": mail_json["mail_data"]["x_mailer"],
        "SPF_Result": mail_json["mail_data"]["spf_result"],
        "DKIM_Result": mail_json["mail_data"]["dkim_result"],
        "Content": content,
        "Filename": filename,
        "Label": None,
    }

    links_datas = []
    attachments_datas = []

    count = 0

    for link in mail_json["links_data"]:
        links_datas.append(
            {
                "ID": count,
                "Mail_Number": 1,
                "URL": link["url"],
                "Domain": link["domain"],
                "Mail_Date": link["mail_date"],
                "Domain_Creation_Date": link["domain_creation_date"],
                "Redirect_URL": link["redirect_url"],
            }
        )
        count += 1

    count = 0
    for attachment in mail_json["attachments_data"]:
        attachments_datas.append(
            {
                "ID": count,
                "Mail_Number": 1,
                "Filename": attachment["filename"],
                "Extension": attachment["extension"],
                "File_Size_Bytes": attachment["file_size"],
                "File_Hash": attachment["file_hash"],
                "Magic_Number": attachment["magic_number"],
            }
        )
        count += 1

    # Normalize the name of the attributes in json, so we can use the function in load.py with the good column names

    mail_df = pd.DataFrame([mail_datas])
    links_df = pd.DataFrame(links_datas)
    attachments_df = pd.DataFrame(attachments_datas)

    return mail_df, links_df, attachments_df


def create_features_jsons(mail_df, links_df, attachments_df):
    mail_feature_df = build_mails_features(mail_df)
    links_feature_df = build_links_features(links_df)
    attachments_feature_df = build_attachments_features(attachments_df)

    final_mails_datas = create_final_mails_datas(mail_feature_df)
    final_links_datas = create_final_links_data(links_feature_df)
    final_attachments_datas = create_final_attachments_data(attachments_feature_df)

    final = final_mails_datas.merge(
        final_links_datas, how="left", left_on="ID", right_on="Mail_ID"
    ).drop(columns="Mail_ID")
    final = final.merge(
        final_attachments_datas, how="left", left_on="ID", right_on="Mail_ID"
    ).drop(columns="Mail_ID")
    final = final.fillna(0)

    return final
