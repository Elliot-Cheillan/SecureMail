import sys

sys.path.append("..")
from feature_engineering.featuring import spamwords_set


FEATURE_LABELS = {
    "Links_Count": "Number of links in the mail",
    "Attachments_Count": "Number of attachments",
    "Is_Date_Coherent": "Date consistency",
    "Is_Time_Coherent": "Time consistency",
    "Is_Mail_Extension_Suspect": "Suspicious sender domain extension",
    "Is_Reply_To_Suspect": "Suspicious Reply-To address",
    "Is_SPF_Result_Unapplicable": "SPF check unavailable",
    "Is_SPF_Result_Suspect": "SPF check failed",
    "Is_DKIM_Result_Unapplicable": "DKIM check unavailable",
    "Is_DKIM_Result_Suspect": "DKIM check failed",
    "Count_Spam_Words_In_Mail": "Number of spam words detected",
    "Ratio_Spam_Words_In_Mail": "Ratio of spam words in content",
    "Number_Of_Words_Content": "Total word count",
    "Is_XMailer_Result_Unapplicable": "Mail client info unavailable",
    "Is_XMailer_Result_Suspect": "Suspicious mail client",
    "Is_Display_Name_Suspect": "Suspicious sender display name",
    "Is_Link_Domain_Age_Unusable_Sum": "Unverifiable link domain ages (total)",
    "Is_Link_Domain_Age_Unusable_Mean": "Unverifiable link domain ages (ratio)",
    "Is_Link_Domain_Age_Suspect_Sum": "Recently created link domains (total)",
    "Is_Link_Domain_Age_Suspect_Mean": "Recently created link domains (ratio)",
    "Is_Redirect_Link_Unusable_Sum": "Unresolvable redirects (total)",
    "Is_Redirect_Link_Unusable_Mean": "Unresolvable redirects (ratio)",
    "Is_Redirect_Link_Suspect_Sum": "Suspicious redirects detected (total)",
    "Is_Redirect_Link_Suspect_Mean": "Suspicious redirects detected (ratio)",
    "Is_Link_HTTP_Sum": "Insecure HTTP links (total)",
    "Is_Link_HTTP_Mean": "Insecure HTTP links (ratio)",
    "Is_Link_An_IPAdress_Sum": "Links pointing to raw IPs (total)",
    "Is_Link_An_IPAdress_Mean": "Links pointing to raw IPs (ratio)",
    "Is_Domain_Name_Suspect_Sum": "Suspicious domain names (total)",
    "Is_Domain_Name_Suspect_Mean": "Suspicious domain names (ratio)",
    "Is_Site_Extension_Suspect_Sum": "Suspicious site extensions (total)",
    "Is_Site_Extension_Suspect_Mean": "Suspicious site extensions (ratio)",
    "Is_Attachment_Executable_Sum": "Executable attachments (total)",
    "Is_Attachment_Executable_Mean": "Executable attachments (ratio)",
    "Is_Double_Extension_Sum": "Double extension attachments (total)",
    "Is_Double_Extension_Mean": "Double extension attachments (ratio)",
    "Is_No_Extension_Sum": "Attachments with no extension (total)",
    "Is_No_Extension_Mean": "Attachments with no extension (ratio)",
    "Is_Extension_Suspect_Sum": "Suspicious attachment extensions (total)",
    "Is_Extension_Suspect_Mean": "Suspicious attachment extensions (ratio)",
    "Is_File_Empty_Sum": "Empty attachments (total)",
    "Is_File_Empty_Mean": "Empty attachments (ratio)",
    "Is_File_Size_Suspect_Sum": "Suspicious file sizes (total)",
    "Is_File_Size_Suspect_Mean": "Suspicious file sizes (ratio)",
    "Is_Magic_Number_Suspect_Sum": "Corrupted or mismatched file signatures (total)",
    "Is_Magic_Number_Suspect_Mean": "Corrupted or mismatched file signatures (ratio)",
}


# Report of the the mail received


def top_10_indicators(shap_dict, result):
    shap_tuple = list(shap_dict.items())

    if result == "SPAM":
        relevant = [(k, v) for k, v in shap_tuple if v > 0]
        relevant_sorted = sorted(relevant, key=lambda x: x[1], reverse=True)
    else:
        relevant = [(k, v) for k, v in shap_tuple if v < 0]
        relevant_sorted = sorted(relevant, key=lambda x: x[1])
    if not relevant_sorted:
        relevant_sorted = sorted(shap_tuple, key=lambda x: abs(x[1]), reverse=True)

    top10 = relevant_sorted[:10]
    return {FEATURE_LABELS.get(k, k): v for k, v in top10}


def spamwords_detection(content):
    spamwords_detected = {}
    word_list = content.strip().split()
    for i in range(len(word_list)):
        if word_list[i].lower().strip(".,!?;:") in spamwords_set:
            spamwords_detected[i] = word_list[i]
        # Could use jaro winckler or levenshtein but I think with them we can have some normal words that will be detected like agent is near than argent
        # so I decided to detect exacts words and not similar.
    return spamwords_detected


def full_report(shap_dict, content, results, json_mail_infos):
    report = {}
    report["result"] = results["result"]
    report["confidence"] = results["confidence"]
    report["confidence_level"] = results["confidence_level"]

    report["top_5_indicators"] = top_10_indicators(shap_dict, report["result"])
    report["spamwords"] = spamwords_detection(content)

    # mails base infos
    report["sender"] = json_mail_infos["mail_data"]["sender_email"]
    report["sender_display"] = json_mail_infos["mail_data"]["sender_display"]
    report["subject"] = json_mail_infos["mail_data"]["subject"]
    report["spf"] = json_mail_infos["mail_data"]["spf_result"]
    report["dkim"] = json_mail_infos["mail_data"]["dkim_result"]

    report["links"] = [
        {"url": l["url"], "domain": l["domain"], "redirect": l["redirect_url"]}
        for l in json_mail_infos["links_data"]
    ]

    report["attachments"] = [
        {"filename": a["filename"], "extension": a["extension"]}
        for a in json_mail_infos["attachments_data"]
    ]

    report["content"] = content

    return report
