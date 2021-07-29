# std 
from pathlib import Path
import os  
import subprocess
import logging
import time
import signal
import sys
import shutil
import pprint
# internal 
import exceptions
import config
# 3rd party 
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent, EVENT_TYPE_MOVED, EVENT_TYPE_CREATED
import schedule

def startup():
    logging.basicConfig(level=config.LOG_LEVEL, format='%(asctime)s - %(message)s')
    logging.debug("CONFIG VALUES")
    for value in config.VALID_CONFIG_VALUES: 
        logging.debug('{}: {}'.format(value, pprint.pformat(getattr(config, value))))
    os.umask(config.UMASK)
    if not Path(config.METADATA_DB).exists(): 
        shutil.copy2(config.DEFAULT_METADATA_DB, config.METADATA_DB)
        logging.info('STARTUP: Coped default.metadata.db into calibre library')
    shutil.chown(config.METADATA_DB, user=config.LIBRARY_UID, group=config.LIBRARY_GID)
    for plugin in Path(config.CALIBRE_PLUGIN_DIR).iterdir():
        try:  
            subprocess.run(['calibre-customize', '--add-plugin', str(plugin)])
        except Exception: 
            logging.exception("STARTUP: Failed to import plugin {}".format(plugin))


def wait_on_file_transfer(file: Path) -> bool:
    size2 = -1
    logging.debug("IMPORT: Waiting on {} to finish transfering".format(file))
    time_start = time.time()
    while file.is_file():
        if (time.time() > time_start + 60 * config.TRANSFER_TIMEOUT): 
            logging.info("IMPORT: Timeout reached whilst waiting for {} to transfer".format(file))
            return False 
        try:
            size1 = file.stat().st_size
            if size1 == size2:
                break
            time.sleep(2)
            size2 = file.stat().st_size 
        except FileNotFoundError: 
            # avoid exceptions when calling stat() on a temp file (such as created by wget, rsync etc)
            continue
    if file.is_file():
        logging.debug("IMPORT: Transfer for file {} finished".format(file))
        return True 
    else:
        logging.debug("IMPORT: File {} deleted while waiting for transfer".format(file))
        return False # inform caller if file was deleted during transfer (likely to be a temp file)


def import_file(fpath: Path, ruleset: dict) -> bool: 
    logging.debug('IMPORT: Importing {} with ruleset {}'.format(fpath, pprint.pformat(ruleset)))
    fpath = fpath.resolve()
    if not fpath.is_file():
        raise exceptions.NotAFileException('IMPORT: Failed to import {} as it is not a file'.format(fpath))

    if ruleset['pattern'] is not None and ruleset['pattern'].match(str(fpath)) is None: 
        logging.info('IMPORT: File {} did not match pattern {} and was not added'.format(str(fpath), ruleset['pattern'].pattern))
        return False

    if ruleset['run'] is not None:  
        res = subprocess.run(ruleset['run'].format(file=fpath).split(), capture_output=True)
        if res.returncode != 0: 
            logging.critical(
                ''' IMPORT: Users command {} returned non-zero exit code, {}. 
                Enable LOG_LEVEL=DEBUG to view command output '''.format(res.args, res.returncode)
            )
        logging.debug('IMPORT: OUTPUT for users command {} \n\n STDERR: {} \n\n STDOUT: {}'.format(res.args, res.stderr, res.stdout))

    # dont bother checking outcome since its basically impossible to fail given a valid file path. calibre will import anything. 
    c = [*(config.CALIBRE_ADD_COMMAND.split()), '--with-library', config.CALIBRE_LIBRARY, str(fpath)]
    logging.debug('IMPORT: Adding file to library using command {}'.format(c))
    subprocess.run(c, user=config.LIBRARY_UID, group=config.LIBRARY_GID, umask=config.UMASK)
    logging.info('IMPORT: File {} added to library'.format(fpath)) 

    if ruleset['remove']: 
        fpath.unlink()
        logging.info('IMPORT: Deleted original file at {}'.format(fpath))
    return True


def import_all_files(ruleset: dict) -> None:
    root = ruleset['source']
    for dirpath, _, fnames in os.walk(str(root)): 
        for f in fnames:
            import_file(Path(dirpath).joinpath(f), ruleset)


class NewFileEventHandler(FileSystemEventHandler):
    def __init__(self, ruleset: dict) -> None: 
        self.ruleset = ruleset

    def on_any_event(self, event: FileSystemEvent) -> None:
        if (
            event.event_type in (EVENT_TYPE_CREATED, EVENT_TYPE_MOVED) and 
            event.is_directory == False 
        ):
            logging.debug('IMPORT: Handling event {} of type {}'.format(event.src_path, event.event_type))
            if event.event_type == EVENT_TYPE_MOVED: 
                path = Path(event.dest_path)
            else: 
                path = Path(event.src_path)

            if (wait_on_file_transfer(path)): 
                import_file(path, self.ruleset)


class Main(): 
    def __init__(self): 
        self.scheduler = schedule.Scheduler()
        self.observer = Observer()
        signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)        

    def start(self): 
        if (config.IMPORT_MODE.casefold() == "ONESHOT".casefold()):
            logging.info("MAIN: Starting ONESHOT mode")
            for ruleset in config.WATCH: 
                import_all_files(ruleset)        
        elif (config.IMPORT_MODE.casefold() == "ALL".casefold()): 
            logging.info("MAIN: Starting ALL mode")
            for ruleset in config.WATCH: 
                self.scheduler.every(config.IMPORT_ALL_TIMER).minutes.do(import_all_files, ruleset)
                self._enter_schedule_thread()
        elif (config.IMPORT_MODE.casefold() == "NEW".casefold()):
            logging.info("MAIN: Starting NEW mode")
            for ruleset in config.WATCH:
                self.observer.schedule(NewFileEventHandler(ruleset), ruleset['source'], recursive=True)
                self._enter_watchdog_thread()
        else: 
            logging.critical("MAIN: Failed to start Main; is IMPORT_MODE valid?")

    def _enter_watchdog_thread(self): 
        self.observer.start()
        self.observer.join()

        logging.critical("MAIN: Observer thread terminated - exiting")
        sys.exit()

    def _enter_schedule_thread(self): 
        while self.scheduler.jobs != []: 
            self.scheduler.run_pending()
            time.sleep(1)
        
        logging.critical("MAIN: Job list empty (without manual intervention) - exiting")
        sys.exit()

    def _signal_handler(self) -> None:
        logging.critical('MAIN: Recieved SIGHUP or SIGTERM exiting after clearing job list - any job currently in progress will complete. ')
        self.scheduler.clear()
        sys.exit("MAIN: Exiting due to SIGHUP/SIGTERM")


if __name__ == "__main__": 
    startup()
    app = Main()
    app.start()