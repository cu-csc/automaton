import pylab as plt
from parser import Parser
from lib.util import read_path

class Graph(object):
    def __init__(self,config):
        self.config = config
        self.parser = Parser(self.config)
        self.graph_path = self.config.globals.graph_path
        self.attributes = list()
        self.attributes = self.parser.instance_types

    def generate_graph(self):
        raw_data = self.parser.get_mean()
        for item in raw_data:
            data=list()
            for n in range(len(self.attributes)):
                data.append(item[n+1])
            figure_name = '%s/%s.png' % (self.graph_path,item[0])
            figure = bar_graph(item[0],self.attributes,data,figure_name)
            

def bar_graph(title,x_value,y_value,path):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    x = range(len(y_value))

    rects = ax.bar(x, y_value, facecolor='#777777', edgecolor='black',align='center',yerr=0.1,width=0.5)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(x_value)
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/4, 1.01*height, '%s' % float(height))
    #plt.show()
    fig.savefig(path)
 
 