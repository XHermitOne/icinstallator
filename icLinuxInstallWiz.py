# !/usr/bin/env python
#  -*- coding: utf-8 -*-
""" 
Инсталятор для Linux/Unix.
Файловая организаци инсталяционного пакета:
..
./packages/ - Папка инсталируемых программ
./icinstallator/ - Пакет инсталятора
./patches/ - Инсталируемы патчи
install.py - Сценарий инсталяции
"""
__version__ = '1.01'

#--- Imports ---
import os,os.path

import wx
import wx.wizard

import util

import icUninstallManager

#--- Classes ---
class icLinuxInstallWizard(wx.wizard.Wizard):
    """
    Визард инсталятора.
    """
    def __init__(self,sTitle=None):
        """
        Конструктор.
        """
        if __file__:
            path=os.path.dirname(__file__)
        else:
            path=os.getcwd()
        self.wizard_img=wx.Image(path+'/install_wiz.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        
        title=sTitle
        wx.wizard.Wizard.__init__(self,None,id=wx.ID_ANY,
                                  title=title,bitmap=self.wizard_img,
                                  pos=wx.DefaultPosition,
                                  style=wx.DEFAULT_DIALOG_STYLE)
        #Установка размера окна визарда
        self.SetPageSize(wx.Size(700,-1))
        #self.SetSizeHintsSz(wx.Size(700,500),wx.DefaultSize)
        
        #Внутренне окружение визарда инсталяции
        self.environment={}
        
        #Список порядка следования страниц
        self.page_order=[]
        
        #Инсталяционная папка
        self._install_dir=None
        
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGED,self.on_changed)
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING,self.on_changing)
        
        #Регистратор-менеджер инсталляции
        self._install_log_manager=icUninstallManager.icInstallLogManager()
        #Регистратор-менеджер деинсталляции
        self._uninstall_log_manager=icUninstallManager.icUninstallLogManager()

    def getInstallLogManager(self):
        """
        Регистратор-менеджер инсталляции.
        """
        return self._install_log_manager
    
    def getUninstallLogManager(self):
        """
        Регистратор-менеджер деинсталляции.
        """
        return self._uninstall_log_manager
    
    def appendPage(self,Page_):
        """
        Установка следующей страницы.
        """
        if Page_:
            if self.page_order:
                #Установить связи между страницами
                Page_.SetPrev(self.page_order[-1])
                self.page_order[-1].SetNext(Page_)
            self.page_order.append(Page_)

    def check_root(self):
        """
        Функция проверки прав администратора.
        """
        ok=util.is_root_user()
        if not ok:
            wx.MessageBox(u'Запуск инсталяции возможен только с правами root!',u'ВНИМАНИЕ!')
        return ok

    def on_changed(self,event):
        """
        Обработчик смены страницы инсталляции.
        Это обработчик срабатывает перед 
        появлением страницы на экране. См. демку.
        """
        page=event.GetPage()
        if hasattr(page,'on_changed'):
            return page.on_changed(event)
        event.Skip()

    def on_changing(self,event):
        """
        Обработчик смены страницы инсталляции.
        Это обработчик срабатывает после 
        нажатия на кнопку Next.
        """
        page=event.GetPage()
        if hasattr(page,'on_changing'):
            return page.on_changing(event)
        event.Skip()
        
    def runFirstPage(self):
        """
        Запуск первой страницы.
        """
        if self.page_order:
            first_page=self.page_order[0]
            if first_page:
                #self.GetPageAreaSizer().CalcMin()
                self.RunWizard(first_page)
                
    def setInstallDir(self,InstallDir_):
        """
        Инсталляционная папка.
        """
        self._install_dir=InstallDir_
        
    def getInstallDir(self):
        """
        Инсталляционная папка.
        """
        return self._install_dir
        
    def uninstall_programm(self,ProgrammName_=None):
        """
        Деинсталлировать программу по имени.
        @param ProgrammName_: Наименование программы.
        """
        return self.getUninstallLogManager().log_uninstall_package(ProgrammName_)
    
