# I'm using this because I'm avoiding more dependencies.
# Feel free to use this as an addon for your projects.



class Styler:
    def __init__(self):
        self.clr = 'ANSI'
        self.init()
        
    
    def init(self):
        if self.clr == 'ANSI':
            self.vals = {
                'underline': ('\033[4m', None, 'underline'),
                'reset': ('\033[0m', None, 'reset'),
                'bold': ('\033[1m', None, 'bold'),
                'black': ('\033[30m', '\033[40m', 'black'),
                'red': ('\033[31m', '\033[41m', 'red'),
                'green': ('\033[32m', '\033[42m', 'green'),
                'yellow':  ('\033[33m', '\033[43m', 'yellow'),
                'blue': ('\033[34m', '\033[44m', 'blue'),
                'magenta': ('\033[35m', None, 'magenta'),
                'cyan': ('\033[36m', None, 'cyan'),
                'white': ('\033[37m', None, 'white'),
            }
            
    def txt_style(self, clr: str, text):
        if clr.lower() in self.vals.keys():
            return f"{self.vals[clr][0]}{text}{self.vals['reset'][0]}"
        else:
            return None
    
    def bckg(self, clr: str, text):
        if clr.lower() in self.vals.keys():
            if self.vals[clr][1] is not None:
                return f"{self.vals[clr][1]}{text}{self.vals['reset'][0]}"
            else:
                return None
        return None