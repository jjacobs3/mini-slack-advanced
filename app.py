from flask import Flask, render_template
import dataset
app = Flask(__name__)

db_url = "postgres://trdjvouxhqrpjj:832df4be295096403707081e0cd7a2f2545985a0c0571f2622b36331a0b516f5@ec2-54-204-18-53.compute-1.amazonaws.com:5432/ddkpks3g8s3pei"
db = dataset.connect(db_url)

@app.route('/')
def show_posts():
    # Use dataset to show all posts+comments
    return "Placeholder"

if __name__ == "__main__":
    app.run()