import pyqrcode

url = pyqrcode.create('https://qorca.herokuapp.com/core/user/3')

url.png('code.png', scale=10)