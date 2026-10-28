from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Cookie Sesh</title>
        </head>
        <body>
            <h1>Grab Your Fortune Today!</h1>
            <p>This is a simple Flask app for all your psychic needs!</p>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
            <a href="/upload">Submit Your Fortunes</a>
            <a href="/download/fortunes.txt">Download Fortunes</a>
        </body>
    </html>
    """

@app.route('/about')
def about():
    return """
    <html>
        <head>
            <title>About Cookie Sesh</title>
        </head>
        <body>
            <h1>About Cookie Sesh</h1>
            <p>This is a simple Flask application created for demonstration purposes.</p>
        </body>
    </html>
    """

@app.route('/contact')
def contact():
    return """
    <html>
        <head>
            <title>Contact Cookie Sesh</title>
        </head>
        <body>
            <h1>Contact Cookie Sesh</h1>
            <p>You can reach me at:</p>
            <ul>
                <li>Email: example@email.com</li>
            </ul>
        </body>
    </html>
    """

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return """
    <html>
        <head>
            <title>Upload File</title>
        </head>
        <body>
            <h1>Upload File</h1>
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="file">
                <input type="submit" value="Upload">
            </form>
        </body>
    </html>
    """


# @app.route('/download/fortunes.txt')
# def download_fortunes():
#     return """
#     <html>
#         <head>
#             <title>Download Fortunes</title>
#         </head>
#         <body>
#             <h1>Download Fortunes</h1>
#             <p>Click the link below to download your fortunes:</p>
#             <a href="/fortunes.txt" download>Download Fortunes</a>
#         </body>
#     </html>
#     """
    

if __name__ == "__main__":
    app.run(debug=True, port=5000)


