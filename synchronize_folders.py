import os
import sys
import shutil
import argparse
import time

# Set up command line arguments
parser = argparse.ArgumentParser(description='Synchronize two folders.')
parser.add_argument('source', metavar='source_folder', type=str, help='Path to source folder.')
parser.add_argument('replica', metavar='replica_folder', type=str, help='Path to replica folder.')
parser.add_argument('interval', metavar='sync_interval', type=int, help='Synchronization interval in seconds.')
parser.add_argument('logfile', metavar='log_file', type=str, help='Path to log file.')
args = parser.parse_args()

# Set up logging
log_file = open(args.logfile, 'a')

# Keep track of source and replica files and directories
source_files = set()
replica_files = set()
source_dirs = set()
replica_dirs = set()

# Synchronize folders
while True:
    start_time = time.time()
    t = time.localtime()
    current_time = time.strftime("%d/%m/%Y %H:%M:%S", t)

    # Copy new and updated files and directories from source to replica
    for root, dirs, files in os.walk(args.source):
        for dir in dirs:
            source_path = os.path.join(root, dir)
            replica_path = os.path.join(args.replica, os.path.relpath(source_path, args.source))
            if not os.path.exists(replica_path):
                shutil.copytree(source_path, replica_path)
                log_line = f'{current_time} [ CREATE ] \n' \
                           f'   - Folder name: {dir} \n' \
                           f'   - Source path: {source_path} \n' \
                           f'   - Replica path: {replica_path} \n'
                log_file.write(log_line)
                log_file.flush()
                sys.stdout.write(log_line)
        for file in files:
            source_path = os.path.join(root, file)
            replica_path = os.path.join(args.replica, os.path.relpath(source_path, args.source))
            if not os.path.exists(replica_path) or os.stat(source_path).st_mtime - os.stat(replica_path).st_mtime > 1:
                shutil.copy2(source_path, replica_path)
                log_line = f'{current_time} [ CREATE ] \n' \
                           f'   - File name: {file} \n' \
                           f'   - Source path: {source_path} \n' \
                           f'   - Replica path: {replica_path} \n'
                log_file.write(log_line)
                log_file.flush()
                sys.stdout.write(log_line)

    # Remove files and directories from replica that are not in source
    for root, dirs, files in os.walk(args.replica):
        for dir in dirs:
            replica_path = os.path.join(root, dir)
            source_path = os.path.join(args.source, os.path.relpath(replica_path, args.replica))
            if not os.path.exists(source_path):
                shutil.rmtree(replica_path)
                log_line = f'{current_time} [ REMOVE ] \n' \
                           f'   - Folder name: {dir} \n' \
                           f'   - Source path: {source_path} \n' \
                           f'   - Replica path: {replica_path} \n'
                log_file.write(log_line)
                log_file.flush()
                sys.stdout.write(log_line)
        for file in files:
            replica_path = os.path.join(root, file)
            source_path = os.path.join(args.source, os.path.relpath(replica_path, args.replica))
            if not os.path.exists(source_path):
                os.remove(replica_path)
                log_line = f'{current_time} [ REMOVE ] \n' \
                           f'   - File name: {file} \n' \
                           f'   - Source path: {source_path} \n' \
                           f'   - Replica path: {replica_path} \n'
                log_file.write(log_line)
                log_file.flush()
                sys.stdout.write(log_line)

        # Calculate synchronization time
        sync_time = time.time() - start_time

        # Wait for the remaining time in the synchronization interval
        if sync_time < args.interval:
            time.sleep(args.interval - sync_time)