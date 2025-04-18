from app import create_app

# create app object
app = create_app()
application = app

# run app
if __name__ == "__main__":
    app.run(debug=False, port=8080, host='0.0.0.0')
