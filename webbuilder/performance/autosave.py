class AutoSave:
    def __init__(self, save_func, interval=0):
        self._save_func = save_func
        self._interval = interval
        self._dirty = False

    def mark_dirty(self):
        self._dirty = True

    def check_and_save(self):
        if self._dirty:
            self._dirty = False
            self._save_func()

    def force_save(self):
        self._dirty = False
        self._save_func()
