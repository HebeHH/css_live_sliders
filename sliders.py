import threading
from Tkinter import *
import time, re, copy, sys, os
from tkColorChooser import askcolor   

from livereload import Server, shell

def serve_html ():
    server = Server()
    server.watch(css_file)
    server.serve(open_url_delay=1)

def write_change():
    rewrite = open(css_file, 'w')
    rewrite.writelines(css)
    rewrite.close()

def replacenth(s, sub, repl, nth):
    cur_val = re.findall(sub, s)[nth][1]
    if cur_val == 'auto':
    	repl += 'px'
    print repl
    print s 
    print cur_val
    return repl.join(s.split(cur_val))

def changeColor(line_idx):
	color = askcolor()[1]
	css[line_idx] = re.sub(r':.+;', color,css[line_idx])
	write_change()

def changeInt(line_idx, var, k):
    css[line_idx] = replacenth(css[line_idx], re.compile(r'([0-9][0-9\.]*)|(auto)'), str(var.get()), k)
    write_change()


def resetStyling():
    with open(css_file, 'w') as write_file:
        with open(dupl_file, 'r') as read_file:
            write_file.writelines(read_file.readlines())

def saveStyling():
    with open('adjusted_css.css', 'w') as f:
        f.writelines(css)

r = 3
showing = []

def showStyles(*args):
	global showing
	for item in showing:
		item.grid_remove()

	showing = selectors[selector.get()]

	for gadget in selectors[selector.get()]:
		gadget.grid()

def makeStyleSlider(line, idx):
	global r
	tag = Label(root, text = line)
	tag.grid(column=1,columnspan=4, row = r+1, rowspan = 2)
	tag.grid_remove()
	ls = [tag]
	j = 0
	for cv in re.findall(r'([0-9][0-9\.]*)|(auto)', line):
		ls += newSlider(cv[0], idx, j)
		j+=1
	return ls

def changeScale(event, label, scale, _from = True):
	curr_bound = int(label['text']) - event.delta
	print 'hi'
	label['text'] = curr_bound
	if _from:
		scale.configure(_from=curr_bound)
	else:
		scale.configure(to=curr_bound)


def newSlider(cv, idx, int_idx):
    global r
    print cv
    v = DoubleVar()
    try:
    	o = float(cv)
    except:
    	o = 24
    l = Label(root, text="0", bg = 'grey', fg= 'white')
    l.grid(row=r, column = 6)
    l.bind("<MouseWheel>", lambda e: changeScale(e, l, scale))
    l.grid_remove()

    scale = Scale(root, variable = v, orient=HORIZONTAL,
        from_=0, to=10*(o+1), resolution=0.01, bg= 'grey')
    scale.bind("<ButtonRelease-1>", lambda x: changeInt(idx, v, int_idx))
    scale.grid(column=8,columnspan=8, row = r, rowspan = 2, ipadx = 5)

    u = Label(root, text=str(int(10*(o+1))), bg = 'grey', fg= 'white')
    u.grid(row=r, column = 19)
    u.bind("<MouseWheel>", lambda e: changeScale(e, u, scale, _from = False))
    u.grid_remove()
    scale.grid_remove()
    r += 2
    return [l, scale, u]

def makeColPicker(line, idx):
	global r 
	tag = Label(root, text = line)
	tag.grid(column=1,columnspan=4, row = r)
	tag.grid_remove()
	color_button = Button(root, text='Select Color', command=lambda: changeColor(idx))
	color_button.grid(column=7,columnspan=4, row = r)
	color_button.grid_remove()
	r += 2
	return [tag, color_button]


def cleanup():
	saveStyling()
	resetStyling()
	if os.path.exists(dupl_file):
		os.remove(dupl_file)


if __name__ == '__main__':
	try:
	    css_file = sys.argv[1]

	    with open(css_file, 'r') as f:
	        css = f.readlines()

	    dupl_file = 'original_css_copy.css'
	    with open(dupl_file, 'w') as f:
	        f.writelines(css)

	    root = Tk()
	    root.geometry("500x500")

	    selectors = {}
	    selector = ''
	    styles = []
	    i = 0
	    for line in css:
	        if '{' in line:
	            styles = []
	            r=3
	            selector = re.split('{', line)[0]
	        elif re.search('color', line):
	            styles += makeColPicker(line, i)
	        elif re.search(r'(margin)|(padding)|([0-9][0-9\.]*)', line):
	        	styles += makeStyleSlider(line, i)
	        elif '}' in line:
	            if len(styles) > 0:
	                selectors[selector] = styles
	        i += 1

	    selector = StringVar(root)
	    selector.set(selectors.keys()[0])
	    selector.trace('w', showStyles)
	    selectors_menu = OptionMenu(root, selector, *selectors.keys())
	    selectors_menu.grid(column=1,columnspan=12, row = 0)

	    reset = Button(root, text="Reset", command=resetStyling)
	    reset.grid(column=1,columnspan=3, row = 1)
	    save = Button(root, text="Save", command=saveStyling)
	    save.grid(column=4,columnspan=3, row = 1)
	    


	    newthread = threading.Thread(target=serve_html )
	    newthread.setDaemon(True)
	    newthread.start()
	    root.mainloop()

	    cleanup()

	except KeyboardInterrupt:
		cleanup()

	sys.exit(0)

