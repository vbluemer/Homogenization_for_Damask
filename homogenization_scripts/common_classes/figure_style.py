
class FigureStyle:
    def __init__(self, 
                 linewidth          =2.0, 
                 markersize         =6.0,
                 markeredgewidth    =2,
                 fontsize           =12,
                 paperformat        = False,
                 pt_color           = '#0072BD',
                 sym_pt_color       = 'r',
                 ln_color           = '#440154',
                 ):
        
        self.lw = linewidth
        self.ms = markersize
        self.mew = markeredgewidth
        self.fs = fontsize
        self.pf = paperformat
        self.pt_color = pt_color
        self.sym_pt_color =sym_pt_color
        self.ln_color = ln_color