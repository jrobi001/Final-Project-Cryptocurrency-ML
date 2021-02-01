from tqdm import tqdm
import time

# for i in tqdm.tqdm(range(1000)):
#     time.sleep(0.01)
#     # or other long operations

pbar = tqdm(total=201)
for i in range(200):
    time.sleep(0.1)
    pbar.update(1)
pbar.close()
