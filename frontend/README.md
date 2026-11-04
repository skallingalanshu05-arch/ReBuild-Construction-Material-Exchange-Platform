# Pixel Perfect Replica

Implement exactly the screenshot and nothing else

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/080dc852-63a6-4e0d-8440-01c1f1de5215).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

This app lives in the **ReBuild monorepo** at `frontend/`. See the [root README](../README.md) for full setup.

```sh
cd frontend
cp .env.example .env
bun install   # or npm install
bun run dev   # or npm run dev
```

Set `VITE_API_BASE_URL` in `.env` (see `.env.example`) when not using the Vite dev proxy; otherwise the app calls `/api/v1` on the same origin.
