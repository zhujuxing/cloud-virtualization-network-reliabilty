# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:33:55 2020

@author: zhujuxing
"""

import tkinter as tk



def makeform(root, pars):
    '''
    该函数为一个制造若干列label与entry控件的函数。

    Parameters
    ----------
    root : 父控件类型
    pars : 每列Label的文字内容。

    Returns
    -------
    entries : List
        DESCRIPTION.

    '''
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

def cal_single_app_avail(e):
    pass

def cal_multi_app_avail(e):
    pass

def output_avail_file(e):
    pass


if __name__ == '__main__':
    root = tk.Tk()
    root.title('基于网络演化的云化虚拟网络可靠性评估软件')
 
    sof_name = tk.Label(root,text='基于网络演化的云化虚拟网络可靠性评估软件')
    sof_name.pack(side=tk.TOP,fill=tk.X)
    
    frame = tk.Frame(root)
    frame.pack(side=tk.TOP,fill=tk.X)

    frame_left = tk.Frame(frame)
    frame_left.pack(side=tk.LEFT,fill=tk.Y)

    frame_right = tk.Frame(frame)
    frame_right.pack(side=tk.RIGHT,fill=tk.Y)

    frame_input = tk.LabelFrame(frame_left,text='输入面板')
    frame_input.pack(side=tk.TOP,fill=tk.X)
    ents_input = makeform(frame_input,('网络信息输入文件','计算周期','计算次数'))

    frame_func = tk.LabelFrame(frame_left,text='功能面板')
    frame_func.pack(side=tk.TOP,fill=tk.X)
    
    button_cal_single = tk.Button(frame_func,text='单业务可靠度计算')
    button_cal_single.pack(side=tk.LEFT,fill=tk.X)
    button_cal_single.bind("<Button-1>",(lambda event, e=ents_input:cal_single_app_avail(e)))
    
    button_cal_multi = tk.Button(frame_func,text='整网业务可靠度计算')
    button_cal_multi.pack(side=tk.LEFT,fill=tk.X)
    button_cal_multi.bind("<Button-1>",(lambda event, e=ents_input:cal_multi_app_avail(e)))
    
    button_output_file = tk.Button(frame_func,text='输出计算结果文件')
    button_output_file.pack(side=tk.LEFT,fill=tk.X)
    button_output_file.bind("<Button-1>",(lambda event, e=ents_input:output_avail_file(e)))
    
    frame_out = tk.LabelFrame(frame_right,text='输出面板')
    frame_out.pack(side=tk.TOP,fill=tk.X)
    
    label_result_sig = tk.Label(frame_out,width=52,text='单业务可靠度计算结果')
    label_result_sig.pack(side=tk.TOP)
    
    text_result_sig = tk.Text(frame_out,width=52,height=6)
    text_result_sig.pack(side=tk.TOP)
    # text_result_sig.insert('insert','111')
    
    frame_out_mul = tk.Frame(frame_out)
    frame_out_mul.pack(side=tk.TOP,fill=tk.X)
    
    label_result_mul = tk.Label(frame_out_mul,width=25,text='多业务可靠度计算结果')
    label_result_mul.pack(side=tk.LEFT)
    
    text_result_mul = tk.Text(frame_out_mul,width=26,height=1)
    text_result_mul.pack(side=tk.LEFT)

    root.mainloop()