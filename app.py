import os
from flask import Flask, render_template, request, url_for, jsonify, redirect
from flask.ext.heroku import Heroku
from datetime import datetime
from flask.ext.mongoengine import MongoEngine
from flask.ext.mail import Mail, Message
from flask_sslify import SSLify
import stripe

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__)
sslify = SSLify(app)
heroku = Heroku(app)

#need to explicity define the mail gun smtp port since flask_heroku
#leaves this out

app.config["MAIL_SERVER"] = os.environ["MAILGUN_SMTP_SERVER"]
app.config['MAIL_PORT'] = os.environ["MAILGUN_SMTP_PORT"]
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ["MAILGUN_SMTP_LOGIN"]
app.config['MAIL_PASSWORD'] = os.environ["MAILGUN_SMTP_PASSWORD"]

mail = Mail(app)

app.config["MONGODB_USERNAME"] = app.config['MONGODB_USER'] #flask_heroku naming convention mismatch, with MongoEngine this time
db = MongoEngine(app)

if not 'Production' in os.environ:
    app.debug = True
    from flask_cake import Cake
    cake = Cake(app, ["build"]) #this converts our coffeescript to javascript
    from flask.ext.less import LESS
    less = LESS(app)
else:
    app.debug = False

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

@app.route('/validate/', methods=['GET'])
def validate():
    email = request.query_string
    data = []
    for i in Customers.objects:
        if i.email == email:
            return jsonify(success=False)
    return jsonify(success=True)


@app.route('/checkout/')
def checkout():
    return render_template('checkout.html', key=stripe_keys['publishable_key'])

@app.route('/')
def index():
    print request.url, ": URL"
    return render_template('home.html')

@app.route('/download/<email>')
def send_pdf(email):
    for c in Customers.objects:
        if c.email == email and c.downloads > 0:
            print c.email
            print c.downloads
            c.downloads = c.downloads - 1
            c.save()
            return app.send_static_file('lec.pdf')
    return render_template('nomas.html')

@app.route('/charge/', methods=['POST'])
def charge():
    # Amount in cents
    amount = 2500
    email = request.form['email']
    customer = stripe.Customer.create(
        email=email,
        card=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Hormonal Nutrition eBook Purchase'
    )

    #mongo goes here...
    customer = Customers(created_at=datetime.now(),email=email,downloads=3)
    customer.save()

    #flask mail...
    msg = Message("Thank you %s for your purchase!" % email,
                  sender=os.environ["MAILGUN_SMTP_LOGIN"],
                  recipients=[email])

    msg.body =  "Thank you! You have 3 attempts to download your ebook." + url_for('send_pdf', email=email.replace('%40','@'), _external=True)

    mail.send(msg)
    return render_template('charge.html', amount=amount)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
