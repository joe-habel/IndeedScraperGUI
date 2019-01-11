import tkinter as Tk
import tkinter.filedialog as filedialog
from tkinter import messagebox
import os
import pandas as pd
import queue, threading
import json
from indeed import job_search



class IndeedGUI:
    def __init__(self,master,q1,q2,q3):
        #Multithreading Queue
        self.loc_queue = q1
        self.pos_queue = q2
        self.done = q3
        #Def Needed Variables For Running The Script
        self.positions = []
        self.locations = []
        self.max_postings = 100
        self.save_dir = os.getcwd()
        self.current_position = None
        self.current_location = None
        self.wait_time = 1000
        self.finished_jobs = None
        
        #Graphical inits
        self.master = master
        master.title("Indeed Scraper")
        self.position_label = Tk.Label(master, text="Job Titles")
        self.position_label.grid(row=0,column=0)
        self.position_frame = Tk.Frame(master)
        self.position_frame.grid(row=0,column=1)
        self.position_entries = [Tk.Entry(self.position_frame)]
        self.position_entries[0].grid(row=0,column=0)
        self.add_position_btn = Tk.Button(master,text = 'Add Title', command=self.add_position)
        self.add_position_btn.grid(row=0,column=2)
        self.location_label = Tk.Label(master, text='City, State')
        self.location_label.grid(row=1,column=0)
        self.location_frame = Tk.Frame(master)
        self.location_entries = [Tk.Entry(self.location_frame)]
        self.add_location_btn = Tk.Button(master, text = 'Add Location', command=self.add_location)
        self.state_entries = [Tk.Entry(self.location_frame)]
        self.location_entries[0].grid(row=0,column=0)
        self.state_entries[0].grid(row=0,column=3)
        self.location_frame.grid(row=1,column=1)
        self.add_location_btn.grid(row=1,column=2)
        self.max_def = Tk.StringVar(master)
        self.max_def.set(str(self.max_postings))
        self.max_label = Tk.Label(master,text='Max Job Postings')
        self.max_label.grid(row=2,column=0)
        self.max_entry = Tk.Entry(master, textvariable=self.max_def)
        self.max_entry.grid(row=2,column=1)
        self.save_loc_label = Tk.Label(master, text="Excel Save Location")
        self.save_loc_label.grid(row=3,column=0)
        self.save_frame = Tk.Frame(master)
        self.save_def = Tk.StringVar(master)
        self.save_def.set(self.save_dir)
        self.save_entry = Tk.Entry(self.save_frame, textvariable=self.save_def)
        self.save_entry.config(state='readonly')
        self.save_btn = Tk.Button(self.save_frame, text = 'Browse', command=self.get_dir)
        self.save_entry.grid(row=0,column=0)
        self.save_btn.grid(row=0,column=4)
        self.save_frame.grid(row=3,column=1)
        self.bottom_btn_frame_l = Tk.Frame(master)
        self.run_btn = Tk.Button(self.bottom_btn_frame_l, text= 'Run', command = self.run)
        self.run_btn.grid(row=0,column=0)
        self.clear_btn = Tk.Button(self.bottom_btn_frame_l, text = 'Clear', command = self.clear_search)
        self.clear_btn.grid(row=0,column=1)
        self.bottom_btn_frame_l.grid(row=4,column=1)
        self.bottom_btn_frame_r = Tk.Frame(master)
        self.bottom_btn_frame_r.grid(row=4,column=2)
        self.save_search = Tk.Button(self.bottom_btn_frame_r, text= 'Save Search', command = self.save_search)
        self.save_search.grid(row=0,column=1)
        self.open_search = Tk.Button(self.bottom_btn_frame_r, text = 'Open Search', command = self.open_search)
        self.open_search.grid(row=0,column=0)
        
    def add_position(self):
        if self.position_entries[-1].get() == '':
            return
        self.positions.append(self.position_entries[-1].get())
        self.position_entries[-1].config(state='readonly')
        self.position_entries.append(Tk.Entry(self.position_frame))
        self.position_entries[-1].grid(row=len(self.position_entries)-1,column=0)
        self.master.update_idletasks()
        
    def add_location(self):
        if self.location_entries[-1].get() == '':
            return
        if self.state_entries[-1].get() == '':
            return
        city = self.location_entries[-1].get()
        state = self.state_entries[-1].get()
        self.locations.append((city,state))
        self.location_entries[-1].config(state='readonly')
        self.state_entries[-1].config(state='readonly')
        self.location_entries.append(Tk.Entry(self.location_frame))
        self.state_entries.append(Tk.Entry(self.location_frame))
        self.location_entries[-1].grid(row=len(self.location_entries)-1,column=0)
        self.state_entries[-1].grid(row=len(self.location_entries)-1,column=3)
        self.master.update_idletasks()
        
    def get_dir(self):
        self.save_dir = filedialog.askdirectory(initialdir=os.getcwd(),title="Please select where you wish for the excel spreadsheets to be saved.")
        self.save_def.set(self.save_dir)
        self.master.update_idletasks()
        
    def run(self):
        if not os.path.isdir(self.save_dir):
            error_pop = Tk.Toplevel()
            error_pop.title(error_pop,"ERROR")
            dir_error = Tk.Label(error_pop, text = '''The save directory you have entered doesnot appear to exist. Please select a new directory and try again.''')
            dir_error.pack()
            return
        if not self.max_entry.get().isdigit():
            error_pop = Tk.Toplevel()
            error_pop.title("ERROR")
            dir_error = Tk.Label(error_pop,text = '''Your maximum number of postings should be  an integer value. Please enter an integer and try again.''')
            dir_error.pack()
            return
        new_pos = self.position_entries[-1].get()
        if new_pos != '':
            self.positions.append(new_pos)
            self.position_entries[-1].config(state='readonly')
        new_city = self.location_entries[-1].get()
        new_state = self.state_entries[-1].get()
        if new_state != '' and new_city != '':
            self.locations.append((new_city,new_state))
            self.location_entries[-1].config(state='readonly')
            self.state_entries[-1].config(state='readonly')
        if len(self.locations) < 1:
            self.locations = [(None,None)]
        if len(self.positions) < 1:
            return
        if self.current_position is None:
            #Disable Buttons
            self.run_btn['state'] = Tk.DISABLED
            self.add_location_btn['state'] = Tk.DISABLED
            self.add_position_btn['state'] = Tk.DISABLED
            self.save_btn['state'] = Tk.DISABLED
            self.master.protocol("WM_DELETE_WINDOW", self.warn)
            
            self.prog_window = Tk.Toplevel()
            self.prog_window.title("Progress")
            self.prog_window.protocol("WM_DELETE_WINDOW", self.no_close)
            max_res = int(self.max_entry.get())
            curr_p = Tk.Label(self.prog_window, text = 'Current Position: ')
            curr_p.grid(row=0,column=0)
            self.current_position = Tk.StringVar(self.prog_window)
            self.current_position.set("None")
            self.pos = Tk.Label(self.prog_window,textvariable=self.current_position)
            self.pos.grid(row=0,column=1)
            curr_l = Tk.Label(self.prog_window, text =  "Current Location: ")
            curr_l.grid(row=1,column=0)
            self.current_location = Tk.StringVar(self.prog_window)
            self.current_location.set("None")
            self.loc = Tk.Label(self.prog_window, textvariable=self.current_location)
            self.loc.grid(row=1,column=1)
            self.prog_window.update_idletasks()
            ThreadedTask(self.pos_queue,self.loc_queue,self.done,self.positions,self.locations,max_res,self.save_dir).start()
            self.master.after(1000,self.look_for_vals)    
            
    
    def open_search(self):
        self.clear_search()
        filename = filedialog.askopenfilename(filetypes=[("Job Search File", "*.jsearch")])
        if filename.find('.jsearch') < 0:
            error_pop = Tk.Toplevel()
            error_pop.title(error_pop,"ERROR")
            dir_error = Tk.Label('''The selected file was not a .jsearch file.''')
            dir_error.pack()
            return
        with open(filename, 'r') as jsearch:
            json_str = jsearch.read()
            
        info = json.loads(json_str)
        for position in info['positions']:
            self.position_entries[-1].insert(0,position)
            self.positions.append(position)
            self.position_entries[-1].config(state='readonly')
            self.position_entries.append(Tk.Entry(self.position_frame))
            self.position_entries[-1].grid(row=len(self.position_entries)-1,column=0)
        for i,city in enumerate(info['cities']):
            state = info['states'][i]
            self.location_entries[-1].insert(0,city)
            self.state_entries[-1].insert(0,state)
            self.locations.append((city,state))
            self.location_entries[-1].config(state='readonly')
            self.state_entries[-1].config(state='readonly')
            self.location_entries.append(Tk.Entry(self.location_frame))
            self.state_entries.append(Tk.Entry(self.location_frame))
            self.location_entries[-1].grid(row=len(self.location_entries)-1,column=0)
            self.state_entries[-1].grid(row=len(self.location_entries)-1,column=3)
        self.max_entry.delete(0,Tk.END)
        self.max_entry.insert(0,str(info['max']))
        self.max_def = info['max']
        self.save_dir = info['savedir']
        self.save_entry.delete(0,Tk.END)
        self.save_entry.insert(0,self.save_dir)
        self.master.update_idletasks()
        
    def save_search(self):
        if not os.path.isdir(self.save_dir):
            error_pop = Tk.Toplevel()
            error_pop.title(error_pop,"ERROR")
            dir_error = Tk.Label(error_pop,text = '''The save directory you have entered does not appear to exist. Please select a new directory and try again.''')
            dir_error.pack()
            return
        if not self.max_entry.get().isdigit():
            error_pop = Tk.Toplevel()
            error_pop.title("ERROR")
            dir_error = Tk.Label(error_pop,text = '''Your maximum number of postings should be an integer value. Please enter an integer and try again.''')
            dir_error.pack()
            return
        new_pos = self.position_entries[-1].get()
        if new_pos != '':
            self.positions.append(new_pos)
            self.position_entries[-1].config(state='readonly')
        new_city = self.location_entries[-1].get()
        new_state = self.state_entries[-1].get()
        if new_state != '' and new_city != '':
            self.locations.append((new_city,new_state))
            self.location_entries[-1].config(state='readonly')
            self.state_entries[-1].config(state='readonly')
        if len(self.positions) < 1:
            error_pop = Tk.Toplevel()
            error_pop.title("ERROR")
            dir_error = Tk.Label(error_pop,text = '''You need more than 1 position listed to save a job search. ''')
            dir_error.pack()
            return
        filename = filedialog.asksaveasfilename(defaultextension=".jsearch", filetypes=(("Job Search File", "*.jsearch"),("All Files", "*.*")))
        info = {}
        info['positions'] = self.positions
        cities,states = zip(*self.locations)
        info['cities'] = cities
        info['states'] = states
        info['max'] = self.max_entry.get()
        info['savedir'] = self.save_dir
        json_str = json.dumps(info)
        with open(filename, 'w') as jsearch:
            jsearch.write(json_str)
            
        
    def no_close(self):
        return
    
    def normal(self):
        self.master.destroy()
    
    def warn(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit? Indeed is still be searched."):
            self.master.destroy()
        
    
    def create_exit(self):
        self.exit_button = Tk.Button(self.prog_window, text = "Continue", command=self.prog_window.destroy)
        self.exit_button.grid(row=2,column=1)
        self.new_search_button = Tk.Button(self.prog_window, text = "New Search", command=self.clear_search)
        self.new_search_button.grid(row=2,column=0)
        self.run_btn['state'] = Tk.NORMAL
        self.add_location_btn['state'] = Tk.NORMAL
        self.add_position_btn['state'] = Tk.NORMAL
        self.save_btn['state'] = Tk.NORMAL
        self.master.protocol("WM_DELETE_WINDOW", self.normal)
        self.prog_window.update_idletasks()
    
    def clear_search(self):
        self.locations = []
        self.positions = []
        for entry in self.position_entries:
            entry.destroy()
        for entry in self.location_entries:
            entry.destroy()
        for entry in self.state_entries:
            entry.destroy()
        self.position_entries = [Tk.Entry(self.position_frame)]
        self.position_entries[0].grid(row=0,column=0)
        self.location_entries = [Tk.Entry(self.location_frame)]
        self.state_entries = [Tk.Entry(self.location_frame)]
        self.location_entries[0].grid(row=0,column=0)
        self.state_entries[0].grid(row=0,column=3)
        self.master.update_idletasks()

    
    
    def look_for_vals(self):
        if self.done.empty():
            if self.pos_queue.empty():
                if self.loc_queue.empty():
                    self.prog_window.after(1000,self.look_for_vals)
                else:
                    new_loc = self.loc_queue.get(0)
                    self.current_location.set(new_loc)
                    self.prog_window.update_idletasks()
                    self.prog_window.after(1000,self.look_for_vals)
            else:
                new_pos = self.pos_queue.get(0)
                self.current_position.set(new_pos)
                self.prog_window.update_idletasks()
                if self.loc_queue.empty():
                    self.prog_window.after(1000,self.look_for_vals)
                else:
                    new_loc = self.loc_queue.get(0)
                    self.current_location.set(new_loc)
                    self.prog_window.update_idletasks()
                    self.prog_window.after(1000,self.look_for_vals)
        else:
            self.create_exit()
            
    
class ThreadedTask(threading.Thread):
    def __init__(self,q1,q2,q3,positions,locations,max_postings,jobdir):
        threading.Thread.__init__(self)
        self.q1 = q1
        self.q2 = q2
        self.q3 = q3
        self.positions = positions
        self.locations = locations
        self.max_postings = max_postings
        self.jobdir = jobdir
    
    def run(self): 
        for position in self.positions:
            self.q1.put(position)
            writer = pd.ExcelWriter(self.jobdir + '/%s.xlsx'%position)
            for location in self.locations:
                self.q2.put(location[0])
                jobs = job_search(position,self.max_postings,location[0],location[1])
                job_df = pd.DataFrame.from_records([job.to_dict() for job in jobs])
                job_df.to_excel(writer,location[0])
            writer.save()
        q3.put("complete")
    

            
root = Tk.Tk()
q1 = queue.Queue()
q2 = queue.Queue()
q3 = queue.Queue()
gui = IndeedGUI(root,q1,q2,q3)
root.mainloop()