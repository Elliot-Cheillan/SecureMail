import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from feature_engineering.featuring import spamwords_set


FEATURE_LABELS_SPAM = {
    "Links_Count": "High number of links",
    "Attachments_Count": "High number of attachments",
    "Is_Date_Coherent": "Incoherent date",
    "Is_Time_Coherent": "Suspicious send time",
    "Is_Mail_Extension_Suspect": "Suspicious sender domain",
    "Is_Reply_To_Suspect": "Suspicious Reply-To address",
    "Is_SPF_Result_Unapplicable": "SPF check unavailable",
    "Is_SPF_Result_Suspect": "SPF check failed",
    "Is_DKIM_Result_Unapplicable": "DKIM check unavailable",
    "Is_DKIM_Result_Suspect": "DKIM check failed",
    "Count_Spam_Words_In_Mail": "High spam word count",
    "Ratio_Spam_Words_In_Mail": "High spam word ratio",
    "Number_Of_Words_Content": "Unusual word count",
    "Is_XMailer_Result_Unapplicable": "Mail client info missing",
    "Is_XMailer_Result_Suspect": "Suspicious mail client",
    "Is_Display_Name_Suspect": "Suspicious sender display name",
    "Is_Link_Domain_Age_Unusable_Sum": "Unverifiable link domains (total)",
    "Is_Link_Domain_Age_Unusable_Mean": "Unverifiable link domains (ratio)",
    "Is_Link_Domain_Age_Suspect_Sum": "Recently created link domains (total)",
    "Is_Link_Domain_Age_Suspect_Mean": "Recently created link domains (ratio)",
    "Is_Redirect_Link_Unusable_Sum": "Unresolvable redirects (total)",
    "Is_Redirect_Link_Unusable_Mean": "Unresolvable redirects (ratio)",
    "Is_Redirect_Link_Suspect_Sum": "Suspicious redirects (total)",
    "Is_Redirect_Link_Suspect_Mean": "Suspicious redirects (ratio)",
    "Is_Link_HTTP_Sum": "Insecure HTTP links (total)",
    "Is_Link_HTTP_Mean": "Insecure HTTP links (ratio)",
    "Is_Link_An_IPAdress_Sum": "Links to raw IPs (total)",
    "Is_Link_An_IPAdress_Mean": "Links to raw IPs (ratio)",
    "Is_Domain_Name_Suspect_Sum": "Suspicious domain names (total)",
    "Is_Domain_Name_Suspect_Mean": "Suspicious domain names (ratio)",
    "Is_Site_Extension_Suspect_Sum": "Suspicious site extensions (total)",
    "Is_Site_Extension_Suspect_Mean": "Suspicious site extensions (ratio)",
    "Is_Attachment_Executable_Sum": "Executable attachments (total)",
    "Is_Attachment_Executable_Mean": "Executable attachments (ratio)",
    "Is_Double_Extension_Sum": "Double extension attachments (total)",
    "Is_Double_Extension_Mean": "Double extension attachments (ratio)",
    "Is_No_Extension_Sum": "Attachments without extension (total)",
    "Is_No_Extension_Mean": "Attachments without extension (ratio)",
    "Is_Extension_Suspect_Sum": "Suspicious attachment extensions (total)",
    "Is_Extension_Suspect_Mean": "Suspicious attachment extensions (ratio)",
    "Is_File_Empty_Sum": "Empty attachments (total)",
    "Is_File_Empty_Mean": "Empty attachments (ratio)",
    "Is_File_Size_Suspect_Sum": "Suspicious file sizes (total)",
    "Is_File_Size_Suspect_Mean": "Suspicious file sizes (ratio)",
    "Is_Magic_Number_Suspect_Sum": "Mismatched file signatures (total)",
    "Is_Magic_Number_Suspect_Mean": "Mismatched file signatures (ratio)",
}

