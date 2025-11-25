from ultralytics import YOLO

model = YOLO('yolov8l-pose.pt')

results = model.train(
   data='/content/data.yaml',
   epochs=120,
   imgsz=640,
   patience=100,
   batch=8,


   name='modelo_final' 
)
