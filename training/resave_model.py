import joblib, os
from training.data_prep import load_and_preprocess
from training.train_model import train_and_save

train_and_save()  # it will automatically save with new absolute paths
