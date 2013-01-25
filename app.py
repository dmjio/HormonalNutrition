import os
from flask import Flask, render_template, request, url_for
from flask.ext.heroku import Heroku
from flask.ext.mail import Mail, Message
import stripe

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__)
heroku = Heroku(app)
mail = Mail(app)

#sending mail
def sendmail(title, fr, to, body):
    msg = Message(title,sender=fr,recipients=[to])
    msg.body = body
    mail.send(msg)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/')
def index():
    return render_template('home.html', key=stripe_keys['publishable_key'])

@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents
    amount = 2500

    customer = stripe.Customer.create(
        email='customer@example.com',
        card=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Hormonal Nutrition eBook Purchase'
    )

    send_mail('Receipt from HormonalNutrition.com',
              'postmaster@hormonalnutrition.mailgun.org', 
              'djohnson.m@gmail.com', 
              'Thank you!')


    return render_template('charge.html', amount=amount)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
