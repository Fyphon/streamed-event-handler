
import tkinter as tk # python 3
import tkinter.ttk as ttk

fuTxt = 'Connected functional Units: %d'
class View:
    def __init__(self, root, model):
        self.frame = tk.Frame(root, borderwidth=6)
        self.model = model

        aframe = tk.LabelFrame(self.frame, 
                               text="Admin")
        aframe.pack()
        tt = tk.Label(aframe, text="Listening on: %s"%model.getHost(), justify = tk.RIGHT, padx = 20)
        tt.pack()
        self.numFu = tk.Label(aframe, text=fuTxt%0, justify = tk.RIGHT, padx = 20)
        self.numFu.pack()
        
        labelframe = tk.LabelFrame(self.frame, text="Functional Unit selector")

        self.fuId = tk.StringVar()                       
        self.fuChosen = ttk.Combobox(labelframe, 
                                    width=36, height=6,
                                    textvariable=self.fuId,
                                    state="readonly",
                                    )
        
        self.fuDict = self.model.getFuList()
        self.fuChosen['values'] = ('No_selected_FUs')#list(self.fuDict) 
        self.fuChosen.current(0)                  
        self.fuChosen.bind("<<ComboboxSelected>>", self.ChangeFu)
        self.fuChosen.pack()

        self.fuDesc = tk.Label(labelframe, text="No FU selected.")
        self.fuDesc.pack()
        buttonDisconnect=tk.Button(labelframe, height=1, width=10, text="Disconnect", 
                    command=self.disconnect)
        buttonDisconnect.pack()

        labelframe.pack()

        labelframe2 = tk.LabelFrame(self.frame, text="Config Options")
        self.opts = tk.StringVar()                       
        
        self.confChosen = ttk.Combobox(labelframe2, 
                                    width=20, height=6,
                                    textvariable=self.opts,
                                    )  # state="readonly", )
        
        self.fuConf = {}
        self.confChosen['values'] = ('No_option_selected') 
        self.confChosen.current(0)                  
        self.confChosen.bind("<<ComboboxSelected>>", self.ChangeConf)
        self.confChosen.pack()

        self.futextBox=tk.Text(labelframe2, height=3, width=40)
        self.futextBox.pack()
        buttonCommit=tk.Button(labelframe2, height=1, width=10, text="Send", 
                    command=self.retrieve_input)
        buttonCommit.pack()
        #buttonForce=tk.Button(labelframe2, height=1, width=10, text="Force", 
        #            command=self.update_defaults)
        #buttonForce.pack()
        labelframe2.pack()

        self.fuConfVal = tk.Label(labelframe2, text="No option selected.")
        self.fuConfVal.pack()

        labelframe3 = tk.LabelFrame(self.frame, text="Progress Report")
        labelframe3.pack()
        self.progRep = tk.StringVar()                       
        self.progRepBox=tk.Text(labelframe3, height=3, width=45)
        self.progRepBox.pack()

        self.frame.pack()
        self.showNumFu()
        
    def retrieve_input(self):
        ''' get text from input box '''
        inputValue=self.futextBox.get("1.0","end-1c")
        #print('Got txt'+inputValue)
        fu = int(self.fuId.get().split('-')[0])
        opt = self.opts.get()
        self.model.updateConfig(fu, opt, inputValue)
        
    def update_defaults(self):
        ''' get text from input box '''
        inputValue=self.futextBox.get("1.0","end-1c")
        #print('Got txt'+inputValue)
        fu = int(self.fuId.get().split('-')[0])
        opt = self.opts.get()
        self.model.updateDefaults(fu, opt, inputValue)
        
    def showNumFu(self):
        ''' calls itself every 2 seconds '''
        changed = self.model.doStuff()
        self.updateProg()
        if changed:
            self.fuDict = self.model.getFuList()
            self.fuChosen['values'] = ['{} - {}'.format(k,v) for k,v in self.fuDict.items()]  
            self.numFu.config(text = fuTxt%self.model.getNumFu())
        self.frame.after(2000, self.showNumFu)
                
    def ChangeFu(self, event):
        fu = int(self.fuId.get().split('-')[0])
        #print(self.fuDict)
        txtStr = """%s: %s """%(fu,self.fuDict[fu])
        self.fuDesc.config(text = self.fuDict[fu])
        self.attrl = self.model.getFuConfig(fu)
        #print(self.attrl)
        self.confChosen['values'] = list(self.attrl)
        self.fuConfVal.config(text = txtStr)

    def disconnect(self):
        fu = int(self.fuId.get().split('-')[0])
        self.model.disconnect(fu)
        
    def ChangeConf(self, event):
        opt = self.opts.get()        
        vall = self.attrl[opt]
        self.futextBox.delete(1.0, tk.END)
        self.futextBox.insert(tk.END, vall)
        
    def updateProg(self):
        try:
            fu = int(self.fuId.get().split('-')[0])
            txtStr = self.model.getProg(fu)
            if txtStr:
                self.progRepBox.delete(1.0, tk.END)
                self.progRepBox.insert(tk.END, txtStr)
        except ValueError:
            pass # no FU has been selected yet
        
class tstModel():
    def __init__(self):
        self.numFu = 1
    def doStuff(self):
        pass
    def getNumFu(self):
        self.numFu += 1
        return self.numFu
    def getFuList(self):
        fuList = {}
        for i in range(self.numFu):
            fuList[str(i)] = 'A FU numbered %d'%i
        return fuList
    
if __name__ == '__main__':
    root = tk.Tk()
    m = tstModel()
    v = View(root, m)
    root.mainloop()
    
    
