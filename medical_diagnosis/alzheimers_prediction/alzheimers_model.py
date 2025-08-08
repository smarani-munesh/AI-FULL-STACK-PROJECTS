import os
import numpy as np
import pydicom
import cv2
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping

# ✅ Step 1: Load and preprocess mixed image formats (.dcm and .jpg/.jpeg/.png)
def load_mixed_images(dataset_path, categories):
    images = []
    labels = []

    print("🧠 Loading medical images (.dcm, .jpg, .jpeg, .png)...")
    valid_image_extensions = [".dcm", ".jpg", ".jpeg", ".png"]

    for category in categories:
        category_path = os.path.join(dataset_path, category)
        if not os.path.exists(category_path):
            print(f"❌ Folder not found: {category_path}")
            continue

        count = 0
        for patient_folder in os.listdir(category_path):
            patient_path = os.path.join(category_path, patient_folder)
            if not os.path.isdir(patient_path):
                continue

            for file in os.listdir(patient_path):
                file_path = os.path.join(patient_path, file)
                ext = os.path.splitext(file)[1].lower()

                try:
                    if ext == ".dcm":
                        ds = pydicom.dcmread(file_path)
                        img = ds.pixel_array
                    elif ext in [".jpg", ".jpeg", ".png"]:
                        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                    else:
                        continue  # Skip unsupported formats

                    # Resize and normalize
                    img_resized = cv2.resize(img, (128, 128))
                    img_normalized = img_resized.astype(np.float32) / 255.0
                    images.append(img_normalized)
                    labels.append(category)
                    count += 1
                except Exception as e:
                    print(f"⚠️ Error in {file_path}: {e}")

        print(f"✅ Loaded {count} images from category '{category}'")

    print(f"🔍 Total samples loaded: {len(images)}")
    print(f"Unique labels found: {set(labels)}")
    return np.array(images), np.array(labels)

# ✅ Step 2: Paths and labels
dataset_path = r"D:\medical_diagnosis\Alzheimers disease mri images"
categories = ['AD', 'MCI', 'NC']

# ✅ Step 3: Load images
images, labels = load_mixed_images(dataset_path, categories)

# ✅ Step 4: Encode labels and reshape
label_encoder = LabelEncoder()
labels_encoded = label_encoder.fit_transform(labels)
images = images.reshape(-1, 128, 128, 1)

# ✅ Step 5: Train-test split
X_train, X_test, y_train, y_test = train_test_split(images, labels_encoded, test_size=0.2, random_state=42)
y_train = to_categorical(y_train, num_classes=3)
y_test = to_categorical(y_test, num_classes=3)

# ✅ Step 6: CNN model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 1)),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(3, activation='softmax')
])

# ✅ Step 7: Compile and Train
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
early_stop = EarlyStopping(patience=5, restore_best_weights=True)
model.fit(X_train, y_train, epochs=20, batch_size=16, validation_split=0.2, callbacks=[early_stop])

# ✅ Step 8: Evaluate
loss, accuracy = model.evaluate(X_test, y_test)
print(f"📊 Test Accuracy: {accuracy * 100:.2f}%")

# ✅ Step 9: Save model
model.save("alzheimers_cnn_model.h5")
print("✅ Model saved as alzheimers_cnn_model.h5")
