from bokeh.io import output_notebook, output_file, show
from bokeh.plotting import figure
import numpy as np
 
p = figure(plot_width=800, plot_height=800)
# 方框
p.square(np.random.randint(1,10,5), np.random.randint(1,10,5), size=20, color="navy")

# 圆形
p.circle(np.random.randint(1,10,5), np.random.randint(1,10,5), size=10, color="green")

show(p)
