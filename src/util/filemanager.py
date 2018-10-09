import os


class FileManager:

    def __init__(self, path):
        self.path = path
        self.dir = os.path.dirname(os.path.abspath(path))
        self.base = os.path.basename(path)
        self.name, self.ext = os.path.splitext(self.base)

        self.folder = "{}/{}".format(self.dir, self.name)
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def get_save_path(self, step):
        save_path = "{}/{}({}).{}".format(self.folder, self.name, step, self.ext)
        return save_path
