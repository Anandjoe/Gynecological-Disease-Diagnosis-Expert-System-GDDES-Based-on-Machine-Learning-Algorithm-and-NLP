from flask import Flask,render_template, url_for, redirect, request, session
import mysql.connector,os ,re , joblib
import pandas as pd
import speech_recognition as sr
from googletrans import Translator
import threading
from gtts import gTTS

# Import libraries
import nltk
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
from nltk.stem import PorterStemmer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
df = pd.read_csv('gynecological_reviews.csv')


app = Flask(__name__)
app.secret_key = 'admin'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306",
    database='db'
)

mycursor = mydb.cursor()


def executionquery(query,values):
    mycursor.execute(query,values)
    mydb.commit()
    return

def retrivequery1(query,values):
    mycursor.execute(query,values)
    data = mycursor.fetchall()
    return data

def retrivequery2(query):
    mycursor.execute(query)
    data = mycursor.fetchall()
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        c_password = request.form['c_password']
        if password == c_password:
            query = "SELECT UPPER(email) FROM users"
            email_data = retrivequery2(query)
            email_data_list = []
            for i in email_data:
                email_data_list.append(i[0])
            if email.upper() not in email_data_list:
                query = "INSERT INTO users (name,email, password) VALUES ( %s, %s, %s)"
                values = (name,email, password)
                executionquery(query, values)
                # Store the registered user data in session
                session['user_email'] = email
                session['user_name'] = request.form['name']
                return render_template('login.html', message="Successfully Registered!")
            return render_template('register.html', message="This email ID is already exists!")
        return render_template('register.html', message="Conform password is not match!")
    return render_template('register.html')

