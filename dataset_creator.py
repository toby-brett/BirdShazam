import os

import numpy as np
from pydub import AudioSegment
import librosa
import random


def make_clip(bird_files, duration_ms=5000):
    base = AudioSegment.silent(duration=duration_ms)
    labels = []

    for bird_name, path in bird_files.items():
        audio = AudioSegment.from_mp3(path)

        length = len(audio)

        # start 5 seconds in to filter any speaking
        if length < 12000:
            continue

        start_idx = random.randint(5000, length - duration_ms)
        audio = audio[start_idx:start_idx + duration_ms]

        base = base.overlay(audio)
        labels.append(bird_name)

    return base, labels


def make_spectrogram(bird_files, duration_ms=5000):
    audio, labels = make_clip(bird_files, duration_ms)
    samples = np.array(audio.get_array_of_samples()).astype(np.float64)
    sr = audio.frame_rate

    gram = librosa.feature.melspectrogram(y=samples, sr=sr, n_mels=128)
    gram_db = librosa.power_to_db(gram, ref=np.max)

    return gram_db, labels


BIRDS = ["blutit", "eurgol", "eurrob1", "houspa"]

def encode_labels(present_birds):
    return [1 if bird in present_birds else 0 for bird in BIRDS]


def generate_data():

    spectrograms = []
    all_labels = []

    for i in range(2_000):

        # up to 10 birds
        birds = {}
        for bird in range(random.randint(1, 10)):

            bird_folders = os.listdir("bird_data")
            bird_name = random.choice(bird_folders)

            bird_dir = os.path.join("bird_data", bird_name)
            file_name = random.choice(os.listdir(bird_dir))

            birds[bird_name] = os.path.join(bird_dir, file_name)

        spectrogram, labels = make_spectrogram(birds)
        labels = encode_labels(labels)
        spectrograms.append(spectrogram)
        all_labels.append(labels)

    np.save("spectograms.npy", np.array(spectrograms))
    np.save("labels.npy", np.array(all_labels))

generate_data()