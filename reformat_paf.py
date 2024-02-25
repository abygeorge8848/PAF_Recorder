from name_generator import NameGenerator
import os
import json
from datetime import datetime
#from gpt import generate_pass_message, generate_fail_message


def reformat_paf_activity(event_queue, activity_name, activity_description):
    PAF_SCRIPT = ""
    VALIDATION_SCRIPT = "\n"
    name_engine = NameGenerator()

    for event in event_queue:
        if event["event"] == "WaitForPageLoad":
            PAF_SCRIPT += '\t<WaitForPageLoad desc="Implementation step" expResult="NA"/>\n'
        elif event["event"] == "end-loop":
            PAF_SCRIPT += "\t</loop>\n"
        elif event["event"] == "alert-accept":
            PAF_SCRIPT += '\t<alert type="accept" desc="Implementation step" expResult="NA"></alert>\n'
        elif event["event"] == "alert-cancel":
            PAF_SCRIPT += '\t<alert type="cancel" desc="Implementation step" expResult="NA"></alert>\n'
        elif event["event"] == "alert-getText":
            keyName = event["keyName"]
            PAF_SCRIPT += f'\t<alert type="getText" keyName="{keyName}" desc="Implementation step" expResult="NA"></alert>\n'
        elif event["event"] == "alert-input":
            value = event["value"]
            PAF_SCRIPT += f'\t<alert type="getText" value="{value}" desc="Implementation step" expResult="NA"></alert>\n'
        elif event["event"] == "alert-authenticate":
            user = event["user"]
            pwd = event["pwd"]
            PAF_SCRIPT += f'\t<alert type="getText" user="{user}" pwd="{pwd}" desc="Implementation step" expResult="NA"></alert>\n'
        elif event["event"] == "custom-step":
            custom_step = event["custom_step"]
            PAF_SCRIPT += f'\t{custom_step}\n'
        elif event["event"] == "refresh-browser":
            PAF_SCRIPT += '\t<BrowserRefresh></BrowserRefresh>\n'
        elif event["event"] == "close-browser":
            PAF_SCRIPT += '\t<closeBrowser></closeBrowser>\n'
        elif event["event"] == "redirect-url":
            url = event["url"]
            PAF_SCRIPT += f'\t<redirect url="{url}" desc="Implementation step" expResult="NA"></redirect>\n'
        elif event["event"] == "start-loop":
            startIndex = event["startIndex"]
            lastIndex = event["lastIndex"]
            increment = event["increment"]
            counterVar = event["counterVar"]
            PAF_SCRIPT += f'\t<loop startIndex="{startIndex}" lastIndex="{lastIndex}" increment="{increment}" counterVar="{counterVar}" desc="Implementation step" expResult="NA">\n'
        elif event["event"] == "end-if":
            PAF_SCRIPT += "\t</if>\n"
        elif event["event"] == "end-if-then":
            PAF_SCRIPT += "\t\t</then>\n"
            PAF_SCRIPT += "\t\t<else>\n"
        elif event["event"] == "end-else":
            PAF_SCRIPT += "\t\t</else>\n"
            PAF_SCRIPT += "\t</if>\n"
        elif event["event"] == "click":
            xpath = event["xpath"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click" desc="Implementation step" expResult="NA"></WaitTillElement>\n'
            #PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<script xpath="{xpath}" clickElement="true" desc="Implementation step" expResult="NA"></script>\n'
        elif event["event"] == "hover":
            xpath = event["xpath"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click" desc="Implementation step" expResult="NA"></WaitTillElement>\n'
            PAF_SCRIPT += f'\t<hover xpath="{xpath}" desc="Implementation step" expResult="NA"></hover>\n'
        elif event["event"] == "DragandDrop":
            src = event["src"]
            target = event["target"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click" desc="Implementation step" expResult="NA"></WaitTillElement>\n'
            PAF_SCRIPT += f'\t<DragandDrop src="{src}" target="{target}" desc="Implementation step" expResult="NA"></DragandDrop>\n'
        elif event["event"] == "clearinput":
            xpath = event["xpath"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click" desc="Implementation step" expResult="NA"></WaitTillElement>\n'
            PAF_SCRIPT += f'\t<ClearInput xpath="{xpath}" desc="Implementation step" expResult="NA"></ClearInput>\n'
        elif event["event"] == "highlight":
            xpath = event["xpath"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click" desc="Implementation step" expResult="NA"></WaitTillElement>\n'
            PAF_SCRIPT += f'\t<highlight xpath="{xpath}" desc="Implementation step" expResult="NA"></highlight>\n'
        elif event["event"] == "excel-write":
            value = event["value"]
            row = event["row"]
            col = event["col"]
            sheetName = event["sheet"]
            excelPath = event["path"]
            saveAs = event["savePath"]
            if len(saveAs):
                PAF_SCRIPT += f'<excel saveAs="{saveAs}" row="{row}" col="{col}" sheetName="{sheetName}" excelPath="{excelPath}" value="{value}" desc="Implementation step" expResult="NA"></excel>\n'
            else:
                PAF_SCRIPT += f'<excel save="true" row="{row}" col="{col}" sheetName="{sheetName}" excelPath="{excelPath}" value="{value}" desc="Implementation step" expResult="NA"></excel>\n'
        elif event["event"] == "excel-read":
            variable = event["variable"]
            row = event["row"]
            col = event["col"]
            sheetName = event["sheet"]
            excelPath = event["path"]
            PAF_SCRIPT += f'<excel row="{row}" col="{col}" sheetName="{sheetName}" excelPath="{excelPath}" variable="{variable}" desc="Implementation step" expResult="NA"></excel>\n'
        elif event["event"] == "excel-search":
            text = event["text"]
            variable = event["variable"]
            row = event["row"]
            col = event["col"]
            sheetName = event["sheet"]
            excelPath = event["path"]
            PAF_SCRIPT += f'<ExcelSearch row="{row}" col="{col}" sheetName="{sheetName}" excelPath="{excelPath}" variable="{variable}" text="{text}" desc="Implementation step" expResult="NA"></ExcelSearch>\n'
        elif event["event"] == "frame":
            id = event["id"]
            PAF_SCRIPT += f'\t<wait time="5000" desc="Implementation step" expResult="NA"></wait>\n'
            PAF_SCRIPT += f'\t<frame id="{id}" desc="Implementation step" expResult="NA"></frame>\n'
        elif event["event"] == "input":
            xpath = event["xpath"]
            value = event["value"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click" desc="Implementation step" expResult="NA"></WaitTillElement>\n'
            #PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<input xpath="{xpath}" value="{value}" desc="Implementation step" expResult="NA"></input>\n'
        elif event["event"] == "specialKeys":
            xpath = event["xpath"]
            value = event["value"]
            value = value.lower()
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click" desc="Implementation step" expResult="NA"></WaitTillElement>\n'
            #PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<specialKeys xpath="{xpath}" specialChar="{{{value}}}" desc="Implementation step" expResult="NA"></specialKeys>\n'
        elif event["event"] == "dblClick":
            xpath = event["xpath"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="click" desc="Implementation step" expResult="NA"></WaitTillElement>\n'
            #PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<dblClick xpath="{xpath}" desc="Implementation step" expResult="NA"></dblClick>\n'
        elif event["event"] == "scroll":
            xpath = event["xpath"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="visible" desc="Implementation step" expResult="NA"></WaitTillElement>\n'
            #PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            PAF_SCRIPT += f'\t<scroll xpath="{xpath}" desc="Implementation step" expResult="NA"></scroll>\n'
        elif event["event"] == "dropdown":
            xpath = event["xpath"]
            selected = event["selected"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="visible" desc="Implementation step" expResult="NA"></WaitTillElement>\n'
            PAF_SCRIPT += f'\t<dropdown xpath="{xpath}" selected="{selected}" desc="Implementation step" expResult="NA"></dropdown>\n'
        elif event["event"] == "getText":
            #getText_variable = name_engine.get_variable_name()
            xpath = event["xpath"]
            variable = event["variable"]
            after = event["after"]
            before = event["before"]
            PAF_SCRIPT += f'\t<WaitTillElement xpath="{xpath}" waitcondition="visible" desc="Implementation step" expResult="NA"></WaitTillElement>\n'
            #PAF_SCRIPT += '\t<wait time="3000"></wait>\n'
            if not after and not before:
                PAF_SCRIPT += f'\t<getText xpath="{xpath}" variable="{variable}" desc="Implementation step" expResult="NA"></getText>\n'
            elif after and not before:
                PAF_SCRIPT += f'\t<getText xpath="{xpath}" variable="{variable}" snapshotAfter="true" desc="Implementation step" expResult="NA"></getText>\n'
            elif not after and before:
                PAF_SCRIPT += f'\t<getText xpath="{xpath}" variable="{variable}" snapshotBefore="true" desc="Implementation step" expResult="NA"></getText>\n'
            else:
               PAF_SCRIPT += f'\t<getText xpath="{xpath}" variable="{variable}" snapshotAfter="true" snapshotBefore="true" desc="Implementation step" expResult="NA"></getText>\n' 
        elif event["event"] == "variable-value":
            variable_name = event["name"]
            variable_value = event["value"]
            after = event["after"]
            before = event["before"]
            if not after and not before:
                PAF_SCRIPT += f'\t<variable keyName="{variable_name}" value="{variable_value}" desc="Implementation step" expResult="NA"></variable>\n'
            elif after and not before:
                PAF_SCRIPT += f'\t<variable keyName="{variable_name}" value="{variable_value}" snapshotAfter="true" desc="Implementation step" expResult="NA"></variable>\n'
            elif not after and before:
                PAF_SCRIPT += f'\t<variable keyName="{variable_name}" value="{variable_value}" snapshotBefore="true" desc="Implementation step" expResult="NA"></variable>\n'
            else:
               PAF_SCRIPT += f'\t<variable keyName="{variable_name}" value="{variable_value}" snapshotAfter="true" snapshotBefore="true" desc="Implementation step" expResult="NA"></variable>\n'
        elif event["event"] in ["validation-exists", "validation-not-exists"]:
            if event["validation_name"] == "Enter validation name(optional)":
                event["validation_name"] = name_engine.get_validation_name()
            if event["pass_msg"] == "Enter pass message(optional)":
                event["pass_msg"] = "STEP PASSED"
            if event["fail_msg"] == "Enter fail message(optional)":
                event["fail_msg"] = "STEP FAILED"  
            validation_name = event["validation_name"]
            xpath = event["xpath"]
            after = event["after"]
            before = event["before"]
            passMsg = event["pass_msg"]
            failMsg = event["fail_msg"]
            if_condition = event["if_condition"]
            if_else_condition = event["if_else_condition"]
            #PAF_SCRIPT += '\t<wait time="5000"></wait>\n'
            if not if_condition and not if_else_condition:
                PAF_SCRIPT += f'\t<validation valGroupIds="{validation_name}" desc="Implementation step" expResult="NA"></validation>\n'
            elif if_else_condition:
                PAF_SCRIPT += f'\t<if valGroupIds="{validation_name}" desc="Implementation step" expResult="NA">\n'
                PAF_SCRIPT += f'\t\t<then>\n'
            else:
                PAF_SCRIPT += f'\t<if valGroupIds="{validation_name}" desc="Implementation step" expResult="NA">\n'
            VALIDATION_SCRIPT += f'\n<valGroup groupId="{validation_name}" desc="Implementation step" expResult="NA">\n'
            if event["event"] == "validation-exists":
                VALIDATION_SCRIPT += f'\t<validate xpath="{xpath}" exists="true" snapshot="true" passMsg="{passMsg}" failMsg="{failMsg}" desc="Implementation step" expResult="NA"></validate>\n'
            elif event["event"] == "validation-not-exists":
                VALIDATION_SCRIPT += f'\t<validate xpath="{xpath}" exists="false" snapshot="true" passMsg="{passMsg}" failMsg="{failMsg}" desc="Implementation step" expResult="NA"></validate>\n'
            VALIDATION_SCRIPT += f'</valGroup>\n'
        elif event["event"] in ["validation-equals", "validation-not-equals", "validation-num-equals", "validation-num-not-equals", "validation-num-le", "validation-num-ge", "validation-contains", "validation-starts-with", "validation-ends-with"]:
            if event["validation_name"] == "Enter validation name(optional)":
                event["validation_name"] = name_engine.get_validation_name()
            if event["pass_msg"] == "Enter pass message(optional)":
                event["pass_msg"] = "STEP PASSED"
            if event["fail_msg"] == "Enter fail message(optional)":
                event["fail_msg"] = "STEP FAILED"    
            validation_name = event["validation_name"]
            variable1 = event["variable1"]
            variable2 = event["variable2"]
            passMsg = event["pass_msg"]
            failMsg = event["fail_msg"]
            if_condition = event["if_condition"]
            if_else_condition = event["if_else_condition"]
            if not if_condition and not if_else_condition:
                PAF_SCRIPT += f'\t<validation valGroupIds="{validation_name}" desc="Implementation step" expResult="NA"></validation>\n'
            elif if_else_condition:
                PAF_SCRIPT += f'\t<if valGroupIds="{validation_name}" desc="Implementation step" expResult="NA">\n'
                PAF_SCRIPT += f'\t\t<then>\n'
            else:
                PAF_SCRIPT += f'\t<if valGroupIds="{validation_name}" desc="Implementation step" expResult="NA">\n'
            VALIDATION_SCRIPT += f'\n<valGroup groupId="{validation_name}" desc="Implementation step" expResult="NA">\n'
            conditions = {"validation-equals": "equals", "validation-not-equals": "not_equals", "validation-num-equals": "num_equals", "validation-num-not-equals": "num_not_equals", "validation-num-le": "num_le", "validation-num-ge": "num_ge", "validation-contains": "contains", "validation-starts-with": "starts_with", "validation-ends-with": "ends_with"}
            condition = event["event"]
            VALIDATION_SCRIPT += f'\t<validate variable="{variable1}" condition="{conditions[condition]}" value="{variable2}" passMsg="{passMsg}" failMsg="{failMsg}" desc="Implementation step" expResult="NA"></validate>\n'
            VALIDATION_SCRIPT += f'</valGroup>\n'

            
    
    if not activity_name:
        activity_name = name_engine.get_activity_name()
    
    PAF_SCRIPT = f'<activity id="{activity_name}">\n' + PAF_SCRIPT + '</activity>' + VALIDATION_SCRIPT
    return {"PAF_SCRIPT" : PAF_SCRIPT, "activity_id" : activity_name}




def reformat_paf_flow(activity_id):

    name_engine = NameGenerator()
    flow_name = name_engine.get_flow_name()

    PAF_FLOW = f'<flow id="{flow_name}">\n'
    PAF_FLOW += f'\t<call activity="{activity_id}" xml="./sample_xml/activity.xml"></call>'
    PAF_FLOW += '</flow>'

    return {"PAF_FLOW": PAF_FLOW, "flow_id": flow_name}




def write_raw_json_data(activity_name, activity_description, activity_path, event_queue):

    data = {
    "activity_name": activity_name,
    "activity_description": activity_description,
    "activity_path": activity_path,
    "event_queue": event_queue
}
    
    json_data = json.dumps(data, indent=4)
    dir_path = os.path.join(os.getcwd(), 'raw_activity_data')
    os.makedirs(dir_path, exist_ok=True)

    filename = f"activity_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    json_file_path = os.path.join(dir_path, filename)

    # Write the JSON data to a file
    with open(json_file_path, 'w') as file:
        file.write(json_data)

    print(f"Data has been written to {json_file_path}")


              
    


        
            
