# !/usr/bin/env python
#  -*- coding: utf-8 -*-
""" 
Страницы визарда инсталятора.
"""
__version__ = '0.01'

#--- Imports ---
import sys
import os
import shutil

import wx
import wx.wizard

import util

#--- Constants ---
INSTALL_PACKAGES_DIR_DEFAULT='/packages/'

#Режимы доступа к инсталлируемым файлам/папкам
PUBLIC_MODE='public'
PROTECT_MODE='protect'

#--- Functions ---
def makeStdPageTitle(wizPg, title):
    """
    Функция стандартного создания заголовка страницы
    """
    sizer = wx.BoxSizer(wx.VERTICAL)
    wizPg.SetSizer(sizer)
    title = wx.StaticText(wizPg, -1, title)
    title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
    sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND|wx.ALL, 5)
    return sizer

#--- Classes ---
class icPackageControlPage(wx.wizard.PyWizardPage):
    """
    Страница проверки установленных пакетов и их версий.
    Если контрольпакетов не проходит, то переход на следующую страницу блокируется, 
    т.к. нет смысла продолжать инсталяцию.
    """
    def __init__(self, parent, title, Packages_=None):
        """
        Конструктор.
        @param parent: Родительский визард, в который вставляется страница.
        @param title: Заголовок страницы.
        @param Package_: Описательная структура проверки наличия python пакетов.
        Формат:
        {
        'имя пакета':{
            'type':'py' или 'pkg',
            'ver':'версия',
            'compare':'условие проверки'
            }
        }
        """
        
        wx.wizard.PyWizardPage.__init__(self, parent)
        
        self.next = None
        self.prev = None
        
        self.sizer = makeStdPageTitle(self, title)

        #Создание списка пакетов
        self.package_list=wx.ListCtrl(self, -1, 
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.LC_REPORT|wx.BORDER_NONE|wx.LC_EDIT_LABELS|wx.LC_SORT_ASCENDING)
            
        self.sizer.Add(self.package_list, 1, wx.EXPAND|wx.GROW, 5)
        
        #Колонки списка пакетов
        info=wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT|wx.LIST_MASK_IMAGE|wx.LIST_MASK_FORMAT
        info.m_image = -1
        info.m_format = 0
        info.m_text = u'Имя пакета'
        self.package_list.InsertColumnInfo(0, info)
        self.package_list.SetColumnWidth(0,200)
        
        info.m_text = u'Версия'
        self.package_list.InsertColumnInfo(1, info)
        self.package_list.SetColumnWidth(1,70)
        
        #Данные списка пакетов
        self.result=True
        if Packages_:
            i=0
            for package_name,package_misc in Packages_.items():
                if 'type' in package_misc:
                    package_type=package_misc['type']
                else:
                    package_type='py'                    

                #Определение версии
                if 'ver' in package_misc:
                    package_ver=package_misc['ver']
                else:
                    package_ver=''
                if 'compare' in package_misc:
                    package_compare=package_misc['compare']
                else:
                    package_compare='=='                    

                index = self.package_list.InsertStringItem(sys.maxint,package_name)
                self.package_list.SetStringItem(index,1,package_ver)
                #Проверка наличия пакетов
                item=self.package_list.GetItem(i)
                
                if package_type=='py':
                    result=util.check_python_library_version(package_name,package_ver,package_compare)
                elif package_type=='pkg':
                    result=util.check_linux_package(package_name,package_ver,package_compare)
                    
                self.result=self.result and result
                #print result
                if result:
                    item.SetTextColour(wx.Colour(0,100,0))
                else:
                    item.SetTextColour(wx.RED)
                self.package_list.SetItem(item)
                i+=1
                    

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        """
        Если все библиотеки присутствуют, то перейти на следующую страницу,
        иначе пропустить следующую страницу.
        """
        if not self.result:
            self.SetNext(None)
        return self.next
        
    def GetPrev(self):
        return self.prev
    
def add_wizard_package_control_page(Wizard_,*args,**kwargs):
    """
    Добавить страницу проверки установленных пакетов в визард.
    @param Wizard_: Объект главного визарда.
    @return: Созданный объект страницы или None в случае ошибки.
    """
    page=icPackageControlPage(Wizard_,u'Проверка пакетов',*args,**kwargs)
    Wizard_.appendPage(page)
    return page    

