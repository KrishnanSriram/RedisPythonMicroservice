# This class will co-ordinate all operations for image conversion
# Will take PDF2ImageCommand object as parameter
# This will consume source PDF file as base64, convert it to a 
# real file, then convert it into an image and store it in images directory
# Further will convert the image file into base64 string if needed and 
# publish final construct into redis service
class PDF2ImageController:
  pass