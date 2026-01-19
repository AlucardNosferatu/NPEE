import os


def list_files_in_directory(directory):
    files = os.listdir(directory)
    return files


[
    '.backup_completed', '.migration_completed',
    'bf0c145d-007f-416d-b6fc-cb873a10cbae',
    'config.dat', 'database.db', 'database.db-shm',
    'database.db-wal', 'requirements.txt', 'terms'
]
if __name__ == "__main__":
    current_directory = os.getcwd()
    files = list_files_in_directory(current_directory)
    print(files)