class icProgrammInstallPage(wx.wizard.PyWizardPage):
    """
    Страница выбора установки программ.
    """
    def __init__(self, parent, title, Programm_=None):
        """
        Конструктор.
        @param parent: Родительский визард, в который вставляется страница.
        @param title: Заголовок страницы.
        @param Programm_: Описательная структура указания устанавливаемых программ.
        [
            {
            'programm':'инсталяционный файл устанавлеемой программы',
            'dir':'инсталяционная папка программы',
            'pth':{
                'name':'имя генерируемого pth-файла',
                'dir':'указание папки, которую содержит pth-файл',
                'var':'пересенная из окружения визарда, которая содержит путь до папки',
                },
            },
        ...
        ]
        """
        
        wx.wizard.PyWizardPage.__init__(self, parent)
        
        self.next = None
        self.prev = None
        
        self.sizer = makeStdPageTitle(self, title)

        self._programm=Programm_
        
        #Создание списка инсталируемых программ
        programm_name_list=[]
        if Programm_:
            programm_name_list=[programm.get('description',programm['programm']) for programm in Programm_]
            
        programmListId=wx.NewId()
        self.programm_list=wx.CheckListBox(self, programmListId, 
            wx.DefaultPosition,wx.DefaultSize,
            programm_name_list)
        for i in range(self.programm_list.GetCount()):
            self.programm_list.Check(i)
            
        self.sizer.Add(self.programm_list, 1, wx.EXPAND|wx.GROW, 5)
        
        self.Bind(wx.EVT_CHECKLISTBOX, self.on_check_change, self.programm_list)
        
        #Список страниц визарда инсталяции
        self._pages=[]
        
    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next
        
    def GetPrev(self):
        return self.prev
        
    def createPages(self):
        """
        Запуск инсталяции программ.
        """
        for i in range(self.programm_list.GetCount()):
            programm_name=self.programm_list.GetString(i)
            #is_checked=self.programm_list.IsChecked(i)
            #if is_checked:
            #    #Программа помечена для установки
            page=icInstallRunPage(self.GetParent(),programm_name,self._programm[i])
            self._pages.append(page)
            self.GetParent().appendPage(page)

    def change_pages(self):
        """
        Изменение порядка страниц в зависимости от выбора пользователем.
        """
        for i in range(self.programm_list.GetCount()):
            programm_name=self.programm_list.GetString(i)
            is_checked=self.programm_list.IsChecked(i)
            page=self._pages[i]
            if is_checked:
                page.GetPrev().SetNext(page)
                if page.GetNext():
                    page.GetNext().SetPrev(page)
            else:
                page.GetPrev().SetNext(page.next)
                if page.GetNext():
                    page.GetNext().SetPrev(page.prev)

    def on_check_change(self,event):
        """
        Обработчик изменения выбора устанавливаемых программ.
        """
        self.change_pages()
        event.Skip()
     
def add_wizard_programm_install_page(Wizard_,*args,**kwargs):
    """
    Добавить страницу инсталляции программ в визард.
    @param Wizard_: Объект главного визарда.
    @return: Созданный объект страницы или None в случае ошибки.
    """
    page=icProgrammInstallPage(Wizard_,u'Программы',*args,**kwargs)
    Wizard_.appendPage(page)
    page.createPages()
    return page    
        
