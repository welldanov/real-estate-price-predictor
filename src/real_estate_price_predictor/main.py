# https://github.com/hflabs/dadata-py

from dadata import Dadata
token = "0fbb51cb8a9256eb5d0154a9aea63540d306888b"
secret = "f702d537399f64bfbffbdf23a508982fbb473d6b"
dadata = Dadata(token, secret)
result = dadata.clean("address", "альметьевск ленина 125")
print(result["city_area"])