# [spec: CHAT-001]
import time

from chatbot import launch_app


def main():
    print("🚀 Launching Jarvis Business Case Chatbot...")
    launch_app(share=False)
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
