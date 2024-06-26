import face_recognition
import os, sys
import cv2
import numpy as np
import math


# calculate accuracy of the model (%)
def face_confidence(face_distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_value = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_value * 100, 2)) + "%"
    else:
        value = (linear_value + ((1.0 - linear_value) * math.pow((linear_value - 0.5) * 2, 0.2))) * 100
        return str(round(value,2)) + "%"
    
class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings = []
    known_face_names = []
    process_current_frame = True

    def __init__(self):
        self.encode_faces()
    
    def encode_faces(self):
        for image in os.listdir('faces'):
            face_image = face_recognition.load_image_file(f'faces/{image}')
            face_encodings = face_recognition.face_encodings(face_image)
            
            if len(face_encodings) > 0:
                face_encoding = face_encodings[0]
                self.known_face_encodings.append(face_encoding)
                self.known_face_names.append(image)
            else:
                print(f"No face found in {image}")

        print(self.known_face_names)


    def run_recognition(self):
        video_capture = cv2.VideoCapture(0) # use default camera
    

        if not video_capture.isOpened():
            sys.exit("Error: Could not open video device.")

        while video_capture.isOpened():
            ret, frame = video_capture.read()

            if self.process_current_frame:
                small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
                # rgb_small_Frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)


                # find all the faces in the current frame of video
                self.face_locations = face_recognition.face_locations(small_frame)
                self.face_encodings = face_recognition.face_encodings(small_frame, self.face_locations)

                # perform image recognition
                self.face_names = []
                for face_encoding in self.face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"
                    confidence = "Unknown"

                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = face_confidence(face_distances[best_match_index])

                        print("====================================")
                        print(f"Match found: {name} with confidence {confidence}")
                        print("Family member detected, contact the owner to unlock the door")
                    
                    else:
                        print("====================================")
                        print(f"No match found, unknown person detected")
                        print("Unknown person detected, notifying the owner")

                    self.face_names.append(name + " " + confidence)

            self.process_current_frame = not self.process_current_frame # happens every other frame to save processing power

            # display the annotation
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), -1)

                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)
            
            cv2.imshow('Face Recognition', frame)

            if cv2.waitKey(1) == ord('q'):
                break

        video_capture.release() # done
        cv2.destroyAllWindows()

if __name__ == '__main__':
    fr = FaceRecognition()
    fr.run_recognition()

