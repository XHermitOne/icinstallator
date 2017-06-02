# !/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
Дополниетельные сервисные функции.
"""

__version__ = (0, 0, 0, 2)

# --- Imports ---
import sys
import sysconfig
import os
import os.path
import pwd
import stat
import getpass
import shutil


def who_am_i():
    """
    Имя залогиненного пользователя.
    """
    return getpass.getuser()


def is_root_user():
    """
    Проверить текущий пользователь - root?
    @return: Функция возвращает True/False.
    """
    return bool(who_am_i().lower()=='root')


def check_python_library_version(LibName_, LibVer_, Compare_='=='):
    """
    Проверка установлена ли библиотека указанной версии.
    @param LibName_: Имя библиотеки, например 'wx'.
    @param LibVer_: Версия библиотеки, например '2.8.8.1'.
    @param Compare_: Оператор сравнения.
    @return: Возвращает True/False.
    """
    import_cmd = 'import '+str(LibName_)
    try:
        exec(import_cmd)
        import_lib = eval(LibName_)
    except ImportError:
        # Нет такой библиотеки
        print('Check Library Error:', LibName_)
        return False

    if Compare_ == '==':
        # Проверка на сравнение
        print('Python Library:', LibName_, 'Version:', import_lib.__version__)
        return bool(import_lib.__version__ == LibVer_)
    elif Compare_ in ('>=', '=>'):
        # Проверка на больше или равно
        print('Python Library:', LibName_, 'Version:', import_lib.__version__)
        return version_compare_greate_equal(import_lib.__version__, LibVer_)
    else:
        print('Not supported compare:', Compare_)
    return False


def version_compare_greate_equal(Version1_, Version2_, Delimiter_='.'):
    """
    Сравнение версий на Version1_>=Version2_.
    @param Version1_: Версия 1. В строковом виде. Например '2.8.9.2'.
    @param Version2_: Версия 2. В строковом виде. Например '2.8.10.1'.
    @param Delimiter_: Разделитель. Например точка.
    """
    ver1 = tuple([int(sub_ver) for sub_ver in Version1_.split(Delimiter_)])
    ver2 = tuple([int(sub_ver) for sub_ver in Version2_.split(Delimiter_)])
    len_ver2 = len(ver2)
    for i, sub_ver1 in enumerate(ver1):
        if i >= len_ver2:
            return True
        sub_ver2 = ver2[i]
        if sub_ver1 < sub_ver2:
            return False
        elif sub_ver1 > sub_ver2:
            return True
    return True


def check_python_labraries(**kwargs):
    """
    Проверка установленных библиотек Python.
    """
    result = True
    for lib_name, lib_ver in kwargs.items():
        result = result and check_python_library_version(lib_name, lib_ver)
    return result


def check_linux_package(PackageName_, Version_=None, Compare_='=='):
    """
    Проверка установленного пакета Linux.
    @param PackageName_: Имя пакета, например 'libgnomeprintui'
    @param Version_: Версия пакета. Если None, то версия не проверяется.\
    @param Compare_: Метод проверки версии.
    @return: True-пакет установлен, False-не установлен, 
        None-система пакетов не определена.
    """
    if is_deb_linux():
        print('This Linux is Debian')
        return check_deb_linux_package(PackageName_, Version_, Compare_)
    else:
        print('This linux is not Debian')
    return None


def check_deb_linux_package(PackageName_, Version_=None, Compare_='=='):
    """
    Проверка установленного пакета Linux.
    @param PackageName_: Имя пакета, например 'libgnomeprintui'
    @param Version_: Версия пакета. Если None, то версия не проверяется.\
    @param Compare_: Метод проверки версии.
    @return: True-пакет установлен, False-не установлен, 
        None-система пакетов не определена.
    """
    try:
        cmd = 'dpkg-query --list | grep \'ii \' | grep \'%s\'' % PackageName_
        result = os.popen3(cmd)[1].readlines()
        return bool(result)
    except:
        print('Check Debian installed package Error', cmd)
        raise
    return None    


def check_deb_package_install(sPackageName):
    """
    Проверка установленн ли пакет DEB.
    @param sPackageName: Имя пакета, например 'libgnomeprintui'
    @return: True-пакет установлен, False-не установлен, 
        None-система пакетов не определена.
    """
    return check_deb_linux_pacakge(sPackageName)


def get_uname(Option_='-a'):
    """
    Результат выполнения комманды uname.
    """
    try:
        cmd = 'uname %s' % Option_
        return os.popen3(cmd)[1].readline()
    except:
        print('Uname Error', cmd)
        raise
    return None    


def get_linux_name():
    """
    Определить название Linux операционной системы и версии.
    """
    try:
        if os.path.exists('/etc/issue'):
            # Обычно Debian/Ubuntu Linux
            cmd = 'cat /etc/issue'
            return os.popen3(cmd)[1].readline().replace('\\n', '').replace('\\l', '').strip()
        elif os.path.exists('/etc/release'):
            # Обычно RedHat Linux
            cmd = 'cat /etc/release'
            return os.popen3(cmd)[1].readline().replace('\\n', '').replace('\\l', '').strip()
    except:
        print('Get linux name ERROR')
        raise
    return None


DEBIAN_LINUX_NAMES = ('Ubuntu', 'Debian', 'Mint', 'Knopix')


def is_deb_linux():
    """
    Проверка является ли дистрибутив c системой пакетов Debian.
    @return: Возвращает True/False.
    """
    linux_name = get_linux_name()
    print('Linux name:', linux_name)
    return bool([name for name in DEBIAN_LINUX_NAMES if name in linux_name])


def is_deb_linux_uname():
    """
    Проверка является ли дистрибутив c системой пакетов Debian.
    Проверка осуществляется с помощью команды uname.
    ВНИМАНИЕ! Это не надежный способ.
    Функция переписана.
    @return: Возвращает True/False.
    """
    uname_result = get_uname()
    return (('Ubuntu' in uname_result) or ('Debian' in uname_result))


def get_dist_packages_path():
    """
    Путь к папке 'dist-packages' или 'site_packages' 
    (в зависимости от дистрибутива) Python.
    """
    python_stdlib_path = sysconfig.get_path('stdlib')
    site_packages_path = os.path.normpath(python_stdlib_path+'/site-packages')
    dist_packages_path = os.path.normpath(python_stdlib_path+'/dist-packages')
    if os.path.exists(site_packages_path):
        return site_packages_path
    elif os.path.exists(dist_packages_path):
        return dist_packages_path
    return None


def create_pth_file(PthFileName_, Path_):
    """
    Создание *.pth файла в папке site_packages.
    @param PthFileName_: Не полное имя pth файла, например 'ic.pth'.
    @param Path_: Путь который указывается в pth файле.
    @return: Возвращает результат выполнения операции True/False.
    """
    pth_file = None
    try:
        dist_packages_path = get_dist_packages_path()
        pth_file_name = dist_packages_path+'/'+PthFileName_
        pth_file = open(pth_file_name, 'wt')
        pth_file.write(Path_)
        pth_file.close()
        pth_file = None
        
        # Установить права на PTH файл
        try:
            os.chmod(pth_file_name, stat.S_IRWXO | stat.S_IRWXG | stat.S_IRWXU)
        except:
            print('ERROR! Chmod function in create_pth_file')
        print('Create PTH file:', pth_file_name, 'path:', Path_)
        return True
    except:
        if pth_file:
            pth_file.close()
            pth_file = None
        raise
    return False


def unzip_to_dir(ZipFileName_, Dir_, bOverwrite=True, bConsole=False):
    """
    Распаковать *.zip архив в папку.
    @param ZipFileName_: Полное имя *.zip архива.
    @param Dir_: Указание папки, в которую будет архив разворачиваться.
    @param bOverwrite: Перезаписать существующие файлы без запроса?
    @param bConsole: Вывод в консоль?
    @return: Возвращает результат выполнения операции True/False.
    """
    try:
        overwrite = ''
        if bOverwrite:
            overwrite = '-o'
        unzip_cmd = 'unzip %s %s -d %s' % (overwrite, ZipFileName_, Dir_)
        if bConsole:
            os.system(unzip_cmd)
            return None
        else:
            return os.popen3(unzip_cmd)
    except:
        print('Unzip Error', unzip_cmd)
        raise
    return None


def tar_extract_to_dir(TarFileName_, Dir_, bConsole=False):
    """
    Распаковать *.tar архив в папку.
    @param TarFileName_: Полное имя *.tar архива.
    @param Dir_: Указание папки, в которую будет архив разворачиваться.
    @param bConsole: Вывод в консоль?
    @return: Возвращает результат выполнения операции True/False.
    """
    try:
        tar_extract_cmd = 'tar --extract --verbose --directory=%s --file=%s' % (Dir_, TarFileName_)
        print('Tar extract command:', tar_extract_cmd, os.path.exists(TarFileName_))
        if bConsole:
            os.system(tar_extract_cmd)
            return None
        else:
            return os.popen3(tar_extract_cmd)
    except:
        print('Tar Extract Error', tar_extract_cmd)
        raise
    return None


def deb_pkg_install(sDEBFileName):
    """
    Установить deb пакет.
    @param sDEBFileName: Полное имя *.deb пакета.
    @return: Возвращает результат выполнения операции True/False.
    """
    try:
        deb_install_cmd = 'dpkg --install %s' % sDEBFileName
        print('DEB package install command:', deb_install_cmd, os.path.exists(sDEBFileName))
        return os.popen3(deb_install_cmd)
    except:
        print('DEB package install Error', deb_install_cmd)
        raise
    return None


def deb_pkg_uninstall(sDEBPackageName):
    """
    Деинсталлировать DEB пакет.
    @param sDEBPackageName: Имя пакета. Например dosemu.
    @return: Возвращает результат выполнения операции True/False.
    """
    try:
        if check_deb_package_install:
            deb_uninstall_cmd = 'dpkg --remove %s' % sDEBPackageName
            print('DEB package uninstall command:', deb_uninstall_cmd)
            return os.popen3(deb_uninstall_cmd)
        else:
            print('WARNING: Package %s not installed' % sDEBPackageName)
    except:
        print('DEB package uninstall Error', deb_uninstall_cmd)
        raise
    return None


def get_home_path(UserName_=None):
    """
    Определить домашнюю папку.
    """
    if sys.platform[:3].lower() == 'win':
        home = os.environ['HOMEDRIVE']+os.environ['HOMEPATH']
        home = home.replace('\\', '/')
    else:
        if UserName_ is None:
            home = os.environ['HOME']
        else:
            user_struct = pwd.getpwnam(UserName_)
            home = user_struct.pw_dir
    return home


def get_login():
    """
    Имя залогинненного пользователя.
    """
    username = os.environ['USERNAME']
    if username != 'root':
        return username
    else:
        return os.environ['SUDO_USER']
        

def dir_dlg(Title_='', DefaultPath_=''):
    """
    Диалог выбора каталога.
    @param Title_: Заголовок диалогового окна.
    @param DefaultPath_: Путь по умолчанию.
    """
    import wx
    app = wx.GetApp()
    result = ''
    dlg = None
    
    if app:
        try:
            main_win = app.GetTopWindow()

            dlg = wx.DirDialog(main_win, Title_,
                               style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)

            # Установка пути по умолчанию
            if not DefaultPath_:
                DefaultPath_ = os.getcwd()
            dlg.SetPath(DefaultPath_)
            if dlg.ShowModal() == wx.ID_OK:
                result = dlg.GetPath()
            else:
                result = ''
        finally:
            if dlg:
                dlg.Destroy()
                dlg = None

    return result


def file_dlg(Title_='', Filter_='', DefaultPath_=''):
    """
    Открыть диалог выбора файла для открытия/записи.
    @param Title_: Заголовок диалогового окна.
    @param Filter_: Фильтр файлов.
    @param DefaultPath_: Путь по умолчанию.
    @return: Возвращает полное имя выбранного файла.
    """
    import wx
    app = wx.GetApp()
    result = ''
    dlg = None
    
    if app:
        try:
            main_win = app.GetTopWindow()

            wildcard = Filter_+'|All Files (*.*)|*.*'
            dlg = wx.FileDialog(main_win, Title_, '', '', wildcard, wx.OPEN)
            if DefaultPath_:
                dlg.SetDirectory(normpath(DefaultPath_, get_login()))
            else:
                dlg.SetDirectory(os.getcwd())
        
            if dlg.ShowModal() == wx.ID_OK:
                result = dlg.GetPaths()[0]
            else:
                result = ''
            dlg.Destroy()
        finally:
            if dlg:
                dlg.Destroy()

    return result


def get_dosemu_dir(UserName_=None):
    """
    Определить папку установленного dosemu.
    """
    home = get_home_path(UserName_)
    dosemu_dir = os.path.join(home, '.dosemu')
    if os.path.exists(dosemu_dir):
        return dosemu_dir
    else:
        return dir_dlg(u'Не найдена папка dosemu')
        
    return None


def check_dir(Dir_):
    """
    Проверить папку, если ее нет то она создается.
    """
    norm_dir = normpath(Dir_, get_login())
    if not os.path.exists(norm_dir):
        try:
            os.makedirs(norm_dir)
            return True
        except:
            print('ERROR! Make directory', norm_dir)
            return False
    else:
        return True


def save_file_txt(FileName_, Txt_=''):
    """
    Запись текста в файл.
    @param FileName_; Имя файла.
    @param Txt_: Записываемый текст.
    """
    file = None
    try:
        file = open(FileName_, 'wt')
        file.write(Txt_)
        file.close()
    except:
        if file:
            file.close()
        print('Save text file', FileName_, 'ERROR')
        return False


def copy_file_to(SrcFileName_, DstPath_, ReWrite_=True):
    """
    Копировать файл в указанную папку.
    @param SrcFileName_: Имя файла-источника.
    @param DstPath_: Папка-назначение.
    @param ReWrite_: Перезаписать файл, если он уже существует?
    """
    try:
        DstPath_ = normpath(DstPath_, get_login())
        if not os.path.exists(DstPath_):
            os.makedirs(DstPath_)
        dst_file_name = DstPath_+'/'+os.path.basename(SrcFileName_)
        if ReWrite_:
            if os.path.exists(dst_file_name):
                os.remove(dst_file_name)
        shutil.copyfile(SrcFileName_, dst_file_name)
        return True
    except:
        return False


def set_chown_login(sPath):
    """
    Установить владельца файла/папки залогиненного пользователя.
    """
    if not os.path.exists(sPath):
        return False
    username = get_login()
    user_struct = pwd.getpwnam(username)
    uid = user_struct.pw_uid
    gid = user_struct.pw_gid
    path = normpath(sPath, username)
    return os.chown(path, uid, gid)


def set_public_chmod(sPath):
    """
    Установить свободный режим доступа (0x777) к файлу/папке.
    """
    path = normpath(sPath, get_login())
    if os.path.exists(path):
        return os.chmod(path, stat.S_IRWXO | stat.S_IRWXG | stat.S_IRWXU)
    return False


def set_public_chmode_tree(sPath):
    """
    Установить свободный режим доступа (0x777) к файлу/папке рекурсивно.
    """
    path = normpath(sPath, get_login())
    result = set_public_chmod(path)
    if os.path.isdir(path):
        for f in os.listdir(path):
            pathname = os.path.join(path, f)
            set_public_chmode_tree(pathname)
    return result


def sym_link(sLinkPath, sLinkName, sUserName=None, bOverwrite=True):
    """
    Создать символическую ссылку.
    @param sLinkPath: На что ссылается ссылка.
    @param sLinkName: Имя ссылки.
    @param sUserName: Имя пользователя.
    @param bOverwrite: Перезаписать ссылку, если она существует?
    """ 
    username = sUserName
    if username is None:
        username = get_login()
    link_path = normpath(sLinkPath, username)
    link_name = normpath(sLinkName, username)
    
    if os.path.exists(link_name) and bOverwrite:
        # Перезаписать?
        os.remove(link_name)
    try:
        return os.symlink(link_path, link_name)
    except:
        print('ERROR! Create symbolic link:', link_name, '->', link_path)
        raise
    return None


def get_options(lArgs=None):
    """
    Преобразование параметров коммандной строки в словарь python.
    Параметры коммандной строки в виде --ключ=значение.
    @param lArgs: Список строк параметров.
    @return: Словарь значений или None в случае ошибки.
    """
    if lArgs is None:
        lArgs = sys.argv[1:]
        
    opts = {}
    args = []
    while lArgs:
        if lArgs[0][:2] == '--':
            if '=' in lArgs[0]:
                # поиск пар “--name=value”
                i = lArgs[0].index('=')
                # ключами словарей будут имена параметров
                opts[lArgs[0][:i]] = lArgs[0][i+1:]
            else:
                # поиск “--name”
                # ключами словарей будут имена параметров
                opts[lArgs[0]] = True
        else:
            args.append(lArgs[0])
        lArgs = lArgs[1:]
    return opts, args
    
    
def normpath(path, sUserName=None):
    """
    Нормировать путь.
    @param path: Путь.
    @param sUserName: Имя пользователя.
    """
    home_dir = get_home_path(sUserName)
    return os.path.abspath(os.path.normpath(path.replace('~', home_dir)))


def text_file_replace(sTextFileName, sOld, sNew, bAutoAdd=True):
    """
    Замена строки в текстовом файле.
    @param sTextFileName: Имя текстового файла.
    @param sOld: Старая строка.
    @param sNew: Новая строка.
    @param bAutoAdd: 
    @return: True/False.
    """
    txt_filename = normpath(sTextFileName, get_login())
    if os.path.exists:
        try:
            f = None
            f = open(txt_filename, 'r')
            txt = f.read()
            txt = txt.replace(sOld, sNew)
            if bAutoAdd and (sNew not in txt):
                txt += '\n'
                txt += sNew
            f.close()
            f = None
            f = open(txt_filename, 'w')
            f.write(txt)
            f.close()
            f = None
            return True
        except:
            print('ERROR! Text file replace in %s' % txt_filename)
            if f:
                f.close()
                f = None
    else:
        print('WARNING! File %s not exists' % txt_filename)
    return False


def test():
    """
    Функция тестирования.
    """
    result = get_options(['--dosemu=/home/user/.dosemu', '--option2', 'aaaa'])
    print('TEST>>>', result)


if __name__ == '__main__':
    test()
