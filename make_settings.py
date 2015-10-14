print "Enter your apikey:"
apikey = raw_input('> ')

with open('my_settings.py', 'w') as f:
    f.write('X_API_KEY = "{}"'.format(apikey))
