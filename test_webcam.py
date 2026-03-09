import cv2 


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_eye.xml')

video = cv2.VideoCapture(0)
ok, image = video.read()
video.release()

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
visage = face_cascade.detectMultiScale(gray)
yeux = eye_cascade.detectMultiScale(gray)

print(f"Visages: {len(visage)}, Yeux: {len(yeux)}")

# pour voir l'image capturer 
# cv2.imshow("Nadhamni - Webcam Test", image)
# cv2.waitKey(0)
