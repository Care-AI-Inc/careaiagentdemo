import json
import os
from typing import Optional

from openai import OpenAI

from beans import MedicalReport

OPEN_API_KEY = os.getenv("OPEN_API_KEY")
client = OpenAI(api_key=OPEN_API_KEY)

EXTRACT_EMAIL_PROMPT = """
Process the document and identify it is medical report document and if not return bottom JSON with  is_document_medical_report as false and don't process remaining information.
From given document, extract the doctor name to whom the document is addressed to or who requested the report (first name and last name) and patients name (first name, last name). Also summarize the document, if the report has any significant/critical findings mention it as first thing in the summary then include recommendations based on the same. 
You need to out the following json. No other output other than below json permitted.
Note: Report is prepared and sent by another doctor and their name would also be mentioned in report, ignore that and use name of the requested doctor or to whom the report is addressed to.
{{
  "is_document_medical_report": true/false // this represents if document is medical report or not, 
  "doctor_first_name": "" // doctors first name i.e who requested the report or to whom the report is address to,
  "report_date": "", // date when report was sent in MMM DD YYYY format ex: Aug 11th 2024,
  report_type": "", // type of report i.e blood work, mri, ct scan, xray etc. if not able to find then mention unknown
 "doctor_last_name": "" // doctors last name,
  "patient_first_name": "" // doctors first name,
 "patient_last_name": "" // doctors second name,
 "critical_findings": "" // Medium to Critical findings from report if any, else mention no critical findings,
 "recommendations": // Recommendations or next steps if any
"summary" : "" // summary of the document , 
"email_subject": "" // provide suitable subject based on summary (include patient name, report type and date (in MMM DD YYYY format ex: Aug 11th 2024)
}}
Document is {medical_report_data}
"""

MATCH_NAME_PROMPT = """
find correct matching for name "{first_name} {last_name}" from following list and return the ID of the person. If multiple such names found return it as list. 
Some time first name or last name can be provided as initials as well so consider that well.
```
{data}
```
You answer be only in json format as mentioned below.
```
{{
"name_ids": [] // list of matching name ID's goes here
}}
```
"""

def _trim_json_markdown(json_str):
    # Check if the string starts with '```json' and ends with '```'
    if json_str.startswith('```json') and json_str.endswith('```'):
        # Remove the markdown markers and any surrounding whitespace
        return json_str[7:-3].strip()
    # Return the original string if no markdown markers are found
    return json_str

def extract_and_summarize_medical_report(medical_report_data: str) -> Optional[MedicalReport]:
    """
    Extracts medical report from given medical report data.
    :param medical_report_data:
    :return:
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": EXTRACT_EMAIL_PROMPT.format(medical_report_data=medical_report_data)},
        ])
    if response.choices:
        message = json.loads(_trim_json_markdown(response.choices[0].message.content))
        return MedicalReport(**message)
    return None

def normalize_and_find_matching_name_ids(name_with_id_data: dict, first_name: str, last_name: str) -> list[str]:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": MATCH_NAME_PROMPT.format(data=json.dumps(name_with_id_data), first_name=first_name, last_name=last_name)},
        ])
    if response.choices:
        message = json.loads(_trim_json_markdown(response.choices[0].message.content))
        return message["name_ids"]
    return []
