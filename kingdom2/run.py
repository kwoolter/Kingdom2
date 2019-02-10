import kingdom2.controller as controller
import logging

def main():

    logging.basicConfig(level = logging.INFO)

    c = controller.GameCLI()
    c.run()
    return

if __name__ == "__main__":
    main()
    exit(0)