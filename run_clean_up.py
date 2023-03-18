from settings import Settings
import os


def main():
    os.system(f"rm {Settings.global_path}/data/articles/*.json")
    os.system(f"rm {Settings.global_path}/data/topics_update.json")
    os.system(f"rm {Settings.global_path}/topic2articles.json")


if __name__ == "__main__":
    main()