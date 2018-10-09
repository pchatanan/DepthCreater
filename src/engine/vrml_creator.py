import subprocess, os, sys


class VrmlCreator:

    def __init__(self, filename, x_length, y_length, z_length):
        self.filename = filename
        self.output_path = "output\\" + filename + "\\" + filename + ".wrl"
        self.x_length = x_length
        self.y_length = y_length
        self.z_length = z_length

    def create(self):
        hx = self.x_length / 2.0
        hy = self.y_length / 2.0
        hz = self.z_length / 2.0

        look_up_list = [('#P1#', '{} {} {}'.format(hx, hy, hz)),
                        ('#P2#', '-{} {} {}'.format(hx, hy, hz)),
                        ('#P3#', '-{} -{} {}'.format(hx, hy, hz)),
                        ('#P4#', '{} -{} {}'.format(hx, hy, hz)),
                        ('#P5#', '{} {} -{}'.format(hx, hy, hz)),
                        ('#P6#', '-{} {} -{}'.format(hx, hy, hz)),
                        ('#P7#', '-{} -{} -{}'.format(hx, hy, hz)),
                        ('#P8#', '{} -{} -{}'.format(hx, hy, hz)),
                        ('#TOP#', '{}(top).png'.format(self.filename)),
                        ('#LEFT#', '{}(left).png'.format(self.filename)),
                        ('#RIGHT#', '{}(right).png'.format(self.filename)),
                        ]

        with open('template.wrl', 'r') as myfile:
            data = myfile.read()
            data_out = data

        for old, new in look_up_list:
            data_out = data_out.replace(old, new)

        with open(self.output_path, 'w') as outfile:
            outfile.write(data_out)

        if sys.platform.startswith('darwin'):
            subprocess.call(('open', self.output_path))
        elif os.name == 'nt':
            os.startfile(self.output_path)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', self.output_path))

