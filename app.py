import os
from flask import Flask, render_template, request, url_for
from flask.ext.heroku import Heroku
from smtplib import SMTP
from datetime import datetime
from flask.ext.mongoengine import MongoEngine
import stripe

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__)
heroku = Heroku(app)
app.config["MONGODB_USERNAME"] = app.config['MONGODB_USER']
db = MongoEngine(app)

class Customers(db.Document):
    created_at = db.DateTimeField(default=datetime.now(), required=True)
    email = db.StringField(max_length=255, required=True)
    downloads = db.IntField()

    def get_absolute_url(self):
        return url_for('customer', kwargs={"created_at": self.created_at})

    def __unicode__(self):
        return self.email

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at'],
        'ordering': ['-created_at']
    }

#sending mail
def send_email(msg,email):
    smtp = SMTP(os.environ['MAILGUN_SMTP_SERVER'], os.environ['MAILGUN_SMTP_PORT'])
    smtp.login(os.environ['MAILGUN_SMTP_LOGIN'], os.environ['MAILGUN_SMTP_PASSWORD'])
    smtp.sendmail(os.environ['MAILGUN_SMTP_LOGIN'], email, msg)
    smtp.quit()

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/')
def index(): return render_template('home.html', key=stripe_keys['publishable_key'])

@app.route('/download/<email>')
def send_pdf(email):
    """Send your static text file."""
    for c in Customers.objects:
        if c.email == email and c.downloads > 0:
            print c.email
            print c.downloads
            c.downloads = c.downloads - 1
            c.save()
            return app.send_static_file('lec.pdf')  	
    return render_template('nomas.html')

@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents
    amount = 2500
    customer = stripe.Customer.create(
        email=request.form['email'],
        card=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Hormonal Nutrition eBook Purchase'
    )
    #mongo goes here...
    customer = Customers(created_at=datetime.now(),email=request.form['email'],downloads=3)
    customer.save()

    send_email("Thanks! You have 3 attempts to download your ebook. " + url_for('send_pdf', email=request.form['email'].replace('%40','@'), _external=True), request.form['email'])
    return render_template('charge.html', amount=amount)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