@app.route('/login',methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = []
        for i in email_data:
            email_data_list.append(i[0])

        if email.upper() in email_data_list:
            query = "SELECT UPPER(password) FROM users WHERE email = %s"
            values = (email,)
            password__data = retrivequery1(query, values)
            if password.upper() == password__data[0][0]:
                global user_email
                user_email = email
                session['user_email'] = user_email
                return render_template('home.html')
            return render_template('login.html', message= "Invalid Password!!")
        return render_template('login.html', message= "This email ID does not exist!")
    return render_template('login.html')

@app.route('/adlogin', methods=["GET", "POST"])
def adlogin():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        if email == "admin@gmail.com":
            if password == "admin":
                # return redirect("/admin",)
                return render_template('admin.html', message= "  welcome to  Admin!!")
            return render_template('adlogin.html', message= "Invalid Password for Admin!!")
        return render_template('adlogin.html', message= "This email ID does not exist!")
    return render_template('adlogin.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')



@app.route('/view_data')
def view_data():
    email = session.get('user_email')
    name = session.get('user_name')
    print(11111111, email)
    print(22222222222, name)
    # disease = session.get('result')
    query = "SELECT name, email, disease FROM prediction1 WHERE email = %s"
    values = (email, ) 
    predictions_data = retrivequery1(query, values)
    print()
    print(predictions_data)
    return render_template('view_data.html', data = predictions_data)
@app.route('/view_data2')
def view_data2():
    email = session.get('user_email')
    name = session.get('user_name')
    print(11111111, email)
    print(22222222222, name)
    # disease = session.get('result')
    query = "SELECT name, email, disease FROM prediction2 WHERE email = %s"
    values = (email, ) 
    predictions_data = retrivequery1(query, values)
    print()
    print(predictions_data)
    return render_template('view_data2.html', data = predictions_data)


@app.route('/home')
def home():
    return render_template('home.html')



@app.route('/prediction', methods = ['GET', "POST"])
def prediction():
    result = None  # Default value for result
    disease_reasons = ""
    diet = []

    if request.method == "POST":
        # Collect form data
        Nausea = int(request.form['Nausea'])
        Lumber = int(request.form['Lumber'])
        Urine = int(request.form['Urine'])
        Micturition = int(request.form['Micturition'])
        Urethra = int(request.form['Urethra'])
        Itch = int(request.form['Itch'])
        Swelling = int(request.form['Swelling'])
        Inflammation = request.form['Inflammation']
        Nephritis = int(request.form['Nephritis'])
        Irregular = int(request.form['Irregular'])
        No_Periods = int(request.form['No_Periods'])
        Excessive_Hair_Growth = int(request.form['Excessive_Hair_Growth'])
        Buttocks = int(request.form['Buttocks'])
        Belly_Fat = int(request.form['Belly_Fat'])
        Hair_Loss = int(request.form['Hair_Loss'])
        Acne = int(request.form['Acne'])

        # Prepare input data for prediction
        lee = [[Nausea, Lumber, Urine, Micturition, Urethra, Itch, Swelling, Inflammation, Nephritis, Irregular,
                 No_Periods, Excessive_Hair_Growth, Buttocks, Belly_Fat, Hair_Loss, Acne]]

        # Load model
        model = joblib.load("random_forest_model.joblib")
        predictions = model.predict(lee)

        # Determine result and corresponding disease reasons and diet
        if predictions == 0:
            result = 'Healthy'
            disease_reasons = "No symptoms of PCOS or UTI detected. The patient is healthy."
            diet = [
                ["Monday", "Oats with fruits", "Grilled chicken with veggies", "Salmon with quinoa"],
                ["Tuesday", "Avocado toast", "Salad with chicken", "Grilled veggies with brown rice"],
                ["Wednesday", "Greek yogurt with honey", "Grilled fish with salad", "Tofu stir fry"],
                ["Thursday", "Smoothie bowl", "Chicken and rice", "Steamed vegetables with beans"],
                ["Friday", "Egg white omelette", "Vegetable sandwich", "Grilled chicken with veggies"],
                ["Saturday", "Porridge", "Rice with dal", "Grilled fish with vegetables"],
                ["Sunday", "Whole wheat toast with avocado", "Veggie wrap", "Baked chicken with steamed veggies"]
            ]
        elif predictions == 1:
            result = 'PCOS'
            disease_reasons = "PCOS is a hormonal disorder that affects women's reproductive systems. Common symptoms include irregular periods, excessive hair growth, and ovarian cysts."
            diet = [
                ["Monday", "3 Idly, 1/2 cup Sambar", "3 roti, 1/2 cup mixed veg salad, Fish curry", "1 cup green gram sprouts", "2 roti / chapati, 1/2 cup Tomato subji"],
                ["Tuesday", "2 slices of brown bread, 1 slice low-fat cheese", "2 Chapati, 1/2 cup Ladies finger subji", "1 Banana (small), 1 cup green tea", "1 cup Broken wheat upma"],
                ["Wednesday", "2 methi Parata, 1/2 cup onion raita", "1 cup veg pulao, 1/2 cup Soya Chunk curry, Butter Milk", "1 cup green tea", "3 wheat dosa, 1 cup any subji"],
                ["Thursday", "1 cup oats Upma, 1/2 cup low-fat milk", "1 cup rice, 1 cup kidney beans", "1 cup yoghurt with raw vegetables (carrots/cucumber)", "Mixed vegetable soup, 1-2 cups"],
                ["Friday", "Poha 1 cup, 1/2 sliced cucumber", "1/2 cup rice + 2 medium Soya Chunk curry, 1/2 cup Ladies finger subji", "1 cup boiled black channa + 1 cup tea", "2 Roti / chapati + 1/2 cup mixed veg curry"],
                ["Saturday", "Mixed vegetable upma 1 cup", "1 cup rice, 1/2 cup Palak subji + 1 cup milk", "1 cup vegetable upma, 1 cup milk", "1-2 cups chicken clear soup or any vegetable soup"],
                ["Sunday", "1 Dosa, 1 cup low-fat milk", "3 roti, 1 cup mixed curry, 1 cup veg curry", "1/2 cup boiled ground nuts, 1 cup tea", "1 cup mixed veg soup"]
            ]
        else:
            result = 'UTI'
            disease_reasons = "UTI (Urinary Tract Infection) is an infection in the urinary system. Symptoms include frequent urination, burning sensation, and cloudy urine."
            diet = [
                ["Monday", "Oats with bananas", "Chicken soup", "Steamed vegetables with fish"],
                ["Tuesday", "Whole wheat toast with avocado", "Grilled chicken with veggies", "Rice and lentils"],
                ["Wednesday", "Greek yogurt with berries", "Salad with chicken", "Baked salmon with quinoa"],
                ["Thursday", "Smoothie with spinach", "Rice with dal", "Grilled vegetables with tofu"],
                ["Friday", "Boiled eggs with avocado", "Grilled fish with veggies", "Vegetable soup"],
                ["Saturday", "Chia pudding", "Vegetable stir fry with rice", "Baked chicken with steamed veggies"],
                ["Sunday", "Fruit smoothie", "Brown rice with beans", "Grilled chicken with salad"]
            ]

        # Send email with the result
        to_email = session['user_email']
        send_email(to_email, result)

        # Insert result into the 'prediction1' table
        name = session.get('user_name')  # Get the name from session
        email = session.get('user_email')
        session['result'] = result
        query = "INSERT INTO prediction1 (name, email, disease) VALUES (%s, %s, %s)"
        values = (name, email, result)
        executionquery(query, values)

    # Render the template with the results
    return render_template('prediction.html', result=result, disease_reasons=disease_reasons, diet=diet)

######################################################################

# Function to send email
def send_email(to_email, result):
    # Email setup
    from_email = ""  # Replace with your email address
    from_password = ""  # Replace with your email password or app-specific password
    
    subject = "Prediction Result"
    body = f"The result of your  prediction is: {result}"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Setup the SMTP server and send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Use TLS
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
####################################################################
@app.route('/voice', methods = ["GET", "POST"])
def voice():
    my_text = None
    translated_text = None
    if request.method == "POST":
        language = request.form["language"]

        # Dictionary of Indian languages
        indian_languages = {
            'hi': 'Hindi',
            'bn': 'Bengali',
            'ta': 'Tamil',
            'te': 'Telugu',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'gu': 'Gujarati',
            'mr': 'Marathi',
            'or': 'Odia',
            'pa': 'Punjabi',
            'as': 'Assamese',
            'sd': 'Sindhi',
            'ur': 'Urdu',
            'ne': 'Nepali'
        }

        # Print available languages for the user to choose
        print("Available Indian languages:")
        for code, lang in indian_languages.items():
            print(f"{code}: {lang}")

        # Get user input for the language code
        language_code = language.strip()

        # Validate user input
        if language_code not in indian_languages:
            print("Invalid language code.")
            exit()

        # Create a speech recognition object
        r = sr.Recognizer()

        # Use the microphone as the audio source
        with sr.Microphone() as source:
            print(f"Please say something in {indian_languages[language_code]}:")
            audio = r.listen(source)

        # Save the audio file
        with open("input.wav", "wb") as f:
            f.write(audio.get_wav_data())

        # Recognize the speech
        try:
            my_text = r.recognize_google(audio, language=f"{language_code}-IN")
            print("You said: " + my_text)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            exit()

        # Translate the text to English
        translator = Translator()
        translated_text = translator.translate(my_text, dest="en").text
        print("Translated text To English : " + translated_text)

        # Convert the translated text to speech
        # output = gTTS(text=translated_text, lang="en", slow=True)
        # output.save("static/saves_audio/output.mp3")
        # os.system("start output.mp3")
        



        # For Reviews Comparision

        def preprocess_text(text):
            """
            Preprocesses the input text by removing non-alphabetic characters,
            converting to lowercase, tokenizing, stemming, and removing stopwords.
            
            Parameters:
            text (str): The input text to preprocess.
            
            Returns:
            str: The processed text.
            """
            ps = PorterStemmer()
            stop_words = set(stopwords.words('english'))
            
            # Remove non-alphabetic characters
            text = re.sub('[^a-zA-Z]', ' ', text)
            
            # Convert to lowercase
            text = text.lower()
            
            # Tokenize the text
            words = word_tokenize(text)
            
            # Remove stopwords and apply stemming
            processed_words = [ps.stem(word) for word in words if word not in stop_words]
            
            # Join the processed words back into a string
            processed_text = ' '.join(processed_words)
            
            return processed_text

        def find_most_similar_review(input_text, df):
            """
            Finds the review most similar to the input text based on cosine similarity.
            
            Parameters:
            input_text (str): The input text to compare with the reviews.
            df (pd.DataFrame): DataFrame containing a 'clean_review' column with reviews.
            
            Returns:
            str: The most similar review from the dataframe.
            """
            # Preprocess the input text
            input_text_processed = preprocess_text(input_text)
            
            # Preprocess the reviews in the dataframe
            df['processed_review'] = df['Review'].apply(preprocess_text)
            
            # Create a list of processed reviews
            reviews = df['processed_review'].tolist()
            
            # Append the input text to the list of reviews
            reviews.append(input_text_processed)
            
            # Compute TF-IDF vectors
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(reviews)
            
            # Compute cosine similarity
            cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
            
            # Get the index of the most similar review
            most_similar_index = cosine_sim.argmax()
            
            # Return the most similar review
            return df['Review'].iloc[most_similar_index]


        input_text = translated_text
        # Find the most similar review
        most_similar_review = find_most_similar_review(input_text, df)
        print(f"Most similar review: {most_similar_review}")


        # Translate the text to user language
        translator2 = Translator()
        translated_text2 = translator2.translate(most_similar_review, dest=language_code).text
        print("Translated text to user lang: " + translated_text2)

        # Convert the translated text to speech
        output2 = gTTS(text=translated_text2, lang=language_code, slow=True)
        output2.save("static/saves_audio/output.mp3")
        # os.system("start output.mp3")
      # Insert the values into the 'prediction1' table
        name = session.get('user_name')  # Get the name from session
        email = session.get('user_email')
        session['most_similar_review'] = most_similar_review
        query = "INSERT INTO prediction2 (name, email, disease) VALUES (%s, %s, %s)"
        values = (name, email, translated_text)
        executionquery(query, values)



        return render_template('voice.html', my_text = my_text, translated_text = translated_text, most_similar_review = most_similar_review)
    return render_template('voice.html')



@app.route('/model',methods =['GET','POST'])
def model():

    if request.method == 'POST':
        algorithams = request.form["algo"]
        if algorithams == "1":
            accuracy = 99
            msg = 'Accuracy  for DecisionTree Classifier is ' + str(accuracy) + str('%')
        elif algorithams == "2":
            accuracy = 99
            msg = 'Accuracy  for RandomForestClassifier is ' + str(accuracy) + str('%')
        elif algorithams == "3":
            accuracy = 74
            msg = 'Accuracy  for Support Vector Machine(SVM) is ' + str(accuracy) + str('%')
        elif algorithams == "4":
            accuracy = 66
            msg = 'Accuracy  for KNeighborsClassifier is ' + str(accuracy) + str('%')
        elif algorithams == "5":
            accuracy = 67
            msg = 'Accuracy  for GradientBoostingClassifier is ' + str(accuracy) + str('%')
        return render_template('model.html',msg=msg,accuracy = accuracy)
    return render_template('model.html')



    
if __name__ == '__main__':
    app.run(debug=True)