### All you need from this package :
- `start_recognition()` --> Start the facial recognition process using the webcam or the raspberry pi cam 
- `get_recognition_result()` --> returns json format contains the `name` and the `class` of the detected person 

#### Just call these methode and you're ready to go.

# package details :
- `helpers` :
    - Run `image_capture.py` indepently to capture the image of persons and save them in the `assets` dirctory , or you can add your photos manually in the assets .
    
    - Then run `model_training.py` to train your model whick then the pickle files will be saved in the assets .

- `controllers` : Essential methods which will be used from this package .