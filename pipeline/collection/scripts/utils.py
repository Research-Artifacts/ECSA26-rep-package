import os
from datetime import datetime
from typing import Optional

ROOT = os.getcwd()


def format_datetime() -> str:
    """Return the current datetime formatted for use in filenames."""
    return datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


class Menu:
    @staticmethod
    def _get_filtered_entries(root: str, *, files: bool) -> list[str]:
        """
        Return a sorted list of directory entries filtered by type (files or folders),
        excluding hidden entries and those starting with '_'.

        Args:
            root (str): Path to search.
            files (bool): If True, return files; otherwise, return folders.

        Returns:
            list[str]: Filtered and sorted list of names.
        """
        try:
            entries = os.listdir(root)
        except FileNotFoundError:
            raise FileNotFoundError(f"Path does not exist: {root}") from None

        result: list[str] = []
        for entry in entries:
            if entry.startswith('.') or entry.startswith('_'):
                continue

            full_path = os.path.join(root, entry)
            if files and not os.path.isdir(full_path):
                result.append(entry)
            elif not files and os.path.isdir(full_path):
                result.append(entry)

        result.sort()
        return result

    @staticmethod
    def _ask_index(max_index: int, prompt: str) -> int:
        """
        Ask the user for a valid index within the range [0, max_index].

        Args:
            max_index (int): Maximum valid index.
            prompt (str): Prompt message.

        Returns:
            int: A valid index chosen by the user.
        """
        while True:
            raw_value = input(prompt)

            try:
                index = int(raw_value)
            except ValueError:
                print("Invalid input. Please type a number.")
                continue

            if 0 <= index <= max_index:
                return index

            print(f"Invalid selection. Please choose a number between 0 and {max_index}.")

    @staticmethod
    def list_files_2_menu(root: str, word: str) -> str:
        """
        Present a menu with all non-hidden files in `root` and return the full path
        of the selected file.

        Args:
            root (str): Path to the directory containing the files.
            word (str): Word to display in the choice prompt.

        Returns:
            str: Full path to the selected file.

        Raises:
            FileNotFoundError: If no files are found in the directory.
        """
        files = Menu._get_filtered_entries(root, files=True)

        if not files:
            raise FileNotFoundError(f"No files available in directory: {root}")

        print('\nAvailable file options:\n')
        for i, filename in enumerate(files):
            print(f'{i} - {filename}')

        index = Menu._ask_index(
            len(files) - 1,
            f'\nWhich {word} do you want to do with?\n'
        )

        return os.path.join(root, files[index])

    @staticmethod
    def list_folders_2_menu(root: str) -> list[str]:
        """
        List all folders in the given root directory, excluding hidden folders
        and those starting with '_'.

        Args:
            root (str): Path to the root directory.

        Returns:
            list[str]: List of folder names in the root directory.
        """
        return Menu._get_filtered_entries(root, files=False)

    @staticmethod
    def recursive_folder_navigation(path: str, word: str) -> Optional[str]:
        """
        Navigate folders recursively until the user selects a directory without subfolders
        or decides to exit.

        Args:
            path (str): Path to the root directory.
            word (str): Word to display in the choice prompt.

        Returns:
            Optional[str]: Path to the selected folder, or None if the user exits.
        """
        current_path = path

        while True:
            folders = Menu.list_folders_2_menu(current_path)

            if not folders:
                print(f"No more subfolders in: {current_path}")
                return current_path

            print('\nAvailable folder options:\n')
            for index, folder_name in enumerate(folders):
                print(f'{index} - {folder_name}')
            print(f'{len(folders)} - Exit')

            selected_index = Menu._ask_index(
                len(folders),
                f'\nWhich {word} do you want to select? '
            )

            if selected_index == len(folders):  # Exit option
                print("Exiting navigation.")
                return None

            current_path = os.path.join(current_path, folders[selected_index])