class icInstallRunPage(wx.wizard.PyWizardPage):
    """
    Страница установки программы.
    """
    def __init__(self, parent, title, Programm_=None):
        """
        Конструктор.
        @param parent: Родительский визард, в который вставляется страница.
        @param title: Заголовок страницы.
        @param Programm_: Описательная структура указания устанавливаемой программы.
        {
            'programm':'инсталяционный файл устанавлеемой программы',
            'dir':'инсталяционная папка программы',
            'pth':{
                'name':'имя генерируемого pth-файла',
                'dir':'указание папки, которую содержит pth-файл',
                'var':'пересенная из окружения визарда, которая содержит путь до папки',
                },
        }
        """
        
        wx.wizard.PyWizardPage.__init__(self, parent)
        
        self.next = None
        self.prev = None
        
        self.sizer = makeStdPageTitle(self, title)
        
        self.install_log=wx.TextCtrl(self, -1,
            style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_CHARWRAP)
            
        self.sizer.Add(self.install_log, 1, wx.EXPAND|wx.GROW, 5)
        
        self._programm=Programm_
        
        #self._install_dir=None
        #self._install_dir=os.getcwd()
        #if self._programm.has_key('dir') and self._programm['dir'] is None:
        #    self._install_dir=self.InstallDirDlg()
    
    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next
        
    def GetPrev(self):
        return self.prev

    def getInstallDir(self):
        """
        Инсталляционная папка.
        """
        return self.GetParent().getInstallDir()
        
    def InstallDirDlg(self):
        """
        Диалоговое окно выбора инсталяционной папки.
        """
        result=os.getcwd()
        dlg=None
        try:
            dlg=wx.DirDialog(self,'Инсталяционная папка:',
                style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
            #Установка пути по умолчанию
            dlg.SetPath(result)
            if dlg.ShowModal()==wx.ID_OK:
                result=dlg.GetPath()
            else:
                result=None
        finally:
            if dlg:
                dlg.Destroy()
                dlg=None
        return result

    def on_changed(self,event):
        """
        Обработчик события запуска инсталяции.
        """
        self.install()
        event.Skip()
        
    def install(self,Programm_=None):
        """
        Запуск инсталяции программы.
        @param Programm_: Структура описания инсталируемой программы.
        """
        if Programm_ is None:
            Programm_=self._programm
        
        #Не инсталлировать уже инсталлированные пакеты
        print('Install:',Programm_['programm'],'...',not self.GetParent().getInstallLogManager().is_installed_package(Programm_['programm']))
        if not self.GetParent().getInstallLogManager().is_installed_package(Programm_['programm']):
            
            #self._install_dir=os.getcwd()
            self.GetParent().setInstallDir(os.getcwd())
        
            if 'dir' in Programm_:
                if Programm_['dir'] is None:
                    #self._install_dir=self.InstallDirDlg()
                    self.GetParent().setInstallDir(self.InstallDirDlg())
                else:
                    self.GetParent().setInstallDir(Programm_['dir'])
                    
            #Если перед инсталяцией инсталляционная папка определена
            #но такой папки на диске не , то создать ее
            install_dir=self.GetParent().getInstallDir()
            if install_dir and not os.path.exists(install_dir):
                os.makedirs(install_dir)
            #Определить папку пакета
            package_dir=install_dir
            if 'package_dir' in Programm_:
                package_dir+='/'+Programm_['package_dir']
                #если папка пакета уже существует, то удалить ее
                if os.path.exists(package_dir):
                    print('Delete package dir:',package_dir)
                    shutil.rmtree(package_dir,1)
        
            if Programm_['programm'][-4:].lower()=='.zip':
                #Разархивировать ZIP файл
                self.unzip(Programm_)
            elif Programm_['programm'][-7:].lower()=='.tar.gz':
                self.tar_extract(Programm_)
            elif Programm_['programm'][-4:].lower()=='.deb':
                self.deb_install(Programm_)
                #Т.к. DEB пакеты не деинсталлируются удалением, то вместо директории
                #пакета указываем имя пакета, которое потом будет использоваться
                #в dpkg --remove комманде
                package_dir=Programm_['name']

            if 'mode' in Programm_:
                if Programm_['mode'].lower()==PUBLIC_MODE:
                    #Если режим установлен, как публичный, то установить режим для
                    #инсталляционной папки и поменять владельца на залогинненного
                    util.set_chown_login(install_dir)
                    util.set_public_chmod(install_dir)        
        
            #Если нужно, то создать pth файл
            if 'pth' in Programm_:
                self._create_pth_file(Programm_['pth'])

            self.GetParent().getInstallLogManager().log_install_package(Programm_['programm'],package_dir)

    def _create_pth_file(self,Pth_):
        """
        Создать pth файл.
        @param Pth_: Структура:
        {
            'name':'имя генерируемого pth-файла',
            'dir':'указание папки, которую содержит pth-файл',
            'var':'пересенная из окружения визарда, которая содержит путь до папки',
        }        
        """
        if Pth_['dir'] is None:
            #Pth_['dir']=self._install_dir
            Pth_['dir']=os.path.normpath(self.GetParent().getInstallDir()+'/'+Pth_.get('package',''))
            
        util.create_pth_file(Pth_['name'],Pth_['dir'])

    def _extract_log(self,cmd=None):
        """
        Вывести надписи утилит в консоли на панель визарда.
        """
        #print 'CMD:',cmd,dir(cmd)
        if cmd:
            if type(cmd)<>type(()):
                #Обработка результат popen
                txt=cmd.readline().strip()
                while txt:
                    self.install_log.AppendText(txt)
                    txt=cmd.readline().strip()                
            elif type(cmd)==type(()) and len(cmd)==3:
                #Обработка результат popen3
                out=cmd[1].readline() #.strip()
                err=cmd[2].readline() #.strip()                
                #print 'CMD:',out,err
                while out or err:
                    if out:
                        self.install_log.AppendText(out)
                    if err:
                        start=len(self.install_log.GetValue())
                        self.install_log.AppendText(err)
                        #Закрасить в красный цвет ошибки
                        end=len(self.install_log.GetValue())
                        #print 'RED:',start,end
                        self.install_log.SetStyle(start,end,wx.TextAttr('RED',wx.NullColour))
                        
                    out=cmd[1].readline() #.strip()
                    err=cmd[2].readline() #.strip()                
        
    def unzip(self,Programm_=None):
        """
        Распаковать zip архив.
        """
        if Programm_ is None:
            Programm_=self._programm

        self.remove(Programm_)
        
        if 'dir' in Programm_:
            install_dir=Programm_['dir']
        if install_dir is None:
            install_dir=self.GetParent().getInstallDir() #self._install_dir
        
        #Если инсталляционной папки нет, то создать ее
        if install_dir and not os.path.exists(install_dir): 
            os.makedirs(install_dir)
                
        zip_file_name=os.path.dirname(os.path.dirname(__file__))+INSTALL_PACKAGES_DIR_DEFAULT+Programm_['programm']
        
        console=Programm_.get('console',False)
        cmd=util.unzip_to_dir(zip_file_name,install_dir,bConsole=console)
        self._extract_log(cmd) 
       
    def tar_extract(self,Programm_=None):
        """
        Распаковать tar архив.
        """
        if Programm_ is None:
            Programm_=self._programm
        
        self.remove(Programm_)
        
        if 'dir' in Programm_:
            install_dir=Programm_['dir']
        if install_dir is None:
            install_dir=self.GetParent().getInstallDir() #self._install_dir
            
        #Если инсталляционной папки нет, то создать ее
        if install_dir and not os.path.exists(install_dir): 
            os.makedirs(install_dirs)
                
        tar_file_name=os.path.dirname(os.path.dirname(__file__))+INSTALL_PACKAGES_DIR_DEFAULT+Programm_['programm']
        
        console=Programm_.get('console',False)
        cmd=util.tar_extract_to_dir(tar_file_name,install_dir,bConsole=console)
        self._extract_log(cmd)

    def deb_install(self,dProgramm=None):
        """
        Установить DEB пакет.
        """
        if dProgramm is None:
            dProgramm=self._programm
        
        #Если необходимо. то деинсталлировать пакеты
        self.remove(dProgramm)
        
        deb_file_name=os.path.dirname(os.path.dirname(__file__))+INSTALL_PACKAGES_DIR_DEFAULT+dProgramm['programm']
        
        cmd=util.deb_pkg_install(deb_file_name)
        self._extract_log(cmd)

    def remove(self,dProgramm=None):
        """
        Произвести дополнительные удаления перед установкой.
        """
        if 'remove' in dProgramm:
            for remove_name in dProgramm['remove']:
                if os.path.isfile(remove_name):
                    print('Remove file %s'%remove_name)
                    os.remove(remove_name)
                elif os.path.isdir(remove_name):
                    print('Remove directory %s'%remove_name)
                    shutil.rmtree(remove_name)
                else:
                    print('Uninstall %s DEB package'%remove_name)
                    cmd=util.deb_pkg_uninstall(remove_name)
                    self._extract_log(cmd)
        
        
class icEndInstallPage(wx.wizard.PyWizardPage):
    """
    Страница окончания установки.
    """
    def __init__(self, parent, title, Txt_=None):
        """
        Конструктор.
        @param parent: Родительский визард, в который вставляется страница.
        @param title: Заголовок страницы.
        @param Txt_: Текст.
        """
        
        wx.wizard.PyWizardPage.__init__(self, parent)
        
        self.next = None
        self.prev = None
        
        self.sizer = makeStdPageTitle(self, title)
        
        self.install_log=wx.StaticText(self, -1,Txt_)
            
        self.sizer.Add(self.install_log, 1, wx.EXPAND|wx.GROW, 5)
        
    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next
        
    def GetPrev(self):
        return self.prev
