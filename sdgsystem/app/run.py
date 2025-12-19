"""Entry point for running the SDG server."""
import uvicorn


def main():
    uvicorn.run(
        "sdgsystem.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()
