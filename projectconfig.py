import os


def create_directories(base_path):
    """
    Erstellt die Verzeichnisse Log und Data sowie ein Unterordner Archive in Data.

    Args:
        base_path (str): Basispfad, unter dem die Verzeichnisse erstellt werden sollen.
    """
    # Erstelle Log Verzeichnis
    log_path = os.path.join(base_path, "Log")
    if not os.path.exists(log_path):
        os.makedirs(log_path)
        print(f"Log directory created at {log_path}")

    # Erstelle Data Verzeichnis
    data_path = os.path.join(base_path, "Data")
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        print(f"Data directory created at {data_path}")

    # Erstelle Archive Unterordner in Data
    archive_path = os.path.join(data_path, "Archive")
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)
        print(f"Archive directory created at {archive_path}")


def update_project_path(filepath):
    """
    Diese Funktion aktualisiert den 'ProjectPath' in der angegebenen Python-Datei.

    Args:
        filepath (str): Der Pfad zur Datei, die aktualisiert werden soll.
    """
    current_path = os.path.dirname(__file__)
    new_content = []

    with open(filepath, "r") as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith("ProjectPath"):
            new_content.append(f'ProjectPath = "{current_path}"\n')
        else:
            new_content.append(line)

    with open(filepath, "w") as file:
        file.writelines(new_content)

    print(f"ProjectPath in {filepath} updated to {current_path}.")

    # Nach der Aktualisierung der Datei, erstelle die benötigten Verzeichnisse
    create_directories(current_path)


if __name__ == "__main__":
    # Pfad zur const.py Datei
    const_file_path = os.path.join(
        os.path.dirname(__file__), "src\\octoplug\\classes\\const.py"
    )
    update_project_path(const_file_path)
