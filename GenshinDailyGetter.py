import os
import sys
import win32com.client
from urllib.error import URLError
import tkinter
from tkinter import messagebox
import winreg
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException
import chromedriver_autoinstaller
from time import sleep

class GenshinDailyGetter:
    
    def __init__(self) -> None:
        self.PROFILE = 'profile'
        self.REG_PATH = r'Software\Knoth\GenshinDailyGetter'

    def raise_except(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                raise
        return wrapper

    def main(self) -> None:
        # Chromeユーザを取得
        profile = None
        try:
            profile = self.get_reg(self.PROFILE)
        except FileNotFoundError:
            # Chromeユーザを自動算出
            profile = ''.join([os.environ['USERPROFILE'], r'\AppData\Local\Google\Chrome\User Data\Default'])
            if os.path.exists(profile):
                self.set_reg(self.PROFILE, profile)

        # デイリーボーナス取得
        try:
            self.get_daily_bonus(profile)
        except NoSuchElementException:
            print('デイリーボーナス取得済み')
        except InvalidArgumentException:
            messagebox.showwarning('Chrome起動時エラー', 'Chromeの起動に失敗しました。Chromeを一旦終了し、再度実行してください。\nエラーが再度発生した場合は引数「init」を指定し、アプリケーションを実行してください。')

    def init(self):
        """ 初期設定を行う """
        
        def save_click():
            """ 保存ボタン押下時処理 """
            profile = profile_entry.get()
            if profile == '':
                messagebox.showwarning('未入力エラー', 'プロフィールパスを入力してください。')
                return

            if not os.path.exists(profile):
                messagebox.showwarning('パス指定エラー', 'プロフィールパスに誤りがあります。再度設定してください。')
                return

            # 設定登録
            self.set_reg(self.PROFILE, profile)

            response = messagebox.showinfo('登録完了', '登録が完了しました。\nログインボーナスの自動取得が可能になりました。')
            if response == 'ok':
                frm.quit()

        # Chromeユーザ情報を設定する
        frm = tkinter.Tk()
        frm.geometry('400x150')
        frm.title('Chromeユーザ選択')
        # プロフィールパス取得
        profile_label = tkinter.Label(text='Google Chromeで「chrome://version」に遷移後\n「プロフィール パス」を確認し、以下に入力してください。', justify='left')
        profile_label.place(x=50, y=20)
        profile_entry = tkinter.Entry(width=40)
        profile_entry.place(x=50, y=80, width=230, height=30)
        # 保存ボタン
        save_btn = tkinter.Button(frm, text='保存', command=save_click)
        save_btn.place(x=300, y=80, width=60, height=30)
        frm.mainloop()

    def set_startup(self):
        """ 自動受取を行うよう設定する """
        # スタートアップ登録
        shortcut_lnk = r'.\GenshinDailyGetter.lnk'
        user_startup_path = ''.join([os.environ['AppData'], r'\Microsoft\Windows\Start Menu\Programs\StartUp'])
        shortcut_path = ''.join([user_startup_path, shortcut_lnk])
        # ショートカットを作成する
        target = ''.join([os.getcwd(), r"\GenshinDailyGetter.exe"])
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.Arguments = 'startup'
        shortcut.Workingdirectory = os.getcwd()
        shortcut.WindowStyle = 1
        shortcut.save()
        

    @raise_except
    def set_reg(self, name, value):
        """ レジストリに書き込む """
        key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, self.REG_PATH, access=winreg.KEY_WRITE)
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)

    @raise_except
    def delete_reg(self):
        """ レジストリを削除する """
        try:
            winreg.DeleteKeyEx(winreg.HKEY_CURRENT_USER, self.REG_PATH, access=winreg.KEY_WRITE)
        except FileNotFoundError:
            pass # 無いなら無いで問題ない

    @raise_except
    def get_reg(self, name):
        """ レジストリを読み込む """
        key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, self.REG_PATH, access=winreg.KEY_READ)
        value, type_id = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return value

    @raise_except
    def chromedriver_install(self, retries=0):
        """ ChromeDriverをインストールする。  
        ネットワークエラー時は1秒毎に再試行を行い、10回接続に失敗した場合はダイアログを表示する
        """
        if 10 < retries:
            messagebox.showerror('ネットワークエラー', 'ネットワークに接続出来なかったため、ChromeDriverの更新に失敗しました。')
            return
        sleep(1)

        # get ChromeDriver
        try:
            chromedriver_autoinstaller.install(cwd=True)
        except URLError:
            retries += 1
            self.chromedriver_install(retries)

    @raise_except
    def get_daily_bonus(self, profile):
        """ デイリーボーナスを取得する """

        # get ChromeDriver
        self.chromedriver_install()

        # get profile
        splited_profile = profile.split('\\')
        profile_path = '\\'.join(splited_profile[:-1])
        profile_directory = splited_profile[-1]

        # init Chrome WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument(''.join(['--user-data-dir=', profile_path]))
        options.add_argument(''.join(['--profile-directory=', profile_directory]))
        options.add_experimental_option('detach', True)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.use_chromium = True
        driver = webdriver.Chrome(options=options)

        try:
            url = 'https://webstatic-sea.mihoyo.com/ys/event/signin-sea/index.html?act_id=e202102251931481&lang=ja-jp'
            driver.get(url)
            sleep(5)
            # get daily bonus
            daily_button = driver.find_element_by_css_selector('div[class*=components-home-assets-__sign-content_---active---]')
            daily_button.click()
            sleep(2)
            login_button = driver.find_element_by_class_name('login-btn')
            if login_button is not None:
                messagebox.showinfo('自動ログイン切れ', '手動でHoYoLABにログインを行い、自動ログインが可能なように設定してください。')

        finally:
            driver.quit()

if __name__ == "__main__":
    
    args = sys.argv
    gdg = GenshinDailyGetter()

    if 2 != len(args):
        # exeからの起動
        gdg.set_startup()
        gdg.main()
    elif args[1] == 'init':
        # コマンドからの引数付き起動
        gdg.delete_reg()
        gdg.set_startup()
        gdg.init()
    elif args[1] == 'startup':
        # スタートアップからの起動
        gdg.main()