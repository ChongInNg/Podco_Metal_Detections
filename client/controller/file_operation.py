
import os
import shutil
import re
from datetime import datetime
from typing import Callable
from log.logger import Logger

class FileOperation:
    def __init__(self, src_folders: list[str], mount_point: str, need_copy_files_suffix: list[str],
            update_progress_callback: Callable[[str, int], None]) -> None:
        self.src_folders = src_folders
        self.mount_point = mount_point
        self.need_copy_files_suffix = need_copy_files_suffix
        self.update_progress_callback = update_progress_callback
        self.total_files_need_to_copy = 0

    def copy_from_folders(self, only_count=False):
        count = 0
        for folder in self.src_folders:
            Logger.debug(f"copying files from {folder}")
            try:
                ncount = self.copy_files(folder, only_count)
                count += ncount
                Logger.debug(f"Total copy files count: {ncount} from {folder}")
            except Exception as e:
                Logger.error(f"copy files from {folder} error: {e}")
        return count

    def count_total_files_need_to_copy(self) -> int:
        self.total_files_need_to_copy = self.copy_from_folders(only_count=True)
        return self.total_files_need_to_copy

    def copy_files(self, src_folder, only_count=False) -> int:
        last_directory = os.path.basename(src_folder)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dest_log_folder = os.path.join(self.mount_point, last_directory, timestamp)
        if not os.path.exists(src_folder):
            Logger.warning(f"src folder:{src_folder} deosn't exist.")
            return 0
        
        if not os.path.exists(dest_log_folder):
            os.makedirs(dest_log_folder)
            Logger.warning(f"dest folder isn't exist, so create the folder: {dest_log_folder}")

        count = 0
        file_list = os.listdir(src_folder)
        for filename in file_list:
            for suffix in self.need_copy_files_suffix:
                pattern = rf"\.{suffix}$"
                
                if re.search(pattern, filename, re.IGNORECASE):
                    src_file_path = os.path.join(src_folder, filename)
                    dest_file_path = os.path.join(dest_log_folder, filename)
                    if not only_count:
                        shutil.copyfile(src_file_path, dest_file_path)
                        if self.update_progress_callback:
                            self.update_progress_callback(src_file_path, count)

                        Logger.debug(f"copy file success {src_file_path}, {dest_file_path}, current count: {count}")

                    count += 1
        if not only_count:
            Logger.debug(f"Total copy {count} files from {src_folder} to {dest_log_folder}")
        return count
    
    def _check_file_exist(self, full_file_path: str) -> bool:
        return os.path.exists(full_file_path)
        
    def _check_file_change(self, src_file_path: str, dest_file_path: str) -> bool:
        try:
            src_file_info = os.stat(src_file_path)
            dest_file_info = os.stat(dest_file_path)
            if src_file_info.st_size == dest_file_info.st_size:
                return False
            else:
                Logger.debug(f"file size was changed, src:{src_file_info.st_size}, dest:{dest_file_info.st_size}")
                return True
        except FileNotFoundError:
            return True
        
        