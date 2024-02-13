from flask import Flask, request, jsonify
from flask_cors import CORS
from waitress import serve
from Recorder_IDE import Recorder
import threading

app = Flask(__name__)
CORS(app)

# In-memory storage for simplicity; consider a database for production use
events = []

@app.route('/save', methods=['POST'])
def save_events():
    print("Sending request to retrieve data to be saved ...")
    data = request.json
    print(f"\nThe recieved data is : {data}\n")
    events.extend(data)
    print(f"\n\n The saved events are : {events} \n\n")
    return jsonify({"status": "success"})


@app.route('/delete-last', methods=['POST'])
def delete_last_event():
    if events:  # Check if there are events in the list
        deleted_event = events.pop()  # Remove the last event
        print(f"\nDeleted event: {deleted_event}\n")
        print(f"\n\n The saved events are : {events} \n\n")
        # Return the status and the deleted event
        return jsonify({"status": "success", "deleted_event": deleted_event})
    else:
        # If there are no events to delete
        print("No events to delete")
        return jsonify({"status": "failure", "message": "No events to delete"})
    
    
@app.route('/delete-backspace', methods=['POST'])
def backspace_event():
    try:
        data = request.json
        xpath = data.get('xpath')
        if events and (events[-1][0] == "input" and events[-1][2] == xpath):  # Check if there are events in the list
            deleted_event = events.pop()  # Remove the last event
            print(f"\nDeleted event: {deleted_event}\n")
            print(f"\n\n The saved events are : {events} \n\n")
            # Return the status and the deleted event
            return jsonify({"status": "success", "deleted_event": deleted_event})
        else:
            print(f"Not backspacing with the same xpath : {events[-1][2]},  with the previous event not being input : {events[-1][0]}")
            return jsonify({"status": "failure", "message": "No events to delete"})
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"status": "error", "message": "Server error"}), 500
    


@app.route('/reset', methods=['POST'])
def reset_events():
    events.clear()  # Clear the events list
    print("\nAll events have been reset\n")
    return jsonify({"status": "success", "message": "All events have been reset"})


@app.route('/retrieve', methods=['GET'])
def retrieve_events():
    return jsonify(events)


def run_flask_app():
    print("The flask application has been successfully started!")
    serve(app, host='0.0.0.0', port=9005)

def start_flask_app():
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()
    

    
    
    

