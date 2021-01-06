# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:33:55 2020

@author: zhujuxing
"""

import tkinter as tk



def makeform(root, pars):
   entries = []
   for field in pars:
      row = tk.Frame(root)
      lab = tk.Label(row, width=16, text=field, anchor='w')
      ent = tk.Entry(row)
      row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5,expand=tk.YES)
      # row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
      lab.pack(side=tk.LEFT)
      ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
      entries.append((field, ent))
   return entries




if __name__ == '__main__':
    root = tk.Tk()
    root.title('基于网络演化的云化虚拟网络可靠性评估软件')
 
    sof_name = tk.Label(root,text='基于网络演化的云化虚拟网络可靠性评估软件')
    sof_name.pack(side=tk.TOP,fill=tk.X)
    
    panel = tk.Frame(root)
    panel.pack(side=tk.TOP,fill=tk.X)

    panel_left = tk.Frame(panel)
    panel_left.pack(side=tk.LEFT,fill=tk.Y)

    panel_right = tk.Frame(panel)
    panel_right.pack(side=tk.RIGHT,fill=tk.Y)

    panel_input = tk.LabelFrame(panel_left,text='输入面板')
    panel_input.pack(side=tk.TOP,fill=tk.X)
    ents_input = makeform(panel_input,('网络信息输入文件','计算周期','计算次数'))

    panel_func = tk.LabelFrame(panel_left,text='功能面板')
    panel_func.pack(side=tk.TOP,fill=tk.X)

    panel_out = tk.LabelFrame(panel_right,text='输出面板')
    panel_out.pack(side=tk.TOP,fill=tk.X)



    root.mainloop()