#std 
from pathlib import Path
import os  
import subprocess
import re
import logging
from typing import Union
import time
import signal
import sys
import shutil
#internal 
import exceptions
import config 
#3rd party 
import watchdog
import schedule

def setup(): 
    os.umask(config.UMASK)
    if not Path(config.METADATA_DB).exists(): 
        shutil.copy2(config.DEFAULT_METADATA_DB, config.METADATA_DB)
    shutil.chown(config.METADATA_DB, user=config.LIBRARY_UID, group=config.LIBRARY_GID)
    for plugin in Path(config.CALIBRE_PLUGIN_DIR).iterdir():
        try:  
            subprocess.run(['calibre-customize', '--add-plugin', str(plugin)])
        except Exception as e: 
            logging.exception("Failed to import plugin {}".format(plugin))

def wait_on_transfer(file: Path) -> None:
    size2 = -1
    while True:
        size1 = file.stat().st_size
        if size1 == size2:
            break
        sleep(2)
        size2 = file.stat().st_size

def import_file(fpath: Path, ruleset: dict) -> bool: 
    fpath = fpath.resolve()
    if not fpath.is_file():
        raise exceptions.NotAFileException('IMPORT: Failed to import {} as it is not a file'.format(fpath))

    if ruleset['pattern'] is not None and ruleset['pattern'].match(fpath) is None: 
        logging.info('IMPORT: File {} did not match pattern {} and was not added'.format(fpath, pattern.pattern))
        return False

    if ruleset['run'] is not None:  
        res = subprocess.run(ruleset['run'].format(file=str(fpath)).split(), capture_output=True)
        if res.returncode != 0: 
            logging.critical(
                ''' IMPORT: Users command {} returned non-zero exit code, {}. 
                Enable LOG_LEVEL=DEBUG to view command output '''.format(res.args, res.returncode)
            )
        logging.debug('IMPORT: OUTPUT for users command {} \n\n STDERR: {} \n\n STDOUT: {}'.format(res.args, res.stderr, res.stdout))

    # dont bother checking outcome since its basically impossible to fail given a valid path 
    subprocess.run(config.CALIBRE_ADD_COMMAND.append(str(fpath), user=config.LIBRARY_UID, group=config.LIBRARY_GID, umask=config.UMASK))
    logging.info('IMPORT: File {} added to library'.format(fpath)) 

    if ruleset['remove']: 
        fpath.unlink()
        logging.info('IMPORT: Deleted original file at {}'.format(fpath))
    return True

def import_all_files(root: Path, ruleset: dict) -> None:
    if not root.is_dir(): 
        raise exceptions.NotADirectoryException('Root folder {} is not a directory'.format(root))
    for dirpath, dirname, fnames in os.walk(str(root)): 
        for f in fnames:
            import_file(Path(dirpath).joinpath(f), ruleset)

class NewFileEventHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, ruleset: dict) -> None: 
        self.ruleset = ruleset

    def on_any_event(self, event: watchdog.events.FileSystemEvent) -> None:
        if (
            event.event_type in (watchdog.events.EVENT_TYPE_CREATED, watchdog.events.EVENT_TYPE_MOVED) and 
            not event.is_directory 
        ): 
            path = Path(event.src_path)
            wait_on_transfer(path)
            import_file(path, self.ruleset)

class Main(): 
    def __init__(self): 
        logging.basicConfig(level=config.LOG_LEVEL, format='%(asctime)s - %(message)s')
        self.scheduler = schedule.Scheduler()
        self.observer = watchdog.observers.Observer()
        signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)        

    def start(self): 
        if (config.IMPORT_MODE.casefold() == "ONESHOT".casefold()):
            for ruleset in config.WATCH: 
                import_all_files(ruleset)        
        elif (config.IMPORT_MODE.casefold() == "ALL".casefold()): 
            for ruleset in config.WATCH: 
                self.scheduler.every(config.IMPORT_ALL_TIMER).minutes.do(import_all_files, ruleset)
                self._enter_schedule_thread()
        elif (config.IMPORT_MODE.casefold() == "NEW".casefold()):
            for ruleset in config.WATCH:
                self.observer.schedule(NewFileEventHandler(ruleset), ruleset['source'], recursive=True)
                self._enter_watchdog_thread()
        else: 
            logging.critical("Failed to start Main; is IMPORT_MODE valid?")

    def _enter_watchdog_thread(self): 
        self.observer.start()
        self.observer.join()

        logging.critical("Observer thread terminated - exiting")
        sys.exit()

    def _enter_schedule_thread(self): 
        while self.run.jobs != []: 
            self.run.run_pending()
            time.sleep(1)
        
        logging.critical("Job list empty (without manual intervention) - exiting")
        sys.exit()

    def _signal_handler(self) -> None:
        logging.critical('Recieved SIGHUP or SIGTERM exiting after clearing job list - any job currently in progress will complete. ')
        self.scheduler.clear()
        sys.exit("Exiting due to SIGHUP/SIGTERM")


if __name__ == "__main__": 
    setup()
    app = Main()
    app.start()