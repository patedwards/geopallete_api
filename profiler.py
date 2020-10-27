from app import analyse_response_data 
import time
#import cProfile

data = {'bBoxes': [[-81.8143831185681, -75.23890778594303, -39.84134836903882, -65.87937207863669]]}
#cProfile.run("analyse_response_data(data)")
t0 = time.time()
print(analyse_response_data(data))
t1 = time.time()
print(t1-t0)