import tkinter as tk
from tkinter import ttk, messagebox
from Recorder import start_recording, stop_and_show_records, create_xpath, create_xpath2, pause_recording_main, resume_recording_main, close_browser_driver, refresh_browser_driver, redirect_url_driver
#from RunPAF import run_file, report_open
from serverConn import conn, delete_last_event, reset_event_queue
import time
from effects import FadingMessage




class Recorder:

    def __init__(self, activity_name, activity_description, activity_path, controller):
        super().__init__()
        self.activity_name = activity_name
        self.activity_description = activity_description
        self.activity_path = activity_path
        self.controller = controller

        self.root = tk.Tk()
        self.root.title("Recorder")

        # Navigation Bar
        self.nav_bar = tk.Frame(self.root)
        self.nav_bar.pack(side=tk.TOP, fill=tk.X)

        self.exit_button = tk.Button(self.nav_bar, text="Exit", command=self.exit)
        self.exit_button.pack(side=tk.LEFT, padx=5)
        self.url_entry = tk.Entry(self.nav_bar)
        self.url_entry.insert(0, 'http://')  # You can set a default or placeholder text if needed
        self.url_entry.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(self.nav_bar, text="Start", command=self.start_record)
        #self.run_button = tk.Button(self.nav_bar, text="Run Script", command=self.run_script)
        #self.open_report_button = tk.Button(self.nav_bar, text="Open Report", command=report_open)
        self.stop_button = tk.Button(self.nav_bar, text="Stop", command=self.stop_recording)
        self.delete_button = tk.Button(self.nav_bar, text="Delete", command=self.delete_step)
        self.insert_custom_button = tk.Button(self.nav_bar, text="Insert", command=self.insert_custom_step)
        self.get_xpath_button = tk.Button(self.nav_bar, text="Get xpath", command=self.capture_xpath_main)
        self.pause_resume_button = tk.Button(self.nav_bar, text="Pause", command=self.pause_recording)
        self.end_if_button = tk.Button(self.nav_bar, text="End if segment", command=self.end_if)
        self.end_if_then_button = tk.Button(self.nav_bar, text="End if then segment", command=self.end_if_then)
        self.end_else_button = tk.Button(self.nav_bar, text="End else segment", command=self.end_else)
        self.end_loop_button = tk.Button(self.nav_bar, text="End loop", command=self.end_loop_placeholder)

        self.start_button.pack(side=tk.LEFT, padx=5)

        # Right Sidebar
        self.sidebar = tk.Frame(self.root)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.dropdown_var = tk.StringVar(self.root)
        self.dropdown_var.set("Choose an option")
        self.dropdown = ttk.Combobox(self.sidebar, textvariable=self.dropdown_var, state="readonly")
        self.dropdown['values'] = ["alert", "getText", "hover", "highlight", "clear input", "variable-value", "excel", "validation", "if-condition", "if-else-condition", "loop", "redirect", "close browser", "refresh browser"]
        self.dropdown.bind("<<ComboboxSelected>>", self.handle_dropdown_selection)
        self.dropdown.pack(fill=tk.X)

        self.validation_dropdown_var = tk.StringVar(self.root)
        self.validation_dropdown_var.set("Choose validation")
        self.validation_dropdown = ttk.Combobox(self.sidebar, textvariable=self.validation_dropdown_var, state="readonly")
        self.validation_dropdown['values'] = ["exists", "not-exists", "equals", "not-equals" ,"contains", "starts-with", "ends-with", "num-equals", "num-not-equals", "num-lesser-than", "num-greater-than"]
        self.validation_dropdown.bind("<<ComboboxSelected>>", self.handle_validation_option)
        self.validation_dropdown.pack_forget()

        self.alert_dropdown_var = tk.StringVar(self.root)
        self.alert_dropdown_var.set("Choose Alert mode")
        self.alert_dropdown = ttk.Combobox(self.sidebar, textvariable=self.alert_dropdown_var, state="readonly")
        self.alert_dropdown['values'] = ["accept", "cancel", "getText", "input", "authenticate"]
        self.alert_dropdown.bind("<<ComboboxSelected>>", self.handle_alert_option)
        self.alert_dropdown.pack_forget()

        self.excel_dropdown_var = tk.StringVar(self.root)
        self.excel_dropdown_var.set("Choose Excel function")
        self.excel_dropdown = ttk.Combobox(self.sidebar, textvariable=self.excel_dropdown_var, state="readonly")
        self.excel_dropdown['values'] = ["read", "write", "search", "getExcelData"]
        self.excel_dropdown.bind("<<ComboboxSelected>>", self.handle_excel_option)
        self.excel_dropdown.pack_forget()

        self.dropdown_frame = tk.Frame(self.sidebar)
        self.dropdown.pack(fill=tk.X)     


        self.insert_custom_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.insert_custom_frame, text='Insert a custom step')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.custom_step_entry = tk.Entry(self.insert_custom_frame)
        self.custom_step_entry.insert(0, 'Enter the custom step')
        self.custom_step_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.custom_step_button = tk.Button(self.insert_custom_frame, text="Insert", command=self.insert_step)
        self.custom_step_button.pack(side=tk.TOP)

        self.display_xpath_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.display_xpath_frame, text='Generated xpath :')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.xpath_label = tk.Label(self.display_xpath_frame, bg='white', text='', relief='sunken', anchor='w')
        self.xpath_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.copy_button_text = "\U0001F4CB"
        self.copy_button = tk.Button(self.display_xpath_frame, text=self.copy_button_text)
        self.copy_button.pack(side=tk.LEFT, padx=5)
        self.copy_button.bind("<Button-1>", self.copy_to_clipboard)



        self.get_text_frame = tk.Frame(self.sidebar)
        self.variable_frame = tk.Frame(self.get_text_frame)
        self.variable_name_label = tk.Label(self.variable_frame, text="Variable Name:")
        self.variable_name_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.getText_variable_name_entry = tk.Entry(self.variable_frame)
        self.getText_variable_name_entry.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        self.variable_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.get_text_snapshot_frame = tk.Frame(self.get_text_frame)
        self.get_text_snapshot_label = tk.Label(self.get_text_snapshot_frame, text="Snapshot")
        self.get_text_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.get_text_after_var = tk.IntVar()
        self.get_text_before_var = tk.IntVar()
        self.get_text_after_check = tk.Checkbutton(self.get_text_snapshot_frame, text="After", variable=self.get_text_after_var)
        self.get_text_before_check = tk.Checkbutton(self.get_text_snapshot_frame, text="Before", variable=self.get_text_before_var)
        self.get_text_after_check.pack(side=tk.LEFT, padx=5)
        self.get_text_before_check.pack(side=tk.LEFT, padx=5)
        self.get_text_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.get_text_button = tk.Button(self.get_text_frame, text="Get Text", command=self.get_text)
        self.get_text_button.pack(side=tk.TOP)


        self.hover_frame = tk.Frame(self.sidebar)
        self.hover_button = tk.Button(self.hover_frame, text="Hover", command=self.hover)
        self.hover_button.pack(side=tk.TOP)

        self.highlight_frame = tk.Frame(self.sidebar)
        self.highlight_button = tk.Button(self.highlight_frame, text="Highlight", command=self.highlight)
        self.highlight_button.pack(side=tk.TOP)

        self.clearinput_frame = tk.Frame(self.sidebar)
        self.clearinput_button = tk.Button(self.clearinput_frame, text="Clear Input", command=self.clearinput)
        self.clearinput_button.pack(side=tk.TOP)


        self.validation_exists_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_exists_frame, text='Exists')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_exists_name_entry = tk.Entry(self.validation_exists_frame)
        self.validation_exists_name_entry.insert(0, 'Enter validation name(optional)')
        self.validation_exists_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.valExists_pass_msg_entry = tk.Entry(self.validation_exists_frame)
        self.valExists_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.valExists_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.valExists_fail_msg_entry = tk.Entry(self.validation_exists_frame)
        self.valExists_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.valExists_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_exists_snapshot_frame = tk.Frame(self.validation_exists_frame)
        self.validation_exists_snapshot_label = tk.Label(self.validation_exists_snapshot_frame, text="Snapshot")
        self.validation_exists_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_exists_after_var = tk.IntVar()
        self.validation_exists_before_var = tk.IntVar()
        self.validation_exists_after_check = tk.Checkbutton(self.validation_exists_snapshot_frame, text="After", variable=self.validation_exists_after_var)
        self.validation_exists_before_check = tk.Checkbutton(self.validation_exists_snapshot_frame, text="Before", variable=self.validation_exists_before_var)
        self.validation_exists_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_exists_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_exists_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_exists_frame, text="Validate", command=self.validate_exists)
        self.validate_button.pack(side=tk.TOP, pady=10)


        self.validation_not_exists_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_not_exists_frame, text='Not exists')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_not_exists_name_entry = tk.Entry(self.validation_not_exists_frame)
        self.validation_not_exists_name_entry.insert(0, 'Enter validation name(optional)')
        self.validation_not_exists_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.valNotExists_pass_msg_entry = tk.Entry(self.validation_not_exists_frame)
        self.valNotExists_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.valNotExists_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.valNotExists_fail_msg_entry = tk.Entry(self.validation_not_exists_frame)
        self.valNotExists_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.valNotExists_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_not_exists_snapshot_frame = tk.Frame(self.validation_not_exists_frame)
        self.validation_not_exists_snapshot_label = tk.Label(self.validation_not_exists_snapshot_frame, text="Snapshot")
        self.validation_not_exists_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_not_exists_after_var = tk.IntVar()
        self.validation_not_exists_before_var = tk.IntVar()
        self.validation_not_exists_after_check = tk.Checkbutton(self.validation_not_exists_snapshot_frame, text="After", variable=self.validation_not_exists_after_var)
        self.validation_not_exists_before_check = tk.Checkbutton(self.validation_not_exists_snapshot_frame, text="Before", variable=self.validation_not_exists_before_var)
        self.validation_not_exists_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_not_exists_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_not_exists_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_not_exists_frame, text="Validate", command=self.validate_not_exists)
        self.validate_button.pack(side=tk.TOP, pady=10)


        self.validation_equals_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_equals_frame, text='Equals')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.equals_variable1_value_entry = tk.Entry(self.validation_equals_frame)
        self.equals_variable1_value_entry.insert(0, 'Enter variable name')
        self.equals_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.equals_variable2_value_entry = tk.Entry(self.validation_equals_frame)
        self.equals_variable2_value_entry.insert(0, 'Enter value')
        self.equals_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.equals_validation_name_entry = tk.Entry(self.validation_equals_frame)
        self.equals_validation_name_entry.insert(0, 'Enter validation name(optional)')
        self.equals_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.equals_pass_msg_entry = tk.Entry(self.validation_equals_frame)
        self.equals_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.equals_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.equals_fail_msg_entry = tk.Entry(self.validation_equals_frame)
        self.equals_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.equals_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_equals_snapshot_frame = tk.Frame(self.validation_equals_frame)
        self.validation_equals_snapshot_label = tk.Label(self.validation_equals_snapshot_frame, text="Snapshot")
        self.validation_equals_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_equals_after_var = tk.IntVar()
        self.validation_equals_before_var = tk.IntVar()
        self.validation_equals_after_check = tk.Checkbutton(self.validation_equals_snapshot_frame, text="After", variable=self.validation_equals_after_var)
        self.validation_equals_before_check = tk.Checkbutton(self.validation_equals_snapshot_frame, text="Before", variable=self.validation_equals_before_var)
        self.validation_equals_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_equals_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_equals_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_equals_frame, text="Validate", command=self.validate_equals)
        self.validate_button.pack(side=tk.TOP, pady=14)

        self.validation_not_equals_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_not_equals_frame, text='Not equals')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.not_equals_variable1_value_entry = tk.Entry(self.validation_not_equals_frame)
        self.not_equals_variable1_value_entry.insert(0, 'Enter variable name')
        self.not_equals_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.not_equals_variable2_value_entry = tk.Entry(self.validation_not_equals_frame)
        self.not_equals_variable2_value_entry.insert(0, 'Enter value')
        self.not_equals_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.not_equals_validation_name_entry = tk.Entry(self.validation_not_equals_frame)
        self.not_equals_validation_name_entry.insert(0, 'Enter validation name(optional)')
        self.not_equals_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.not_equals_pass_msg_entry = tk.Entry(self.validation_not_equals_frame)
        self.not_equals_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.not_equals_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.not_equals_fail_msg_entry = tk.Entry(self.validation_not_equals_frame)
        self.not_equals_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.not_equals_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_not_equals_snapshot_frame = tk.Frame(self.validation_not_equals_frame)
        self.validation_not_equals_snapshot_label = tk.Label(self.validation_not_equals_snapshot_frame, text="Snapshot")
        self.validation_not_equals_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_not_equals_after_var = tk.IntVar()
        self.validation_not_equals_before_var = tk.IntVar()
        self.validation_not_equals_after_check = tk.Checkbutton(self.validation_not_equals_snapshot_frame, text="After", variable=self.validation_not_equals_after_var)
        self.validation_not_equals_before_check = tk.Checkbutton(self.validation_not_equals_snapshot_frame, text="Before", variable=self.validation_not_equals_before_var)
        self.validation_not_equals_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_not_equals_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_not_equals_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_not_equals_frame, text="Validate", command=self.validate_not_equals)
        self.validate_button.pack(side=tk.TOP, pady=14)


        self.validation_num_equals_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_num_equals_frame, text='Num equals')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_equals_variable1_value_entry = tk.Entry(self.validation_num_equals_frame)
        self.num_equals_variable1_value_entry.insert(0, 'Enter variable name')
        self.num_equals_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_equals_variable2_value_entry = tk.Entry(self.validation_num_equals_frame)
        self.num_equals_variable2_value_entry.insert(0, 'Enter value')
        self.num_equals_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_equals_validation_name_entry = tk.Entry(self.validation_num_equals_frame)
        self.num_equals_validation_name_entry.insert(0, 'Enter validation name(optional)')
        self.num_equals_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_equals_pass_msg_entry = tk.Entry(self.validation_num_equals_frame)
        self.num_equals_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.num_equals_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_equals_fail_msg_entry = tk.Entry(self.validation_num_equals_frame)
        self.num_equals_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.num_equals_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_num_equals_snapshot_frame = tk.Frame(self.validation_num_equals_frame)
        self.validation_num_equals_snapshot_label = tk.Label(self.validation_num_equals_snapshot_frame, text="Snapshot")
        self.validation_num_equals_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_num_equals_after_var = tk.IntVar()
        self.validation_num_equals_before_var = tk.IntVar()
        self.validation_num_equals_after_check = tk.Checkbutton(self.validation_num_equals_snapshot_frame, text="After", variable=self.validation_num_equals_after_var)
        self.validation_num_equals_before_check = tk.Checkbutton(self.validation_num_equals_snapshot_frame, text="Before", variable=self.validation_num_equals_before_var)
        self.validation_num_equals_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_num_equals_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_num_equals_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_num_equals_frame, text="Validate", command=self.validate_num_equals)
        self.validate_button.pack(side=tk.TOP, pady=14)


        self.validation_num_not_equals_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_num_not_equals_frame, text='Num not equals')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_not_equals_variable1_value_entry = tk.Entry(self.validation_num_not_equals_frame)
        self.num_not_equals_variable1_value_entry.insert(0, 'Enter variable name')
        self.num_not_equals_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_not_equals_variable2_value_entry = tk.Entry(self.validation_num_not_equals_frame)
        self.num_not_equals_variable2_value_entry.insert(0, 'Enter value')
        self.num_not_equals_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_not_equals_validation_name_entry = tk.Entry(self.validation_num_not_equals_frame)
        self.num_not_equals_validation_name_entry.insert(0, 'Enter validation name(optional)')
        self.num_not_equals_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_not_equals_pass_msg_entry = tk.Entry(self.validation_num_not_equals_frame)
        self.num_not_equals_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.num_not_equals_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_not_equals_fail_msg_entry = tk.Entry(self.validation_num_not_equals_frame)
        self.num_not_equals_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.num_not_equals_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_num_not_equals_snapshot_frame = tk.Frame(self.validation_num_not_equals_frame)
        self.validation_num_not_equals_snapshot_label = tk.Label(self.validation_num_not_equals_snapshot_frame, text="Snapshot")
        self.validation_num_not_equals_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_num_not_equals_after_var = tk.IntVar()
        self.validation_num_not_equals_before_var = tk.IntVar()
        self.validation_num_not_equals_after_check = tk.Checkbutton(self.validation_num_not_equals_snapshot_frame, text="After", variable=self.validation_num_not_equals_after_var)
        self.validation_num_not_equals_before_check = tk.Checkbutton(self.validation_num_not_equals_snapshot_frame, text="Before", variable=self.validation_num_not_equals_before_var)
        self.validation_num_not_equals_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_num_not_equals_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_num_not_equals_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_num_not_equals_frame, text="Validate", command=self.validate_num_not_equals)
        self.validate_button.pack(side=tk.TOP, pady=14)


        self.validation_num_le_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_num_le_frame, text='Num lesser than')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_le_variable1_value_entry = tk.Entry(self.validation_num_le_frame)
        self.num_le_variable1_value_entry.insert(0, 'Enter variable name')
        self.num_le_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_le_variable2_value_entry = tk.Entry(self.validation_num_le_frame)
        self.num_le_variable2_value_entry.insert(0, 'Enter value')
        self.num_le_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_le_validation_name_entry = tk.Entry(self.validation_num_le_frame)
        self.num_le_validation_name_entry.insert(0, 'Enter validation name(optional)')
        self.num_le_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_le_pass_msg_entry = tk.Entry(self.validation_num_le_frame)
        self.num_le_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.num_le_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_le_fail_msg_entry = tk.Entry(self.validation_num_le_frame)
        self.num_le_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.num_le_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_num_le_snapshot_frame = tk.Frame(self.validation_num_le_frame)
        self.validation_num_le_snapshot_label = tk.Label(self.validation_num_le_snapshot_frame, text="Snapshot")
        self.validation_num_le_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_num_le_after_var = tk.IntVar()
        self.validation_num_le_before_var = tk.IntVar()
        self.validation_num_le_after_check = tk.Checkbutton(self.validation_num_le_snapshot_frame, text="After", variable=self.validation_num_le_after_var)
        self.validation_num_le_before_check = tk.Checkbutton(self.validation_num_le_snapshot_frame, text="Before", variable=self.validation_num_le_before_var)
        self.validation_num_le_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_num_le_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_num_le_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_num_le_frame, text="Validate", command=self.validate_num_le)
        self.validate_button.pack(side=tk.TOP, pady=14)


        self.validation_num_ge_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_num_ge_frame, text='Num greater than')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_ge_variable1_value_entry = tk.Entry(self.validation_num_ge_frame)
        self.num_ge_variable1_value_entry.insert(0, 'Enter variable name')
        self.num_ge_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_ge_variable2_value_entry = tk.Entry(self.validation_num_ge_frame)
        self.num_ge_variable2_value_entry.insert(0, 'Enter value')
        self.num_ge_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_ge_validation_name_entry = tk.Entry(self.validation_num_ge_frame)
        self.num_ge_validation_name_entry.insert(0, 'Enter validation name(optional)')
        self.num_ge_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_ge_pass_msg_entry = tk.Entry(self.validation_num_ge_frame)
        self.num_ge_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.num_ge_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.num_ge_fail_msg_entry = tk.Entry(self.validation_num_ge_frame)
        self.num_ge_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.num_ge_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_num_ge_snapshot_frame = tk.Frame(self.validation_num_ge_frame)
        self.validation_num_ge_snapshot_label = tk.Label(self.validation_num_ge_snapshot_frame, text="Snapshot")
        self.validation_num_ge_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_num_ge_after_var = tk.IntVar()
        self.validation_num_ge_before_var = tk.IntVar()
        self.validation_num_ge_after_check = tk.Checkbutton(self.validation_num_ge_snapshot_frame, text="After", variable=self.validation_num_ge_after_var)
        self.validation_num_ge_before_check = tk.Checkbutton(self.validation_num_ge_snapshot_frame, text="Before", variable=self.validation_num_ge_before_var)
        self.validation_num_ge_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_num_ge_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_num_ge_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_num_ge_frame, text="Validate", command=self.validate_num_ge)
        self.validate_button.pack(side=tk.TOP, pady=14)


        self.validation_contains_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_contains_frame, text='Contains')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.contains_variable1_value_entry = tk.Entry(self.validation_contains_frame)
        self.contains_variable1_value_entry.insert(0, 'Enter variable name')
        self.contains_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.contains_variable2_value_entry = tk.Entry(self.validation_contains_frame)
        self.contains_variable2_value_entry.insert(0, 'Enter value')
        self.contains_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.contains_validation_name_entry = tk.Entry(self.validation_contains_frame)
        self.contains_validation_name_entry.insert(0, 'Enter validation name(optional)')
        self.contains_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.contains_pass_msg_entry = tk.Entry(self.validation_contains_frame)
        self.contains_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.contains_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.contains_fail_msg_entry = tk.Entry(self.validation_contains_frame)
        self.contains_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.contains_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_contains_snapshot_frame = tk.Frame(self.validation_contains_frame)
        self.validation_contains_snapshot_label = tk.Label(self.validation_contains_snapshot_frame, text="Snapshot")
        self.validation_contains_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_contains_after_var = tk.IntVar()
        self.validation_contains_before_var = tk.IntVar()
        self.validation_contains_after_check = tk.Checkbutton(self.validation_contains_snapshot_frame, text="After", variable=self.validation_contains_after_var)
        self.validation_contains_before_check = tk.Checkbutton(self.validation_contains_snapshot_frame, text="Before", variable=self.validation_contains_before_var)
        self.validation_contains_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_contains_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_contains_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_contains_frame, text="Validate", command=self.validate_contains)
        self.validate_button.pack(side=tk.TOP, pady=14)


        self.validation_starts_with_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_starts_with_frame, text='Starts with')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.starts_with_variable1_value_entry = tk.Entry(self.validation_starts_with_frame)
        self.starts_with_variable1_value_entry.insert(0, 'Enter variable name')
        self.starts_with_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.starts_with_variable2_value_entry = tk.Entry(self.validation_starts_with_frame)
        self.starts_with_variable2_value_entry.insert(0, 'Enter value')
        self.starts_with_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.starts_with_validation_name_entry = tk.Entry(self.validation_starts_with_frame)
        self.starts_with_validation_name_entry.insert(0, 'Enter validation name(optional)')
        self.starts_with_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.starts_with_pass_msg_entry = tk.Entry(self.validation_starts_with_frame)
        self.starts_with_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.starts_with_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.starts_with_fail_msg_entry = tk.Entry(self.validation_starts_with_frame)
        self.starts_with_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.starts_with_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_starts_with_snapshot_frame = tk.Frame(self.validation_starts_with_frame)
        self.validation_starts_with_snapshot_label = tk.Label(self.validation_starts_with_snapshot_frame, text="Snapshot")
        self.validation_starts_with_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_starts_with_after_var = tk.IntVar()
        self.validation_starts_with_before_var = tk.IntVar()
        self.validation_starts_with_after_check = tk.Checkbutton(self.validation_starts_with_snapshot_frame, text="After", variable=self.validation_starts_with_after_var)
        self.validation_starts_with_before_check = tk.Checkbutton(self.validation_starts_with_snapshot_frame, text="Before", variable=self.validation_starts_with_before_var)
        self.validation_starts_with_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_starts_with_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_starts_with_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_starts_with_frame, text="Validate", command=self.validate_starts_with)
        self.validate_button.pack(side=tk.TOP, pady=14)


        self.validation_ends_with_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.validation_ends_with_frame, text='Ends with')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.ends_with_variable1_value_entry = tk.Entry(self.validation_ends_with_frame)
        self.ends_with_variable1_value_entry.insert(0, 'Enter variable name')
        self.ends_with_variable1_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.ends_with_variable2_value_entry = tk.Entry(self.validation_ends_with_frame)
        self.ends_with_variable2_value_entry.insert(0, 'Enter value')
        self.ends_with_variable2_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.ends_with_validation_name_entry = tk.Entry(self.validation_ends_with_frame)
        self.ends_with_validation_name_entry.insert(0, 'Enter validation name(optional)')
        self.ends_with_validation_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.ends_with_pass_msg_entry = tk.Entry(self.validation_ends_with_frame)
        self.ends_with_pass_msg_entry.insert(0, 'Enter pass message(optional)')
        self.ends_with_pass_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.ends_with_fail_msg_entry = tk.Entry(self.validation_ends_with_frame)
        self.ends_with_fail_msg_entry.insert(0, 'Enter fail message(optional)')
        self.ends_with_fail_msg_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.validation_ends_with_snapshot_frame = tk.Frame(self.validation_ends_with_frame)
        self.validation_ends_with_snapshot_label = tk.Label(self.validation_ends_with_snapshot_frame, text="Snapshot")
        self.validation_ends_with_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.validation_ends_with_after_var = tk.IntVar()
        self.validation_ends_with_before_var = tk.IntVar()
        self.validation_ends_with_after_check = tk.Checkbutton(self.validation_ends_with_snapshot_frame, text="After", variable=self.validation_ends_with_after_var)
        self.validation_ends_with_before_check = tk.Checkbutton(self.validation_ends_with_snapshot_frame, text="Before", variable=self.validation_ends_with_before_var)
        self.validation_ends_with_after_check.pack(side=tk.LEFT, padx=5)
        self.validation_ends_with_before_check.pack(side=tk.LEFT, padx=5)
        self.validation_ends_with_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.validation_ends_with_frame, text="Validate", command=self.validate_ends_with)
        self.validate_button.pack(side=tk.TOP, pady=14)


        self.variable_value_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.variable_value_frame, text='Variable value')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.variable_value_name_entry = tk.Entry(self.variable_value_frame)
        self.variable_value_name_entry.insert(0, 'Enter variable name')
        self.variable_value_name_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.variable_value_entry = tk.Entry(self.variable_value_frame)
        self.variable_value_entry.insert(0, 'Enter variable value')
        self.variable_value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.variable_value_snapshot_frame = tk.Frame(self.variable_value_frame)
        self.variable_value_snapshot_label = tk.Label(self.variable_value_snapshot_frame, text="Snapshot")
        self.variable_value_snapshot_label.pack(side=tk.LEFT, padx=5)
        self.variable_value_after_var = tk.IntVar()
        self.variable_value_before_var = tk.IntVar()
        self.variable_value_after_check = tk.Checkbutton(self.variable_value_snapshot_frame, text="After", variable=self.variable_value_after_var)
        self.variable_value_before_check = tk.Checkbutton(self.variable_value_snapshot_frame, text="Before", variable=self.variable_value_before_var)
        self.variable_value_after_check.pack(side=tk.LEFT, padx=5)
        self.variable_value_before_check.pack(side=tk.LEFT, padx=5)
        self.variable_value_snapshot_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.validate_button = tk.Button(self.variable_value_frame, text="Stash", command=self.variable_value)
        self.validate_button.pack(side=tk.TOP, pady=8)


        self.loop_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.loop_frame, text='Loop')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.start_index_entry = tk.Entry(self.loop_frame)
        self.start_index_entry.insert(0, 'Enter start index(optional - default to 1)')
        self.start_index_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.last_index_entry = tk.Entry(self.loop_frame)
        self.last_index_entry.insert(0, 'Enter last index')
        self.last_index_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.increment_entry = tk.Entry(self.loop_frame)
        self.increment_entry.insert(0, 'Enter increment(optional - deafult to 1)')
        self.increment_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.counterVar_entry = tk.Entry(self.loop_frame)
        self.counterVar_entry.insert(0, 'Assign counter(optional - default to i)')
        self.counterVar_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.start_loop_button = tk.Button(self.loop_frame, text="Start loop", command=self.start_loop)
        self.start_loop_button.pack(side=tk.TOP, pady=8)


        self.alert_accept_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.alert_accept_frame, text='Alert Accept')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.alert_accept_button = tk.Button(self.alert_accept_frame, text="Accept", command=self.alert_accept)
        self.alert_accept_button.pack(side=tk.TOP, pady=8)


        self.alert_cancel_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.alert_cancel_frame, text='Alert Cancel')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.alert_cancel_button = tk.Button(self.alert_cancel_frame, text="Cancel", command=self.alert_cancel)
        self.alert_cancel_button.pack(side=tk.TOP, pady=8)


        self.alert_getText_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.alert_getText_frame, text='Alert Get Text')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.keyName_entry = tk.Entry(self.alert_getText_frame)
        self.keyName_entry.insert(0, 'Enter variable name')
        self.keyName_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.alert_getText_button = tk.Button(self.alert_getText_frame, text="GetText", command=self.alert_getText)
        self.alert_getText_button.pack(side=tk.TOP, pady=8)


        self.alert_input_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.alert_input_frame, text='Alert Input')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.value_entry = tk.Entry(self.alert_input_frame)
        self.value_entry.insert(0, 'Enter desired alert input')
        self.value_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.alert_input_button = tk.Button(self.alert_input_frame, text="Input", command=self.alert_input)
        self.alert_input_button.pack(side=tk.TOP, pady=8)


        self.redirect_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.redirect_frame, text='Redirect URL')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.redirect_url_entry = tk.Entry(self.redirect_frame)
        self.redirect_url_entry.insert(0, 'Enter the URL')
        self.redirect_url_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.redirect_url_button = tk.Button(self.redirect_frame, text="Redirect", command=self.redirect_url)
        self.redirect_url_button.pack(side=tk.TOP, pady=8)


        self.alert_authenticate_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.alert_authenticate_frame, text='Alert Authenticate')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.user_entry = tk.Entry(self.alert_authenticate_frame)
        self.user_entry.insert(0, 'Enter the username')
        self.user_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.pwd_entry = tk.Entry(self.alert_authenticate_frame)
        self.pwd_entry.insert(0, 'Enter the password')
        self.pwd_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.alert_input_button = tk.Button(self.alert_authenticate_frame, text="Authenticate", command=self.alert_authenticate)
        self.alert_input_button.pack(side=tk.TOP, pady=8)


        self.close_browser_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.close_browser_frame, text='Close Browser')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.close_browser_button = tk.Button(self.close_browser_frame, text="Close Browser", command=self.close_browser)
        self.close_browser_button.pack(side=tk.TOP, pady=8)

        self.refresh_browser_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.refresh_browser_frame, text='Refresh Browser')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.refresh_browser_button = tk.Button(self.refresh_browser_frame, text="Refresh Browser", command=self.refresh_browser)
        self.refresh_browser_button.pack(side=tk.TOP, pady=8)

        self.excel_read_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.excel_read_frame, text='Read from Excel')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.row_read_entry = tk.Entry(self.excel_read_frame)
        self.row_read_entry.insert(0, 'Enter the row num')
        self.row_read_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.col_read_entry = tk.Entry(self.excel_read_frame)
        self.col_read_entry.insert(0, 'Enter the col num')
        self.col_read_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.sheet_read_entry = tk.Entry(self.excel_read_frame)
        self.sheet_read_entry.insert(0, 'Enter the sheet name')
        self.sheet_read_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.excelPath_read_entry = tk.Entry(self.excel_read_frame)
        self.excelPath_read_entry.insert(0, 'Enter the excel path')
        self.excelPath_read_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.variable_read_entry = tk.Entry(self.excel_read_frame)
        self.variable_read_entry.insert(0, 'Enter the variable name')
        self.variable_read_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.excel_read_button = tk.Button(self.excel_read_frame, text="Excel read", command=self.excel_read)
        self.excel_read_button.pack(side=tk.TOP, pady=8)

        self.excel_write_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.excel_write_frame, text='Write to Excel')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.row_write_entry = tk.Entry(self.excel_write_frame)
        self.row_write_entry.insert(0, 'Enter the row num')
        self.row_write_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.col_write_entry = tk.Entry(self.excel_write_frame)
        self.col_write_entry.insert(0, 'Enter the col num')
        self.col_write_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.sheet_write_entry = tk.Entry(self.excel_write_frame)
        self.sheet_write_entry.insert(0, 'Enter the sheet name')
        self.sheet_write_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.excelPath_write_entry = tk.Entry(self.excel_write_frame)
        self.excelPath_write_entry.insert(0, 'Enter the excel path')
        self.excelPath_write_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.value_write_entry = tk.Entry(self.excel_write_frame)
        self.value_write_entry.insert(0, 'Enter the value')
        self.value_write_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.excel_write_button = tk.Button(self.excel_write_frame, text="Excel write", command=self.excel_write)
        self.excel_write_button.pack(side=tk.TOP, pady=8)

        self.excel_search_frame = tk.Frame(self.sidebar)
        self.title_label = tk.Label(self.excel_search_frame, text='Search in Excel')
        self.title_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.row_search_entry = tk.Entry(self.excel_search_frame)
        self.row_search_entry.insert(0, 'Enter the row start num')
        self.row_search_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.col_search_entry = tk.Entry(self.excel_search_frame)
        self.col_search_entry.insert(0, 'Enter the col num')
        self.col_search_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.sheet_search_entry = tk.Entry(self.excel_search_frame)
        self.sheet_search_entry.insert(0, 'Enter the sheet name')
        self.sheet_search_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.excelPath_search_entry = tk.Entry(self.excel_search_frame)
        self.excelPath_search_entry.insert(0, 'Enter the excel path')
        self.excelPath_search_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.variable_search_entry = tk.Entry(self.excel_search_frame)
        self.variable_search_entry.insert(0, 'Enter the variable name')
        self.variable_search_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.text_search_entry = tk.Entry(self.excel_search_frame)
        self.text_search_entry.insert(0, 'Enter the text to be searched')
        self.text_search_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.excel_search_button = tk.Button(self.excel_search_frame, text="Excel search", command=self.excel_search)
        self.excel_search_button.pack(side=tk.TOP, pady=8)


        # Left Main Area
        self.main_area = tk.Frame(self.root)
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.executed_steps = tk.Listbox(self.main_area, width=50, height=20)
        self.executed_steps.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for the Listbox
        self.scrollbar = tk.Scrollbar(self.main_area, orient="vertical", command=self.executed_steps.yview)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.executed_steps.config(yscrollcommand=self.scrollbar.set)
        self.executed_steps.config(xscrollcommand=self.scrollbar.set)



    def start_record(self):
        reset_event_queue()
        self.executed_steps.delete(0, tk.END)
        self.start_button.pack_forget()
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.pause_resume_button.config(text="Pause", command=self.pause_recording)
        self.pause_resume_button.pack(side=tk.LEFT, padx=5)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        self.update_steps("Start Recording")
        self.disable_dropdown_options()
        url = self.url_entry.get()
        start_recording(url)

    def stop_recording(self):
        self.stop_button.pack_forget()
        self.pause_resume_button.pack_forget()
        self.dropdown_frame.pack_forget()
        self.delete_button.pack_forget()
        self.update_steps("Stop Recording")
        self.disable_dropdown_options()
        response = stop_and_show_records(self.activity_name, self.activity_description, self.activity_path)
        if response:
            self.start_button.pack(side=tk.LEFT, padx=5)
            #self.run_button.pack(side=tk.LEFT, padx=5)


    def pause_recording(self):
        pause_recording_main()
        self.pause_resume_button.config(text="Resume", command=self.resume_recording)
        self.dropdown_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
        self.insert_custom_button.pack(side=tk.RIGHT, padx=5)
        self.get_xpath_button.pack(side=tk.RIGHT, padx=5)
        self.update_steps("Pause Recording")
        self.enable_dropdown_options()

    def resume_recording(self):
        resume_recording_main()
        self.pause_resume_button.config(text="Pause", command=self.pause_recording)
        self.dropdown_frame.pack_forget()
        self.variable_value_frame.pack_forget()
        self.get_text_frame.pack_forget()
        self.validation_exists_frame.pack_forget()
        self.validation_not_exists_frame.pack_forget()
        self.validation_equals_frame.pack_forget()
        self.validation_not_equals_frame.pack_forget()
        self.validation_num_equals_frame.pack_forget()
        self.validation_num_not_equals_frame.pack_forget()
        self.loop_frame.pack_forget()
        self.insert_custom_button.pack_forget()
        self.insert_custom_frame.pack_forget()
        self.get_xpath_button.pack_forget()
        self.display_xpath_frame.pack_forget()
        self.alert_accept_frame.pack_forget()
        self.alert_cancel_frame.pack_forget()
        self.alert_getText_frame.pack_forget()
        self.alert_input_frame.pack_forget()
        self.alert_authenticate_frame.pack_forget()
        self.hover_frame.pack_forget()
        self.highlight_frame.pack_forget()
        self.excel_read_frame.pack_forget()
        self.excel_write_frame.pack_forget()
        self.excel_search_frame.pack_forget()
        self.redirect_frame.pack_forget()
        self.refresh_browser_frame.pack_forget()
        self.close_browser_frame.pack_forget()
        self.update_steps("Resume Recording")
        self.disable_dropdown_options()


    def delete_step(self):
        # Show a confirmation dialog
        self.user_response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the previous step?")
        # Check the user's response
        if self.user_response:  # If the user clicked 'Yes'
            deleted_event = delete_last_event()
            if "end" in deleted_event[0] or deleted_event[0] == "loop" or deleted_event[0] == "getText" or "validation" in deleted_event[0] or "if-" in deleted_event[0] or deleted_event[0] == "variable-value" or deleted_event[0] == "custom-step" or "alert" in deleted_event[0] or deleted_event[0] == "hover" or deleted_event[0] == "highlight" or "excel" in deleted_event[0] or deleted_event[0] == "clearinput" or "excel" in deleted_event[0] or "browser" in deleted_event[0] or deleted_event[0] == "redirect":
                self.delete_last_step_from_executed_steps()
        else:
            return


    def insert_custom_step(self):
        self.forget_all()
        self.insert_custom_frame.pack(side=tk.TOP, pady=5, fill=tk.X)

    def capture_xpath_main(self):
        xpath = create_xpath2()
        if not xpath:
            messagebox.showwarning("Warning", "You have not clicked on your target element you want the xpath of!")
            return
        self.xpath_label.config(text=xpath)
        self.display_xpath_frame.pack(side=tk.TOP, pady=5, fill=tk.X)


    def end_if(self):
        now = int(time.time() * 1000)
        conn([["end-if", now]])
        self.update_steps(f"End if condition segment")
        self.end_if_button.pack_forget()

    def end_if_then(self):
        now = int(time.time() * 1000)
        conn([["end-if-then", now]])
        self.update_steps(f"End if then condition segment")
        self.end_if_then_button.pack_forget()
        self.end_else_button.pack(side=tk.LEFT, padx=5)

    def end_else(self):
        now = int(time.time() * 1000)
        conn([["end-else", now]])
        self.update_steps(f"End else condition segment")
        self.end_else_button.pack_forget()

    def end_loop_create(self, counterVar):
        global counterVariable
        counterVariable = counterVar
        self.end_loop_button.config(text=f"End loop - {counterVar}", command=self.end_loop)
        self.end_loop_button.pack(side=tk.LEFT, padx=5)


    def end_loop(self):
        now = int(time.time() * 1000)
        conn([["end-loop", now]])
        self.update_steps(f"End loop - {counterVariable}")
        self.end_loop_button.pack_forget()

    def end_loop_placeholder(self):
        pass


    def enable_dropdown_options(self):
        self.dropdown.configure(state='readonly')
        self.validation_dropdown.configure(state='readonly')
        self.alert_dropdown.configure(state='readonly')

    def disable_dropdown_options(self):
        self.dropdown.configure(state='disabled')
        self.forget_all()



    def handle_excel_option(self, event=None):
        if self.recording_paused():
            selected_excel_option = self.excel_dropdown_var.get()
            print(f"The selected alert option is: {selected_excel_option}")
            if selected_excel_option == "read":
                self.forget_all()
                self.excel_read_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_excel_option == "write":
                self.forget_all()
                self.excel_write_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_excel_option == "search":
                self.forget_all()
                self.excel_search_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_excel_option == "getExcelData":
                self.forget_all()
                #self.alert_input_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            


    def handle_alert_option(self, event=None):
        if self.recording_paused():
            selected_alert = self.alert_dropdown_var.get()
            print(f"The selected alert option is: {selected_alert}")
            if selected_alert == "accept":
                self.forget_all()
                self.alert_accept_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_alert == "cancel":
                self.forget_all()
                self.alert_cancel_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_alert == "getText":
                self.forget_all()
                self.alert_getText_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_alert == "input":
                self.forget_all()
                self.alert_input_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_alert == "authenticate":
                self.forget_all()
                self.alert_authenticate_frame.pack(side=tk.TOP, pady=5, fill=tk.X)


    def handle_validation_option(self, event=None):
        if self.recording_paused():
            selected_validation = self.validation_dropdown_var.get()
            print(f"The selected validation option is: {selected_validation}")
            if selected_validation == "exists":
                self.forget_all()
                self.validation_exists_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_validation == "not-exists":
                self.forget_all()
                self.validation_not_exists_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_validation == "equals":
                self.forget_all()
                self.validation_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_validation == "not-equals":
                self.forget_all()
                self.validation_not_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_validation == "num-equals":
                self.forget_all()
                self.validation_num_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_validation == "num-not-equals":
                self.forget_all()
                self.validation_num_not_equals_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_validation == "starts-with":
                self.forget_all()
                self.validation_starts_with_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_validation == "ends-with":
                self.forget_all()
                self.validation_ends_with_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_validation == "contains":
                self.forget_all()
                self.validation_contains_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_validation == "num-lesser-than":
                self.forget_all()
                self.validation_num_le_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected_validation == "num-greater-than":
                self.forget_all()
                self.validation_num_ge_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            else:
                self.forget_all()


    def handle_dropdown_selection(self, event=None):
        if self.recording_paused():
            self.root.update_idletasks()
            selected = self.dropdown_var.get()
            print(f"The selected dropdown option is : {selected}")

            # Check if one of the specific options is selected
            if selected in ["validation", "if-condition", "if-else-condition"]:
                self.forget_all()
                self.validation_dropdown.pack(fill=tk.X)  # Show the validation dropdown
            elif selected == "getText":
                self.forget_all()
                self.get_text_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected == "variable-value":
                self.forget_all()
                self.variable_value_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected == "loop":
                self.forget_all()
                self.loop_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected == "alert":
                self.forget_all()
                self.alert_dropdown.pack(fill=tk.X)
            elif selected == "excel":
                self.forget_all()
                self.excel_dropdown.pack(fill=tk.X)
            elif selected == "hover":
                self.forget_all()
                self.hover_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected == "highlight":
                self.forget_all()
                self.highlight_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected == "clear input":
                self.forget_all()
                self.clearinput_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected == "redirect":
                self.forget_all()
                self.redirect_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected == "close browser":
                self.forget_all()
                self.close_browser_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            elif selected == "refresh browser":
                self.forget_all()
                self.refresh_browser_frame.pack(side=tk.TOP, pady=5, fill=tk.X)
            else:
                self.forget_all()

        else:
            messagebox.showinfo("Alert", "Please pause the recording before entering custom steps.")

    
    def forget_all(self):
        self.alert_dropdown.pack_forget()
        self.validation_dropdown.pack_forget()
        self.loop_frame.pack_forget()
        self.variable_value_frame.pack_forget()
        self.get_text_frame.pack_forget()
        self.validation_exists_frame.pack_forget()
        self.validation_not_exists_frame.pack_forget()
        self.validation_equals_frame.pack_forget()
        self.validation_not_equals_frame.pack_forget()
        self.validation_num_equals_frame.pack_forget()
        self.validation_num_not_equals_frame.pack_forget()
        self.validation_contains_frame.pack_forget()
        self.validation_starts_with_frame.pack_forget()
        self.validation_ends_with_frame.pack_forget()
        self.validation_num_le_frame.pack_forget()
        self.validation_num_ge_frame.pack_forget()
        self.insert_custom_frame.pack_forget()
        self.display_xpath_frame.pack_forget()
        self.alert_accept_frame.pack_forget()
        self.alert_cancel_frame.pack_forget()
        self.alert_getText_frame.pack_forget()
        self.alert_input_frame.pack_forget()
        self.hover_frame.pack_forget()
        self.highlight_frame.pack_forget()
        self.alert_authenticate_frame.pack_forget()
        self.clearinput_frame.pack_forget()
        self.excel_dropdown.pack_forget()
        self.excel_read_frame.pack_forget()
        self.excel_write_frame.pack_forget()
        self.excel_search_frame.pack_forget()
        self.redirect_frame.pack_forget()
        self.refresh_browser_frame.pack_forget()
        self.close_browser_frame.pack_forget()

    def recording_paused(self):
        return self.pause_resume_button.cget('text') == "Resume"

    def get_text(self):
        get_text_after_checked = self.get_text_after_var.get()
        get_text_before_checked = self.get_text_before_var.get()
        variable_name = self.getText_variable_name_entry.get()
        xpath = create_xpath()
        now = int(time.time() * 1000)
        conn([["getText", now, xpath, variable_name, get_text_after_checked, get_text_before_checked]])
        self.get_text_frame.pack_forget()
        self.update_steps(f"Get Text: {variable_name}")

    def hover(self):
        xpath = create_xpath()
        now = int(time.time() * 1000)
        conn([["hover", now, xpath]])
        self.hover_frame.pack_forget()
        self.update_steps("Hover")

    def redirect_url(self):
        redirect_url = self.redirect_url_entry.get()
        now = int(time.time() * 1000)
        conn([["redirect-url", now, redirect_url]])
        self.redirect_frame.pack_forget()
        self.update_steps(f"Redirect to : {redirect_url}")
        redirect_url_driver(redirect_url)

    def highlight(self):
        xpath = create_xpath()
        now = int(time.time() * 1000)
        conn([["highlight", now, xpath]])
        self.highlight_frame.pack_forget()
        self.update_steps("Highlight")

    def clearinput(self):
        xpath = create_xpath()
        now = int(time.time() * 1000)
        conn([["clearinput", now, xpath]])
        self.clearinput_frame.pack_forget()
        self.update_steps("Clear input")

    def excel_read(self):
        row = self.row_read_entry.get()
        col = self.col_read_entry.get()
        sheet = self.sheet_read_entry.get()
        path = self.excelPath_read_entry.get()
        variable = self.variable_read_entry.get()
        now = int(time.time() * 1000)
        conn([["excel-read", now, row, col, sheet, path, variable]])
        self.excel_read_frame.pack_forget()
        self.update_steps(f"Excel read and store in : {variable}")

    def excel_write(self):
        row = self.row_write_entry.get()
        col = self.col_write_entry.get()
        sheet = self.sheet_write_entry.get()
        path = self.excelPath_write_entry.get()
        value = self.value_write_entry.get()
        now = int(time.time() * 1000)
        conn([["excel-write", now, row, col, sheet, path, value]])
        self.excel_write_frame.pack_forget()
        self.update_steps(f"Excel write : {value}")

    def excel_search(self):
        row = self.row_search_entry.get()
        col = self.col_search_entry.get()
        sheet = self.sheet_search_entry.get()
        path = self.excelPath_search_entry.get()
        text = self.text_search_entry.get()
        variable = self.variable_search_entry.get()
        now = int(time.time() * 1000)
        conn([["excel-search", now, row, col, sheet, path, text, variable]])
        self.excel_search_frame.pack_forget()
        self.update_steps(f"Excel searched value in : {variable}")


    def validate_exists(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_exists_after_checked = self.validation_exists_after_var.get()
        validate_exists_before_checked = self.validation_exists_before_var.get()
        validation_name = self.validation_exists_name_entry.get()
        validation_pass_msg = self.valExists_pass_msg_entry.get()
        validation_fail_msg = self.valExists_fail_msg_entry.get()
        xpath = create_xpath()
        now = int(time.time() * 1000)
        conn([["validation-exists", now, xpath, validation_name, validation_pass_msg, validation_fail_msg, validate_exists_after_checked, validate_exists_before_checked, if_condition, if_else_condition]])
        self.validation_exists_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"Validate-exists: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then exists starts: {validation_name}")
        else:
            self.update_steps(f"if exists starts: {validation_name}")

    def validate_not_exists(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_not_exists_after_checked = self.validation_not_exists_after_var.get()
        validate_not_exists_before_checked = self.validation_not_exists_before_var.get()
        validation_name = self.validation_not_exists_name_entry.get()
        validation_pass_msg = self.valNotExists_pass_msg_entry.get()
        validation_fail_msg = self.valNotExists_fail_msg_entry.get()
        xpath = create_xpath()
        now = int(time.time() * 1000)
        conn([["validation-not-exists", now, xpath, validation_name, validation_pass_msg, validation_fail_msg, validate_not_exists_after_checked, validate_not_exists_before_checked, if_condition, if_else_condition]])
        self.variable_value_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"Validate-not-exists: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then not-exists starts: {validation_name}")
        else:
            self.update_steps(f"if not-exists starts: {validation_name}")

    def validate_equals(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_equals_after_checked = self.validation_equals_after_var.get()
        validate_equals_before_checked = self.validation_equals_before_var.get()
        validation_name = self.equals_validation_name_entry.get()
        variable1 = self.equals_variable1_value_entry.get()
        variable2 = self.equals_variable2_value_entry.get()
        validation_pass_msg = self.equals_pass_msg_entry.get()
        validation_fail_msg = self.equals_fail_msg_entry.get()
        now = int(time.time() * 1000)
        conn([["validation-equals", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_equals_after_checked, validate_equals_before_checked, if_condition, if_else_condition]])
        self.validation_equals_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"validate-equals: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then equals starts: {validation_name}")
        else:
            self.update_steps(f"if equals starts: {validation_name}")

    def validate_not_equals(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_not_equals_after_checked = self.validation_not_equals_after_var.get()
        validate_not_equals_before_checked = self.validation_not_equals_before_var.get()
        validation_name = self.not_equals_validation_name_entry.get()
        variable1 = self.not_equals_variable1_value_entry.get()
        variable2 = self.not_equals_variable2_value_entry.get()
        validation_pass_msg = self.not_equals_pass_msg_entry.get()
        validation_fail_msg = self.not_equals_fail_msg_entry.get()
        now = int(time.time() * 1000)
        conn([["validation-not-equals", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_not_equals_after_checked, validate_not_equals_before_checked, if_condition, if_else_condition]])
        self.validation_not_equals_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"validate-not-equals: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then not-equals starts: {validation_name}")
        else:
            self.update_steps(f"if not-equals starts: {validation_name}")

    def validate_num_equals(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_num_equals_after_checked = self.validation_num_equals_after_var.get()
        validate_num_equals_before_checked = self.validation_num_equals_before_var.get()
        validation_name = self.num_equals_validation_name_entry.get()
        variable1 = self.num_equals_variable1_value_entry.get()
        variable2 = self.num_equals_variable2_value_entry.get()
        validation_pass_msg = self.num_equals_pass_msg_entry.get()
        validation_fail_msg = self.num_equals_fail_msg_entry.get()
        now = int(time.time() * 1000)
        conn([["validation-num-equals", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_num_equals_after_checked, validate_num_equals_before_checked, if_condition, if_else_condition]])
        self.validation_num_equals_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"validate-num-equals: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then num-equals starts: {validation_name}")
        else:
            self.update_steps(f"if num-equals starts: {validation_name}")

    def validate_num_not_equals(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_num_not_equals_after_checked = self.validation_num_not_equals_after_var.get()
        validate_num_not_equals_before_checked = self.validation_num_not_equals_before_var.get()
        validation_name = self.num_not_equals_validation_name_entry.get()
        variable1 = self.num_not_equals_variable1_value_entry.get()
        variable2 = self.num_not_equals_variable2_value_entry.get()
        validation_pass_msg = self.num_not_equals_pass_msg_entry.get()
        validation_fail_msg = self.num_not_equals_fail_msg_entry.get()
        now = int(time.time() * 1000)
        conn([["validation-num-not-equals", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_num_not_equals_after_checked, validate_num_not_equals_before_checked, if_condition, if_else_condition]])
        self.validation_num_not_equals_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"validate-num-not-equals: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then num-not-equals starts: {validation_name}")
        else:
            self.update_steps(f"if num-not-equals starts: {validation_name}")

    def validate_contains(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_contains_after_checked = self.validation_contains_after_var.get()
        validate_contains_before_checked = self.validation_contains_before_var.get()
        validation_name = self.contains_validation_name_entry.get()
        variable1 = self.contains_variable1_value_entry.get()
        variable2 = self.contains_variable2_value_entry.get()
        validation_pass_msg = self.contains_pass_msg_entry.get()
        validation_fail_msg = self.contains_fail_msg_entry.get()
        now = int(time.time() * 1000)
        conn([["validation-contains", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_contains_after_checked, validate_contains_before_checked, if_condition, if_else_condition]])
        self.validation_contains_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"validate-contains: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then contains starts: {validation_name}")
        else:
            self.update_steps(f"if contains starts: {validation_name}")

    def validate_num_le(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_num_le_after_checked = self.validation_num_le_after_var.get()
        validate_num_le_before_checked = self.validation_num_le_before_var.get()
        validation_name = self.num_le_validation_name_entry.get()
        variable1 = self.num_le_variable1_value_entry.get()
        variable2 = self.num_le_variable2_value_entry.get()
        validation_pass_msg = self.num_le_pass_msg_entry.get()
        validation_fail_msg = self.num_le_fail_msg_entry.get()
        now = int(time.time() * 1000)
        conn([["validation-num-le", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_num_le_after_checked, validate_num_le_before_checked, if_condition, if_else_condition]])
        self.validation_num_le_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"validate-num-le: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then num-le starts: {validation_name}")
        else:
            self.update_steps(f"if num-le starts: {validation_name}")

    def validate_num_ge(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_num_ge_after_checked = self.validation_num_ge_after_var.get()
        validate_num_ge_before_checked = self.validation_num_ge_before_var.get()
        validation_name = self.num_ge_validation_name_entry.get()
        variable1 = self.num_ge_variable1_value_entry.get()
        variable2 = self.num_ge_variable2_value_entry.get()
        validation_pass_msg = self.num_ge_pass_msg_entry.get()
        validation_fail_msg = self.num_ge_fail_msg_entry.get()
        now = int(time.time() * 1000)
        conn([["validation-num-ge", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_num_ge_after_checked, validate_num_ge_before_checked, if_condition, if_else_condition]])
        self.validation_num_ge_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"validate-num-ge: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then num-ge starts: {validation_name}")
        else:
            self.update_steps(f"if num-ge starts: {validation_name}")

    def validate_starts_with(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_starts_with_after_checked = self.validation_starts_with_after_var.get()
        validate_starts_with_before_checked = self.validation_starts_with_before_var.get()
        validation_name = self.starts_with_validation_name_entry.get()
        variable1 = self.starts_with_variable1_value_entry.get()
        variable2 = self.starts_with_variable2_value_entry.get()
        validation_pass_msg = self.starts_with_pass_msg_entry.get()
        validation_fail_msg = self.starts_with_fail_msg_entry.get()
        now = int(time.time() * 1000)
        conn([["validation-starts-with", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_starts_with_after_checked, validate_starts_with_before_checked, if_condition, if_else_condition]])
        self.validation_starts_with_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"validate-starts-with: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then starts-with starts: {validation_name}")
        else:
            self.update_steps(f"if starts-with starts: {validation_name}")

    def validate_ends_with(self):
        if_condition = False
        if_else_condition = False
        if self.dropdown_var.get() == "if-condition":
            if_condition = True
            self.end_if_button.pack(side=tk.LEFT, padx=5)
        elif self.dropdown_var.get() == "if-else-condition":
            if_condition = True
            if_else_condition = True
            self.end_if_then_button.pack(side=tk.LEFT, padx=5)
        validate_ends_with_after_checked = self.validation_ends_with_after_var.get()
        validate_ends_with_before_checked = self.validation_ends_with_before_var.get()
        validation_name = self.ends_with_validation_name_entry.get()
        variable1 = self.ends_with_variable1_value_entry.get()
        variable2 = self.ends_with_variable2_value_entry.get()
        validation_pass_msg = self.ends_with_pass_msg_entry.get()
        validation_fail_msg = self.ends_with_fail_msg_entry.get()
        now = int(time.time() * 1000)
        conn([["validation-ends-with", now, validation_name, variable1, variable2, validation_pass_msg, validation_fail_msg, validate_ends_with_after_checked, validate_ends_with_before_checked, if_condition, if_else_condition]])
        self.validation_ends_with_frame.pack_forget()
        if self.dropdown_var.get() == "validation":
            self.update_steps(f"validate-ends-with: {validation_name}")
        elif self.dropdown_var.get() == "if-else-condition":
            self.update_steps(f"if then ends-with starts: {validation_name}")
        else:
            self.update_steps(f"if ends-with starts: {validation_name}")

    def variable_value(self):
        variable_value_after_checked = self.variable_value_after_var.get()
        variable_value_before_checked = self.variable_value_before_var.get()
        variable_name = self.variable_value_name_entry.get()
        variable_value = self.variable_value_entry.get()
        now = int(time.time() * 1000)
        conn([["variable-value", now, variable_name, variable_value, variable_value_after_checked, variable_value_before_checked]])
        self.variable_value_frame.pack_forget()
        self.update_steps(f"variable-value: {variable_name}")

    def start_loop(self):
        startIndex = self.start_index_entry.get()
        if startIndex == "Enter start index(optional - default to 1)" or not startIndex:
            startIndex = 1
        lastIndex = self.last_index_entry.get()
        increment = self.increment_entry.get()
        if increment == "Enter increment(optional - deafult to 1)" or not increment:
            increment = 1
        counterVar = self.counterVar_entry.get()
        if counterVar == "Assign counter(optional - default to i)" or not counterVar:
            counterVar = "i"
        now = int(time.time() * 1000)
        conn([["start-loop", now, startIndex, lastIndex, increment, counterVar]])
        self.loop_frame.pack_forget()
        self.end_loop_create(counterVar)
        self.update_steps(f"start-loop: Counter var -{counterVar}")

    def alert_accept(self):
        now = int(time.time() * 1000)
        conn([["alert-accept", now]])
        self.alert_accept_frame.pack_forget()
        self.update_steps("Alert Accept")

    def alert_cancel(self):
        now = int(time.time() * 1000)
        conn([["alert-cancel", now]])
        self.alert_cancel_frame.pack_forget()
        self.update_steps("Alert Cancel")

    def alert_getText(self):
        keyName = self.keyName_entry.get()
        now = int(time.time() * 1000)
        conn([["alert-getText", now, keyName]])
        self.alert_getText_frame.pack_forget()
        self.update_steps(f"Alert Get Text in : {keyName}")

    def alert_input(self):
        value = self.value_entry.get()
        now = int(time.time() * 1000)
        conn([["alert-input", now, value]])
        self.alert_input_frame.pack_forget()
        self.update_steps(f"Alert Input : {value}")

    def alert_authenticate(self):
        user = self.user_entry.get()
        pwd = self.pwd_entry.get()
        now = int(time.time() * 1000)
        conn([["alert-authenticate", now, user, pwd]])
        self.alert_authenticate_frame.pack_forget()
        self.update_steps(f"Alert Authenticate as user : {user}")

    def close_browser(self):
        now = int(time.time() * 1000)
        conn([["close-browser", now]])
        self.close_browser_frame.pack_forget()
        self.update_steps("Close Browser")
        self.stop_recording()
        close_browser_driver()

    def refresh_browser(self):
        now = int(time.time() * 1000)
        conn([["refresh-browser", now]])
        self.refresh_browser_frame.pack_forget()
        self.update_steps("Refresh Browser")
        refresh_browser_driver()

    def insert_step(self):
        custom_step = self.custom_step_entry.get()
        now = int(time.time() * 1000)
        conn([["custom-step", now, custom_step]])
        self.update_steps(f"Custom step enetred : {custom_step}")
        self.insert_custom_frame.pack_forget()


    def copy_to_clipboard(self, position):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.xpath_label.cget("text"))
        self.root.update()
        x, y = position.x_root, position.y_root
        FadingMessage(self.root, "Copied to clipboard!", x, y)


    def update_steps(self, step):
        self.executed_steps.insert(tk.END, step)
        self.executed_steps.see(tk.END)

    def delete_last_step_from_executed_steps(self):
        if self.executed_steps.size() > 0:  # Check if the Listbox is not empty
            last = 1
            last_item = self.get_last_item(last)
            last_index = self.executed_steps.size() - 1  # Index of the last item
            while last_item is not None and (last_item == "Pause Recording" or last_item == "Resume Recording"):   
                last_index -= 1
                last += 1
                last_item = self.get_last_item(last)
            self.executed_steps.delete(last_index)  # Delete the last item

    def get_last_item(self, last):
        if self.executed_steps.size() > 0:  # Check if the Listbox is not empty
            last_index = self.executed_steps.size() - last  # Index of the last item
            return self.executed_steps.get(last_index)  # Get the last item
        else:
            return None  # Return None if the Listbox is empty
    
    def exit(self):
        reset_event_queue()
        self.executed_steps.delete(0, tk.END)
        self.stop_button.pack_forget()
        self.pause_resume_button.pack_forget()
        self.dropdown_frame.pack_forget()
        self.delete_button.pack_forget()
        self.update_steps("Stop Recording")
        self.disable_dropdown_options()
        self.end_if_button.pack_forget()
        self.end_if_then_button.pack_forget()
        self.end_else_button.pack_forget()
        self.end_loop_button.pack_forget()
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.controller.show_activity_manager()

    def run(self):
        self.root.deiconify()

    def withdraw(self):
        self.root.withdraw()

if __name__ == "__main__":
    RecorderInstance = Recorder()
    RecorderInstance.run()

