from openwakeword.train import train
import os

# Output folder for the trained model
os.makedirs("models/wake_word", exist_ok=True)

train(
    model_name="hey_athena",
    target_phrase=["Hey Athena"],
    output_dir="models/wake_word",
    n_samples=5000,        # synthetic samples to generate
    epochs=100,
    batch_size=32,
)

print("✅ Wake word model trained and saved to models/wake_word/")