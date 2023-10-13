### 友盟API上传dYSMs文件


# 一、 背景

每次上传符号表文件需要打开友盟[官网](https://apm.umeng.com/),过程比较繁琐，故借鉴[简书](https://www.jianshu.com/p/2b8c1cbdd17a)上网友提供的命令行工具，开发一款简单的GUI工具，方便上传至[友盟](https://apm.umeng.com/)。

# 二、前期准备

可参见[简书](https://www.jianshu.com/p/2b8c1cbdd17a)中1-5条内容，安装好python环境和依赖库。安装打包工具[pyinstaller](https://pyinstaller.org/en/stable/installation.html),方便将项目打包成app，直接使用。

# 三、克隆

克隆本项目到本地，修改dSYMs.py文件中：`APPKey`、`apiKey`、`apiSecurity`, 参见[简书](https://www.jianshu.com/p/2b8c1cbdd17a)第二部分第5步。将`app1`、`app2`改成你的项目名称，如果项目名为`Github`,打包后生成的dSYM文件名即`Github.app.dSYM`，  `app1`就可以改成`Github`即可。

# 四、打包

打开终端工具,进入项目目录下运行以下命令即可：
```
  pyinstaller --windowed dSYMs.py
```
打包完成后，可在`dist`文件夹下找到打包后的文件。

感谢[简书](https://www.jianshu.com/p/2b8c1cbdd17a)作者的启发

因为第一次写python，代码比较乱，只是为了自己在工作中方便一点，后续有时间学习python再完善。

谢谢。祝好🙏
