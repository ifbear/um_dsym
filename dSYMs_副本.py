from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
import tkinter.ttk as ttk
import zipfile
import os
import plistlib as pl
import asyncio
import requests


from threading import Thread
from typing import List

from alibabacloud_umeng_apm20220214.client import Client as umeng_apm20220214Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_umeng_apm20220214 import models as umeng_apm_20220214_models
from alibabacloud_tea_util import models as util_models

_path = ""

_apps = [{"name": "app1", "data_source_id": 'APPKey'}, 
         {"name": "app2", "data_source_id": 'APPKey'}]

_app = {}

_accessKeyId = 'apiKey'
_accessKeySecret = 'apiSecurity'

class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> umeng_apm20220214Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # ⚠️您的 AccessKey ID,
            access_key_id=_accessKeyId,
            # ⚠️您的 AccessKey Secret,
            access_key_secret=_accessKeySecret
        )
        # 访问的域名
        config.endpoint = f'apm.openapi.umeng.com'
        return umeng_apm20220214Client(config)

    @staticmethod
    async def main_async(
        args: List[str],
    ) -> None:
        app_version = args[0]
        file_name = args[1]
        client = Sample.create_client('accessKeyId', 'accessKeySecret')
        get_sym_upload_param_request = umeng_apm_20220214_models.GetSymUploadParamRequest(
            app_version=app_version,
            data_source_id=_app['data_source_id'],
            file_name=file_name,
            file_type=3
        )
        headers = {}
        try:
            response = await client.get_sym_upload_param_with_options_async(get_sym_upload_param_request, headers, util_models.RuntimeOptions())
            response_body = response.body.data
            upload_address = response_body.upload_address
            access_key_id = response_body.access_key_id
            key = response_body.key
            policy = response_body.policy
            signature = response_body.signature
            callback = response_body.callback
            zipfile = open(os.path.join(_path, "dSYMs", dsymName()+'.zip'), 'rb')
            res = requests.post(upload_address, 
                          files={'file': zipfile}, 
                          data={"signature": signature, "OSSAccessKeyId": access_key_id, "policy": policy, "key": key, "callback": callback}, 
                          headers={"Context-type": "application/json"})
            if res.ok:
                pText.insert(END, "上传成功\n")
                print("上传成功")
            else:
                pText.insert(END, "上传失败...\n")
                pText.insert(END, res.text)

        except Exception as error:
            # 如有需要，请打印 error
            print(error) 

# 获取版本
def dsymVersion():
    infopath = os.path.join(_path, "Info.plist")
    with open(infopath, 'rb') as ifile:
        info = pl.load(ifile)
    return info["ApplicationProperties"]["CFBundleShortVersionString"]

# dsym name
def dsymName():
    return _app['name']+'.app.dSYM'

# dsym.zip
def zipdsymName():
    return dsymName()+'.zip'

# dsym path
def dsymPath():
    return os.path.join(_path, "dSYMs", dsymName())

# 压缩路径
def zipPath():
    return os.path.join(_path, "dSYMs", zipdsymName())

# 获取dsym文件
def zipDSYMAndUpload():
    dsympath = dsymPath()
    zippath = zipPath()
    z = zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED) #参数一：文件夹名
    for dirpath, dirnames, filenames in os.walk(dsympath):
        fpath = dirpath.replace(dsympath,'') #这一句很重要，不replace的话，就从根目录开始复制
        fpath = fpath and fpath + os.sep or ''#这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
        for filename in filenames:
            z.write(os.path.join(dirpath, filename),fpath+filename)
    z.close()
    pText.insert(END, "压缩完成...\n")

    # 获取版本
    version = dsymVersion()
    pText.insert(END, "版本号:"+version+"\n")
    #2. 压缩上传
    # 上传
    pText.insert(END, "开始上传...\n")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(Sample.main_async([version, zipdsymName()]))
    loop.close()

# 设置回调函数
def selectdSYM(event=None):
    myFileTypes = [('All files', '*')]
    filepath = filedialog.askopenfilename(title="选择", initialdir=os.environ['HOME']+"/Library/Developer/Xcode/Archives/", filetypes=myFileTypes)
    # 激活窗口
    window.deiconify()
    if len(filepath) == 0:
        return
    global _path
    _path = filepath
    pText.insert(END, "选中文件:"+_path+"\n")

# 选择app
def selectRadio(event=None):
    global _app
    _app = list(filter(lambda app: app['name'] == radio_var.get(), _apps))[0]

# 上传
def uploaddSYM(event=None):
    if len(_path) == 0:
        messagebox.showinfo("提示","请先选择dsym文件")
        return
    pText.insert(END, "开始压缩...\n")
    td = Thread(target=zipDSYMAndUpload)
    td.start()

# GUI 

window = Tk()
window.title("dSYMs")
window.resizable(False, False)
# 获取屏幕宽度和高度
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
# 计算窗口左上角坐标
x = (screen_width - 450) // 2
y = (screen_height - 300) // 2
window.geometry("450x300+{}+{}".format(x, y))

# 选择app
radio_var = tk.StringVar()
for app in _apps:
    i = _apps.index(app)
    x = i * 120 + 20
    radio = Radiobutton(window, text=app['name'], variable=radio_var, value=app['name'], command=selectRadio)
    radio.place(x=x, y=20, width=100, height=32)
    if i == 0:
        radio.invoke()

# 选择文件
sBtn = Button(window, text="选择", command=selectdSYM, anchor=CENTER)
sBtn.place(x=260, y=20, height=32, width=60)

# 上传文件
uBtn = Button(window, text="上传", command=uploaddSYM, anchor=CENTER)
uBtn.place(x=340, y=20, height=32, width=60)

# 日志
pText = Text(window)
pText.place(x=20, y=72, width=410, height=208)

window.mainloop()