def run(InstallScript_=None,*args,**kwargs):
    """
    Основная функция запуска инсталлятора.
    @param InstallScript_: Функция инсталляционного скрипта.
    В качестве аргумента функция должна принимать объект визарда.
    """
    import icLinuxInstallPage
    
    app=wx.PySimpleApp()
    wizard=icLinuxInstallWizard(u'программного обеспечения')
    
    #Запустить функцию инсталляционного скрипта
    if InstallScript_:
        InstallScript_(wizard,*args,**kwargs)

    #Всегда присутствует страница окончания инсталляции
    end_page=icLinuxInstallPage.icEndInstallPage(wizard,u'Окончание',u'Инсталяция успешно завершена')
    wizard.appendPage(end_page)
    
    #Визард всегда запускается с первой страницы
    wizard.runFirstPage()

def install(Script_=None,PrevInstallScript_=None,PostInstallScript_=None,*args,**kwargs):
    """
    Основная функция запуска инсталлятора.
    @param Script_: Функция инсталляционного скрипта.
    @param PrevInstallScript_: Предварительный скрипт инсталляции.
    @param PostInstallScript_: Завершающий скрипт инсталляции.
    В качестве аргумента функция должна принимать объект визарда.
    """
    import icLinuxInstallPage
    
    app=wx.PySimpleApp()
    wizard=icLinuxInstallWizard(u'Инсталляция программного обеспечения')

    if PrevInstallScript_:
        PrevInstallScript_(wizard,*args,**kwargs)
    
    #Запустить функцию инсталляционного скрипта
    if Script_:
        Script_(wizard,*args,**kwargs)

    #Всегда присутствует страница окончания инсталляции
    end_page=icLinuxInstallPage.icEndInstallPage(wizard,u'Окончание',u'Инсталяция успешно завершена')
    wizard.appendPage(end_page)
    
    #Визард всегда запускается с первой страницы
    wizard.runFirstPage()

    if PostInstallScript_:
        PostInstallScript_(wizard,*args,**kwargs)
    
def uninstall(Script_=None,PrevUninstallScript_=None,PostUninstallScript_=None,Programms_=None,*args,**kwargs):
    """
    Основная функция запуска деинсталлятора.
    @param Script_: Функция деинсталляционного скрипта.
    @param PrevInstallScript_: Предварительный скрипт деинсталляции.
    @param PostInstallScript_: Завершающий скрипт деинсталляции.
    @param Programms_; Описание инсталлируемы/Деинсталлируемых программ.
    В качестве аргумента функция должна принимать объект визарда.
    """
    import icLinuxInstallPage
    import icLinuxUninstallPage
    
    app=wx.PySimpleApp()
    wizard=icLinuxInstallWizard(u'Деинсталляция программного обеспечения')
    
    if PrevUninstallScript_:
        PrevUninstallScript_(wizard,*args,**kwargs)
        
    #Запустить функцию деинсталляционного скрипта
    if Script_:
        Script_(wizard,*args,**kwargs)
    else:
        icLinuxUninstallPage.add_wizard_programm_uninstall_page(wizard,Programms_)

    #Всегда присутствует страница окончания инсталляции
    end_page=icLinuxInstallPage.icEndInstallPage(wizard,u'Окончание',u'Деинсталяция успешно завершена')
    wizard.appendPage(end_page)
    
    #Визард всегда запускается с первой страницы
    wizard.runFirstPage()

    if PostUninstallScript_:
        PostUninstallScript_(wizard,*args,**kwargs)
    
def test():
    """
    Функция тестирования визарда инсталятора.
    """
    import icLinuxInstallPage
    
    app=wx.PySimpleApp()
    wizard=icLinuxInstallWizard(u'Проверка тестового пакета')
    #if not wizard.check_root():
    #    return 
    
    packages={'wx':{'ver':'2.8.8.1','compare':'>='},
        'sqlalchemy':{'ver':'0.4','compare':'>='},}
    page1=icLinuxInstallPage.icPackageControlPage(wizard,u'Проверка пакетов',packages)
    wizard.appendPage(page1)

    programm=[{'programm':'Editra-0.3.80.tar.gz','dir':None},
        {'programm':'defis-0.3.5.zip',
            'dir':None,
            'pth':{'name':'ic.pth','dir':None}},
        ]
    page2=icLinuxInstallPage.icProgrammInstallPage(wizard,u'Программы',programm)
    wizard.appendPage(page2)
    page2.createPages()

    page3=icLinuxInstallPage.icEndInstallPage(wizard,u'Окончание',u'Инсталяция успешно завершена')
    wizard.appendPage(page3)

    wizard.RunWizard(page1)
    
        
if __name__=='__main__':
    test()
