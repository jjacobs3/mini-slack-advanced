from flask import Flask, render_template, request
import dataset
app = Flask(__name__)

db_url = "postgres://trdjvouxhqrpjj:832df4be295096403707081e0cd7a2f2545985a0c0571f2622b36331a0b516f5@ec2-54-204-18-53.compute-1.amazonaws.com:5432/ddkpks3g8s3pei"
db = dataset.connect(db_url)

# Stores the list of users
user_table = db.create_table('users')
# Stores the list of messages
message_table = db.create_table('messages')
# Stores a list of (message_id, recipient_id) pairs, where message_id is the
# id in messages table and recipient_id is id in user_table. THIS IS WHAT
# ALLOWS A MESSAGE TO BE SENT TO MULTIPLE USERS
link_table = db.create_table('links')

@app.route('/')
def show_db():
    # Use dataset to show all db contents
    all_users = list(user_table.find())
    all_messages = list(message_table.find())
    all_links = list(link_table.find())
    return "Users:<br>" + str(all_users) + "<br>Messages:<br>" + str(all_messages) + "<br>Links:<br>" + str(all_links)

#############################
### Code for adding users ###
#############################

@app.route('/userForm')
def user_form():
    return render_template('user_form.jinja')

@app.route('/handleUserForm', methods=["GET","POST"])
def handle_user_form():
    print("handleUserForm()")
    # Get the name they typed in
    name = request.form["username"]
    # And call our add_user() function!
    add_user(name)

def add_user(name):
    if user_table.find_one(name=name):
        return "User already exists!"
    else:
        user_table.insert(dict(name=name))
        return "User added!"

# Show a list of all users
@app.route('/showUsers')
def show_users():
    all_user_data = user_table.find()
    all_user_names = []
    for user_data in all_user_data:
        # Get the user's name
        user_name = user_data["name"]
        all_user_names.append(user_name)
    return render_template('user_list.jinja', user_list=all_user_names)

############################################
### Code for adding and showing messages ###
############################################

# Give the visitor a message form
@app.route('/messageForm')
def message_form():
    return render_template("message_form.jinja")

# Parse the entered data and then call add_message()
@app.route('/handleMessageForm')
def handle_message_form():
    # Get the text they entered in the form
    from_name = request.form["fromname"]
    to_names = request.form["tonames"]
    message_text = request.form["messagetext"]
    # Now just call our add_message function!
    add_message(message_text, from_name, to_names)

# Add a message to the db
def add_message(text, sender_name, recipient_names):
    # recipients is a COMMA-SEPARATED list of users, so we can get them into a
    # list using .split(",")
    recipient_name_list = recipient_names.split(",")
    # Remember that we need to update the message table AND the links table
    if message_table.find_one(text=text):
        return "Message already exists!"
    else:
        # Add to message table
        # Find the id of the sender
        sender_data = user_table.find_one(name=sender_name)
        sender_id = sender_data["id"]
        message_id = message_table.insert(dict(text=text, sender_id=sender_id))
        # And to link table
        for recipient_name in recipient_name_list:
            # Get the recipient's id
            recipient_data = user_table.find_one(name=recipient_name)
            if recipient_data:
                recipient_id = recipient_data["id"]
                link_table.insert(dict(message_id=message_id, recipient_id=recipient_id))
            else:
                return "Recipient " + recipient_name + " not found!!"

# Show a list of all messages
@app.route('/showMessages')
def show_messages():
    all_message_data = []
    all_messages = list(message_table.find())
    for message in all_messages:
        message_text = message["text"]
        message_sender_id = message["sender_id"]
        # Let's get the sender's name
        message_sender_data = user_table.find_one(id=message_sender_id)
        message_sender_name = message_sender_data["name"]
        # We need to get the message's id so we can find all the links
        message_id = message["id"]
        # Now find all links with this id
        all_links = link_table.find(message_id=message_id)
        # And finally, find all the *users* for these links
        all_recipients = []
        for link in all_links:
            recipient_id = link["recipient_id"]
            recipient_data = user_table.find_one(id=recipient_id)
            recipient_name = recipient_data["name"]
            all_recipients.append(recipient_name)
        # Combine everything together!!
        # This just takes all the recipients and puts a comma between them
        recipients_str = ",".join(all_recipients)
        message_data = dict(text=message_text, sender_name=message_sender_name, recipients=recipients_str)
        all_message_data.append(message_data)
    # And send all the message data to the jinja template
    print(all_message_data)
    return render_template('message_list.jinja', message_list=all_message_data)

###################################
### Code for adding sample data ###
###################################

@app.route('/setupHard')
def setup_hard():
    # THIS IS THE HARD, MANUAL WAY TO DO THE SETUP! THE EASY WAY IS IN setup_easy()
    # First we empty the tables, in case there's other stuff in it already
    user_table.delete()
    message_table.delete()
    link_table.delete()
    # Make 3 users
    jeff_id = user_table.insert(dict(name="Jeff"))
    tahseen_id = user_table.insert(dict(name="Tahseen"))
    sadek_id = user_table.insert(dict(name="Sadek"))
    # Make a message from Jeff to Tahseen and Sadek
    message_id = message_table.insert(dict(text="Hello friends!", sender_id=jeff_id))
    # Now let the database know that this message is from Jeff TO BOTH TAHSEEN
    # AND SADEK
    # We have the message id AND the recipient ids, so we can make the links!
    link_table.insert(dict(message_id=message_id, recipient_id=tahseen_id))
    link_table.insert(dict(message_id=message_id, recipient_id=sadek_id))
    # So now the *first* entry in link_table tells our app that the message
    # should go to Tahseen, and the *second* entry tells our app that the message
    # should (also) go to Sadek
    return "DB set up!"

@app.route('/setup')
def setup_easy():
    # THIS IS THE EASY WAY TO DO THE SETUP! Just use the add_message() and
    # addUser() functions we wrote above :)
    user_table.delete()
    message_table.delete()
    link_table.delete()
    # Add users
    add_user("Jeff")
    add_user("Tahseen")
    add_user("Sadek")
    # Add messages
    add_message("Hello friends!", "Jeff", "Tahseen,Sadek")
    add_message("I'm shutting down the camp", "Sadek", "Jeff,Tahseen")
    return "DB set up!"

if __name__ == "__main__":
    app.run()