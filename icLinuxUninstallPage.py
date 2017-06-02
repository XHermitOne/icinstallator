# !/usr/bin/env python
#  -*- coding: utf-8 -*-
""" 
Страницы визарда деинсталятора.
"""
__version__ = '0.01'

#--- Imports ---
import sys
import os

import wx
import wx.wizard

import util

import icLinuxInstallPage

#--- Constants ---

#--- Functions ---

#--- Classes ---
class icProgrammUninstallPage(wx.wizard.PyWizardPage):
    """
    Страница выбора деинсталляции программ/пакетов.
    """
    def __init__(self, parent, title, Programms_=None):
        """
        Конструктор.
        @param parent: Родительский визард, в который вставляется страница.
        @param title: Заголовок страницы.
        @param Programms_: Описательная структура указания установленных программ.
        [
            {
            'programm':'инсталяционный файл устанавлеенной программы',
            'dir':'инсталяционная папка программы',
            },
        ...
        ]
        """
        
        wx.wizard.PyWizardPage.__init__(self, parent)
        
        self.next = None
        self.prev = None
        
        self.sizer = icLinuxInstallPage.makeStdPageTitle(self, title)

        self._programms=Programms_
        
        #Создание списка инсталируемых программ
        programm_name_list=[]
        if Programms_:
            programm_name_list=[programm.get('description',programm['programm']) for programm in Programms_]
            
        programmListId=wx.NewId()
        self.programm_list=wx.CheckListBox(self, programmListId, 
            wx.DefaultPosition,wx.DefaultSize,
            programm_name_list)
        for i in range(self.programm_list.GetCount()):
            self.programm_list.Check(i)
            
        self.sizer.Add(self.programm_list, 1, wx.EXPAND|wx.GROW, 5)
        
        self.Bind(wx.EVT_CHECKLISTBOX, self.on_check_change, self.programm_list)
        
        #Список помеченных для деинсталляции программ/пакетов
        self._checked_uninstall_programms=self._programms
        
        #Список страниц визарда инсталяции
        #self._pages=[]
        
    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next
        
    def GetPrev(self):
        return self.prev
        
    def on_check_change(self,event):
        """
        Обработчик изменения выбора устанавливаемых программ.
        """
        self._checked_uninstall_programms=self.check_uninstall()
        event.Skip()
     
    def check_uninstall(self,Programms_=None):
        """
        Отметить деинсталлируемые программы.
        @param Programms_: Структура описания деинсталлируемых программ.
        @return: Функция возвращает список помеченных для инсталляции программ.
        """
        if Programms_ is None:
            Programms_=self._programms
            
        check_programms=[]
        for i in range(self.programm_list.GetCount()):
            programm_name=self.programm_list.GetString(i)
            is_checked=self.programm_list.IsChecked(i)
            if is_checked:
                check_programms.append(Programms_[i])
        return check_programms            
        
    def on_changing(self,event):
        """
        Смена страницы. Это обработчик срабатывает после 
        нажатия на кнопку Next.
        Обработчик события запуска деинсталяции.
        """
        self.uninstall(self._checked_uninstall_programms)
        event.Skip()
        
    def uninstall(self,Programms_=None):
        """
        Метод деинсталляции выбранных программ/пакетов.
        @param Programm_: Структура описания деинсталируемых программ.
        """
        if Programms_ is None:
            Programms_=self._programms

        uninstalled_programms=[]
        for programm in Programms_:
            if 'dir' in programm:
                ok=self.GetParent().uninstall_programm(programm['programm'])
                uninstalled_txt=programm['programm']+'...'+('YES' if ok else 'NO')
                uninstalled_programms.append(uninstalled_txt)
        
        #В конце вывести сообщение об деинстллированных пакетах
        txt='\n'.join(uninstalled_programms)
        wx.MessageBox(txt,u'Результат деинсталляции')       
        
     
def add_wizard_programm_uninstall_page(Wizard_,Programms_,*args,**kwargs):
    """
    Добавить страницу инсталляции программ в визард.
    @param Wizard_: Объект главного визарда.
    @param Programms_; Описание инсталлируемы/Деинсталлируемых программ.
    @return: Созданный объект страницы или None в случае ошибки.
    """
    packages=Wizard_.getInstallLogManager().load_packages()
    programms=[]
    if packages:
        if Programms_:
            descriptions=dict([(prg['programm'],prg.get('description',prg['programm'])) for prg in Programms_])
        programms=[{'programm':package_name,'dir':package_dir,'description':descriptions[package_name]} for package_name,package_dir in packages.items()]
    page=icProgrammUninstallPage(Wizard_,u'Программы',programms,*args,**kwargs)
    Wizard_.appendPage(page)
    #page.createPages()
    return page    
