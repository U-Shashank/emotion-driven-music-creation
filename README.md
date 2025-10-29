# Emotion Driven Music Curation

This is a mini project for our Computer Vision coursework: a simple service that predicts emotion from images and recommends music accordingly. The repo contains a client (UI) and a server (inference + API), and includes pointers to model training and the best pretrained weights.

## Quick Start

### Client

```bash
cd client
pnpm install
pnpm dev
```

### Server

```bash
cd server
sudo mv example.env .env
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Using a custom model

- If you want to use the provided pretrained model, download `best_model.pth` from the "Best Model" link below.
- Alternatively, you can train your own ViT model (see Model Training).
- By default the server loads the built-in model. To use a custom model:
  1. Put `best_model.pth` (or your model file) into a `server/best_model.pth`
  2. Update your .env to tell the server to use a custom model:
     - MODEL_TYPE=custom
  3. Restart the server.

## Model Training

https://colab.research.google.com/drive/1sGvVHqpOi6HvSpsuo6EAc-09QIgaNkJA?usp=sharing

## Best Model

https://drive.google.com/drive/folders/123kh4zBkUBRiDx5zbTJz50zyIjt7zuY2
