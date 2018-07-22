from flask import Flask, render_template
import dataset
app = Flask(__name__)

@app.route('/')
def show_posts():
    # Use dataset to show all posts+comments
    return "Placeholder"

if __name__ == "__main__":
    app.run()