FEATURE_LABELS_HAM = {
    "Links_Count": "Normal number of links",
    "Attachments_Count": "Normal number of attachments",
    "Is_Date_Coherent": "Coherent date",
    "Is_Time_Coherent": "Normal send time",
    "Is_Mail_Extension_Suspect": "Legitimate sender domain",
    "Is_Reply_To_Suspect": "Consistent Reply-To address",
    "Is_SPF_Result_Unapplicable": "SPF not applicable (old mail)",
    "Is_SPF_Result_Suspect": "SPF check passed",
    "Is_DKIM_Result_Unapplicable": "DKIM not applicable (old mail)",
    "Is_DKIM_Result_Suspect": "DKIM check passed",
    "Count_Spam_Words_In_Mail": "Low spam word count",
    "Ratio_Spam_Words_In_Mail": "Low spam word ratio",
    "Number_Of_Words_Content": "Normal word count",
    "Is_XMailer_Result_Unapplicable": "Mail client info present",
    "Is_XMailer_Result_Suspect": "Legitimate mail client",
    "Is_Display_Name_Suspect": "Legitimate sender display name",
    "Is_Link_Domain_Age_Unusable_Sum": "Link domains verifiable (total)",
    "Is_Link_Domain_Age_Unusable_Mean": "Link domains verifiable (ratio)",
    "Is_Link_Domain_Age_Suspect_Sum": "Established link domains (total)",
    "Is_Link_Domain_Age_Suspect_Mean": "Established link domains (ratio)",
    "Is_Redirect_Link_Unusable_Sum": "Redirects resolvable (total)",
    "Is_Redirect_Link_Unusable_Mean": "Redirects resolvable (ratio)",
    "Is_Redirect_Link_Suspect_Sum": "Clean redirects (total)",
    "Is_Redirect_Link_Suspect_Mean": "Clean redirects (ratio)",
    "Is_Link_HTTP_Sum": "Secure HTTPS links (total)",
    "Is_Link_HTTP_Mean": "Secure HTTPS links (ratio)",
    "Is_Link_An_IPAdress_Sum": "No raw IP links (total)",
    "Is_Link_An_IPAdress_Mean": "No raw IP links (ratio)",
    "Is_Domain_Name_Suspect_Sum": "Legitimate domain names (total)",
    "Is_Domain_Name_Suspect_Mean": "Legitimate domain names (ratio)",
    "Is_Site_Extension_Suspect_Sum": "Normal site extensions (total)",
    "Is_Site_Extension_Suspect_Mean": "Normal site extensions (ratio)",
    "Is_Attachment_Executable_Sum": "No executable attachments (total)",
    "Is_Attachment_Executable_Mean": "No executable attachments (ratio)",
    "Is_Double_Extension_Sum": "No double extension attachments (total)",
    "Is_Double_Extension_Mean": "No double extension attachments (ratio)",
    "Is_No_Extension_Sum": "All attachments have extensions (total)",
    "Is_No_Extension_Mean": "All attachments have extensions (ratio)",
    "Is_Extension_Suspect_Sum": "Normal attachment extensions (total)",
    "Is_Extension_Suspect_Mean": "Normal attachment extensions (ratio)",
    "Is_File_Empty_Sum": "No empty attachments (total)",
    "Is_File_Empty_Mean": "No empty attachments (ratio)",
    "Is_File_Size_Suspect_Sum": "Normal file sizes (total)",
    "Is_File_Size_Suspect_Mean": "Normal file sizes (ratio)",
    "Is_Magic_Number_Suspect_Sum": "Valid file signatures (total)",
    "Is_Magic_Number_Suspect_Mean": "Valid file signatures (ratio)",
}

# Report of the the mail received


def top_10_indicators(shap_dict, result):
    shap_tuple = list(shap_dict.items())
    labels = FEATURE_LABELS_SPAM if result == "SPAM" else FEATURE_LABELS_HAM

    if result == "SPAM":
        relevant = [(k, v) for k, v in shap_tuple if v > 0]
        relevant_sorted = sorted(relevant, key=lambda x: x[1], reverse=True)
    else:
        relevant = [(k, v) for k, v in shap_tuple if v < 0]
        relevant_sorted = sorted(relevant, key=lambda x: x[1])

    if not relevant_sorted:
        relevant_sorted = sorted(shap_tuple, key=lambda x: abs(x[1]), reverse=True)

    top10 = relevant_sorted[:10]
    return {labels.get(k, k): v for k, v in top10}


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
