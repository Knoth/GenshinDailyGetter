# GenshinDailyGetter

## how to use
1. download GenshinDailyGetter.exe
    - https://github.com/Knoth/GenshinDailyGetter/releases/
2. Place the file in any location.  
    like `C:\GenshinDailyGetter\GenshinDailyGetter.exe`.
3. Close Google Chrome tasks.
4. Double click GenshinDailyGetter.exe to initialize.
5. __All done.__  
    you can receive hoyolab's daily login bonus automatically when you start your pc.

## 悩み
悪い事してないのにウイルス判定されます。悲しい…。

## develop
python -m venv env  
env\Scripts\activate  
python -m pip install --upgrade pip  
pip install -r requirements.txt  

## to exe
pyinstaller GenshinDailyGetter.py --onefile --noconsole
