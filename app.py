from src.main import create_app
from src.config import config_instance
import threading

# Create the Flask app, chat_io, and message_loop
app = create_app(config=config_instance())


if __name__ == '__main__':
    # Run the Flask app

    app.run(debug=True, port=8088)
