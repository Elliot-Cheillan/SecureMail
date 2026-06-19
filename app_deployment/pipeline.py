import sys
import pandas as pd
import shap
import asyncio
import aiohttp
import asyncwhois
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

from model import load_model, _predict, run_explanation


async def _enrich_links_async(link_data):
    if not link_data:
        return link_data

    client = asyncwhois.DomainClient()
    domain_cache = {}
    rdap_semaphore = asyncio.Semaphore(5)
    http_semaphore = asyncio.Semaphore(5)

    async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
        rdap_tasks = [
            get_creation_date(client, link["domain"], domain_cache, rdap_semaphore)
            for link in link_data
        ]
        redirect_tasks = [
            get_redirect_url(session, link["url"], http_semaphore) for link in link_data
        ]
        creation_dates, redirects = await asyncio.gather(
            asyncio.gather(*rdap_tasks),
            asyncio.gather(*redirect_tasks),
        )

    for link, creation, redirect in zip(link_data, creation_dates, redirects):
        link["domain_creation_date"] = creation
        link["redirect_url"] = redirect

    return link_data


def get_raw_infos(file_uploaded_bytes):
    # Take the bytes of a file so don't forget to take all the file bytes before using this
    msg, mail_data, content = parse_email_file(file_bytes=file_uploaded_bytes)
    link_data = parse_links(msg, mail_data["date"])
    attachment_data = parse_attachments(msg)

    link_data = asyncio.run(_enrich_links_async(link_data))

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
    links_columns = [
        "ID",
        "Mail_Number",
        "URL",
        "Domain",
        "Mail_Date",
        "Domain_Creation_Date",
        "Redirect_URL",
    ]
    links_df = pd.DataFrame(links_datas, columns=links_columns)
    attachments_columns = [
        "ID",
        "Mail_Number",
        "Filename",
        "Extension",
        "File_Size_Bytes",
        "File_Hash",
        "Magic_Number",
    ]
    attachments_df = pd.DataFrame(attachments_datas, columns=attachments_columns)

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

    cols_sorted = [
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
    return final


def model_and_explanation(final_df):

    df = pd.DataFrame()

    model, scaler = load_model()
    predictions, probabilities = _predict(model, scaler, final_df)
    explanation = run_explanation(model, scaler, final_df)

    df["Prediction"] = predictions
    df["Spam_Probability"] = probabilities
    df["Result"] = df["Prediction"].map({1.0: "SPAM", 0.0: "HAM"})

    result = df["Result"][0]

    confidence = round(abs(0.5 - float(probabilities[0])) * 2, 4)

    if confidence < 0.20:
        confidence_level = "Undecided"
    elif confidence < 0.40:
        confidence_level = "Unsure"
    elif confidence < 0.60:
        confidence_level = "Moderate"
    elif confidence < 0.80:
        confidence_level = "High"
    elif confidence < 0.90:
        confidence_level = "Very High"
    else:
        confidence_level = "Extremely High"

    results = {
        "predictions": predictions,
        "probabilities": probabilities,
        "result": result,
        "confidence": confidence,
        "confidence_level": confidence_level,
    }

    return results, explanation


def full_pipeline(file_bytes, filename):
    # The full pipeline is the operations before the explaining part
    json_mail_infos, content = get_raw_infos(file_bytes)
    mail_df, links_df, attachments_df = normalize_mail_json(
        json_mail_infos, content, filename
    )
    final_df = final_df = create_features_jsons(mail_df, links_df, attachments_df)
    print(final_df.to_string())

    results, explanation = model_and_explanation(final_df)

    return json_mail_infos, final_df, results, explanation, content
