# Cataclysm_Util
Here is the Cataclysm: Dark Days Ahead, aka CDDA , Player and Vehicle cross world transfer tool . 

大灾变（cdda）辅助工具。可以跨世界跨版本导入导出角色和车辆。

## How to use it ?（如何使用？）

![](https://9527-1259377398.cos.ap-beijing.myqcloud.com/typora_picgo_images/image-20220407131902543.png)

![](https://9527-1259377398.cos.ap-beijing.myqcloud.com/typora_picgo_images/image-20220407132534220.png)

## How to build it （如何编译程序）

### environment build （环境搭建）

```
python -m venv venv
venv\scripts\activate
python -m pip install -U pip # test under python3.8.2~python3.8.10
pip install -r requirements.txt
```

### compile the res/ui file （资源文件和UI文件编译）

```
venv\Scripts\pyrcc5.exe cdda.qrc
venv\Scripts\pyuic5.exe cdda.ui
```

### run the script （执行程序）

```
python cdda.py
```

### build the exe file （创建可执行程序）

```
pyinstaller -F -w -i res\cataicon.icon cdda.py
```

 

