from app import app

if __name__ == "__main__":
    import webbrowser
    # Open the default web browser to the Flask server URL
    webbrowser.open_new("http://127.0.0.1:5000")
    app.run()

