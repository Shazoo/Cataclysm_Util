from re import S
import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
import Ui_cdda
import base64
import re


def get_world_folders(game_base):
    world_folders = []
    for item in os.listdir(game_base):
        full_path = os.path.join(game_base, item)
        if os.path.isdir(full_path):
            world_folders.append({'name': item, 'path':full_path})
    return world_folders

def get_charactors(world_folder):
    charactors = []
    for item in os.listdir(world_folder):
        if item.endswith('.sav'):
            name = base64.urlsafe_b64decode(item.split('.')[0]).decode('utf8')
            c = {'name':name, 'path': os.path.join(world_folder, item), 'world':world_folder}
            charactors.append(c)
    return charactors

def get_vehicles(world_folder):
    vehicles = []
    for item in os.listdir(world_folder):
        if m := re.match(r'''o\.(\-?\d+)\.(\-?\d+)''', item):
            omx , omy = m.groups()
            om = load_gamefile(os.path.join(world_folder, item))
            if om['tracked_vehicles'] != []:
                for v in om['tracked_vehicles']:
                    v['omx'] = int(omx)
                    v['omy'] = int(omy)
                    vehicles.append(v) 
    return vehicles

def load_gamefile(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = ''
        for line in f.readlines():
            if line.startswith('#'):
                continue
            else:
                data += line
        return json.loads(data)

def save_gamefile(data, savefile_path):
    with open(savefile_path, 'w' , encoding='utf-8') as f:
        json.dump(data, f)        



def merge_player_data(source, target, clear_bio=False, clear_book=False, clear_task=False):
    # location
    posx = target['posx']
    posy = target['posy']
    known_traps = target['known_traps']
    target = source
    target['posx'] = posx
    target['posy'] = posy
    target['known_traps'] = known_traps
    
    # missions
    if clear_task:
        target['active_mission'] = -1
        target['active_missions'] = []
        target['completed_missions'] = []
        target['failed_missions'] = []

    if clear_bio:
        target['my_bionics'] = []
    
    if clear_book:
        target['items_identified'] = []

    return target

default_folder = os.path.join(os.environ['USERPROFILE'], 'Desktop') if os.environ.get('USERPROFILE') else 'C:/'

class MainForm(QMainWindow, Ui_cdda.Ui_MainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setupUi(self)
        self.export_charactor_savefile_folder = default_folder
        self.import_charactor_savefile_folder = default_folder
        self.export_vehicle_savefile_folder = default_folder
        self.import_vehicle_savefile_folder = default_folder
        self.ed_export_charactor_gamefolder.setText(self.export_charactor_savefile_folder)
        self.ed_import_charactor_gamefolder.setText(self.import_charactor_savefile_folder)
        self.ed_export_vehicle_gamefolder.setText(self.export_vehicle_savefile_folder)
        self.ed_import_vehicle_gamefolder.setText(self.import_vehicle_savefile_folder)
        self.export_charactor_worlds = []
        self.import_charactor_worlds = []
        self.export_vehicle_worlds = []
        self.import_vehicle_worlds = []
        self.char = None
        self.vehicle = None
        onlyint = QIntValidator()
        self.ed_vehicle_omx.setValidator(onlyint)
        self.ed_vehicle_omy.setValidator(onlyint)
        self.ed_vehicle_x.setValidator(onlyint)
        self.ed_vehicle_y.setValidator(onlyint)


    def OnSelectExportCharactorGamefolder(self):
        folderpath = QFileDialog.getExistingDirectory(self, '选择游戏目录', self.export_charactor_savefile_folder)
        savefile_folder = os.path.join(folderpath, 'save')
        if not os.path.exists(savefile_folder):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("所选目录有误，请选择游戏根目录")
            msg.setWindowTitle("目录有误")
            msg.setDetailedText("提示，目录下应该有游戏可执行程序和save、data、config等文件夹")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return 
        self.export_charactor_savefile_folder = savefile_folder
        self.list_export_charactor_world_list.clear()
        self.list_export_char_list.clear()
        self.ed_export_charactor_gamefolder.setText(folderpath)
        self.export_charactor_worlds = get_world_folders(self.export_charactor_savefile_folder)
        for world in self.export_charactor_worlds:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, world['path'])
            item.setText(world['name'])
            self.list_export_charactor_world_list.addItem(item)        
 
    def OnSelectImportCharactorGamefolder(self):
        folderpath = QFileDialog.getExistingDirectory(self, '选择游戏目录', self.import_charactor_savefile_folder)
        savefile_folder = os.path.join(folderpath, 'save')
        if not os.path.exists(savefile_folder):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("所选目录有误，请选择游戏根目录")
            msg.setWindowTitle("目录有误")
            msg.setDetailedText("提示，目录下应该有游戏可执行程序和save、data、config等文件夹")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return 
        self.import_charactor_savefile_folder = savefile_folder
        self.list_import_char_list.clear()
        self.list_import_charactor_world_list.clear()
        self.ed_import_charactor_gamefolder.setText(folderpath)
        self.import_charactor_worlds = get_world_folders(self.import_charactor_savefile_folder)
        for world in self.import_charactor_worlds:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, world['path'])
            item.setText(world['name'])
            self.list_import_charactor_world_list.addItem(item)  


    def OnSelectImportVehicleGamefolder(self):
        folderpath = QFileDialog.getExistingDirectory(self, '选择游戏目录', self.import_vehicle_savefile_folder)
        savefile_folder = os.path.join(folderpath, 'save')
        if not os.path.exists(savefile_folder):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("所选目录有误，请选择游戏根目录")
            msg.setWindowTitle("目录有误")
            msg.setDetailedText("提示，目录下应该有游戏可执行程序和save、data、config等文件夹")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return 
        self.import_vehicle_savefile_folder = savefile_folder
        self.list_import_vehicle_world_list.clear()
        self.ed_import_vehicle_gamefolder.setText(folderpath)
        self.import_vehicle_worlds = get_world_folders(self.import_vehicle_savefile_folder)
        for world in self.import_vehicle_worlds:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, world['path'])
            item.setText(world['name'])
            self.list_import_vehicle_world_list.addItem(item)  



    def OnSelectExportVehicleGameFolder(self):
        folderpath = QFileDialog.getExistingDirectory(self, '选择游戏目录', self.export_vehicle_savefile_folder)
        savefile_folder = os.path.join(folderpath, 'save')
        if not os.path.exists(savefile_folder):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("所选目录有误，请选择游戏根目录")
            msg.setWindowTitle("目录有误")
            msg.setDetailedText("提示，目录下应该有游戏可执行程序和save、data、config等文件夹")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return 
        self.export_vehicle_savefile_folder = savefile_folder
        self.list_export_vehicle_list.clear()
        self.list_export_vehicle_world_list.clear()
        self.ed_export_vehicle_gamefolder.setText(folderpath)
        self.export_vehicle_worlds = get_world_folders(self.export_vehicle_savefile_folder)
        for world in self.export_vehicle_worlds:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, world['path'])
            item.setText(world['name'])
            self.list_export_vehicle_world_list.addItem(item)  


    def OnSelectCharactorTemplate(self):
        char_path, _ = QFileDialog.getOpenFileName(self, '选择保存的角色模板', default_folder, "*.cdda_player")
        if char_path != '':
            self.char = load_gamefile(char_path)
            self.ed_import_charactor_filename.setText(char_path)

    def OnSelectVehicleTemplate(self):
        vehicle_path, _ = QFileDialog.getOpenFileName(self, '选择保存的车辆模板', default_folder, "*.cdda_vehicle")
        if vehicle_path != '':
            self.vehicle = load_gamefile(vehicle_path)
            self.ed_import_vehicle_filename.setText(vehicle_path)
            
    def OnBtnExportCharactorClick(self):
        selected = self.list_export_char_list.selectedItems()
        if not selected:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("请确保选中了要导出的角色")
            msg.setWindowTitle("未选中角色")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return 
        char_path = selected[0].data(Qt.UserRole)
        obj = load_gamefile(char_path)
        if not obj.get('player'):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("文件疑似损坏，请确保已经退出游戏并正常保存")
            msg.setWindowTitle("文件损毁")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return 
        save_file, _ = QFileDialog.getSaveFileName(self, "保存导出角色信息", default_folder, "*.cdda_player")
        if save_file != '':
            save_gamefile(obj.get('player'), save_file)
            self.char = obj.get('player')
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("成功导入")
            msg.setWindowTitle("成功")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()        

    def OnBtnExportVehicleClick(self):
        selected = self.list_export_vehicle_list.selectedItems()
        if not selected:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("请确保选中了要导出的角色")
            msg.setWindowTitle("未选中角色")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return 
        v = selected[0].data(Qt.UserRole)
        vehicle_map_path = f"{v['omx']*180+v['x']}.{v['omy']*180+v['y']}.0.map"
        for root, dirs, files in os.walk(self.export_vehicle_savefile_folder, 'maps'):
            if vehicle_map_path in files:
                data = load_gamefile(os.path.join(root, vehicle_map_path))
                for submap in data:
                    for vehicle in submap['vehicles']:
                        if vehicle['om_id'] == v['id']:
                            save_file, _ = QFileDialog.getSaveFileName(self, "保存导出车辆信息", os.path.join(default_folder, f"{v['name']}.cdda_vehicle"), f"*.cdda_vehicle")
                            if save_file != '':
                                save_gamefile(vehicle, save_file)
                                self.vehicle = vehicle
                                msg = QMessageBox()
                                msg.setIcon(QMessageBox.Information)
                                msg.setText("成功导出")
                                msg.setWindowTitle("成功")
                                msg.setStandardButtons(QMessageBox.Ok)
                                msg.exec() 
                                return
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("未能找到对应车辆数据")
            msg.setWindowTitle("数据丢失")
            msg.setDetailedText("提示，可以尝试保证车辆在角色视线范围内存盘，然后导出。")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return 

    def OnExportCharactorWorldChange(self):
        self.list_export_char_list.clear()
        selected = self.list_export_charactor_world_list.selectedItems()
        if not selected:
            return 
        selected = selected[0]
        world_path = selected.data(Qt.UserRole)
        chars = get_charactors(world_path)
        for char in chars:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, char['path'])
            item.setText(char['name'])
            self.list_export_char_list.addItem(item)

    def OnExportVehicleWorldChange(self):
        self.list_export_vehicle_list.clear()
        selected = self.list_export_vehicle_world_list.selectedItems()
        if not selected:
            return 
        selected = selected[0]
        world_path = selected.data(Qt.UserRole)
        vehicles = get_vehicles(world_path)
        for v in vehicles:
            print(v)
            item = QListWidgetItem()
            item.setData(Qt.UserRole, v)
            item.setText(f"{v['name']}({v['omx']}'{v['x']}, {v['omy']}'{v['y']})")
            self.list_export_vehicle_list.addItem(item)


    def OnImportCharactorWorldChange(self):
        self.list_import_char_list.clear()
        selected = self.list_import_charactor_world_list.selectedItems()
        if not selected:
            return 
        selected = selected[0]
        world_path = selected.data(Qt.UserRole)
        chars = get_charactors(world_path)
        for char in chars:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, char['path'])
            item.setText(char['name'])
            self.list_import_char_list.addItem(item)


    def OnBtnImportCharactorClick(self):
        selected = self.list_import_char_list.selectedItems()
        if not selected:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("请确保选中了要导出的角色")
            msg.setWindowTitle("未选中角色")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return 
        char_path = selected[0].data(Qt.UserRole)
        import_gamedata = load_gamefile(char_path)
        if not import_gamedata.get('player'):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("文件疑似损坏，请确保已经退出游戏并正常保存")
            msg.setWindowTitle("文件损毁")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return 

        target_player = import_gamedata.get('player')
        source_player = self.char
        player = merge_player_data(source_player, 
                            target_player, 
                            self.cb_clearbio.isChecked(),
                            self.cb_clearbook.isChecked(),
                            self.cb_cleartask.isChecked())
        import_gamedata['player'] = player

        save_gamefile(import_gamedata, char_path)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("成功导入")
        msg.setWindowTitle("成功")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()        

    def OnBtnImportVehicleClick(self):
        selected = self.list_import_vehicle_world_list.selectedItems()
        if not selected:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("请确保选中了要导入的世界")
            msg.setWindowTitle("未选中世界")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return 
        world_path = selected[0].data(Qt.UserRole)

        try:
            omx = int(self.ed_vehicle_omx.text())
            omy = int(self.ed_vehicle_omy.text())
            x = int(self.ed_vehicle_x.text())
            y = int(self.ed_vehicle_y.text())
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("请填写车辆导入的地图坐标")
            msg.setWindowTitle("地图坐标有误")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return 


        target_map_path = f"{omx*180+x}.{omy*180+y}.0.map"
        for root, dirs, files in os.walk(os.path.join(world_path, 'maps')):
            if target_map_path in files:
                map = load_gamefile(os.path.join(root, target_map_path))
                map[0]['vehicles'].append(self.vehicle)
                save_gamefile(map, os.path.join(root, target_map_path))
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("成功导入")
                msg.setWindowTitle("成功")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()   
                return 
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("未能找到对应地图数据")
            msg.setWindowTitle("数据丢失")
            msg.setDetailedText("提示，可以尝试保证该坐标在角色视线范围内存盘，然后导出。")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

def main():
    app = QApplication(sys.argv)
    ui = MainForm()
    ui.show()
    sys.exit(app.exec())
 

if __name__ == '__main__':
    main()