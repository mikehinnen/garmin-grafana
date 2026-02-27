from garminconnect import Garmin
email = input('Email: ')
password = input('Password: ')
g = Garmin(email, password)
g.login()
g.garth.dump('/home/appuser/.garminconnect')
print('Token gespeichert!')
