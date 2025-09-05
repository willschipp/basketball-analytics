import pickle

def get_list(pkl_path):
    values = []
    with open(pkl_path,'rb') as f:
        values = pickle.load(f)    
    return values