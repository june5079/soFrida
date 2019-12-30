
<p align="center">
  <img src="static/README_Images/newlogo.png" width=100%>
  <p>soFrida+ is a GUI framework powered by Frida(https://frida.re) and provides special features to find cloud credentials from mobile applications. The upgraded soFrdia+ not only supports hooking to various cloud SDK functions but also provides powerful customizations for hacking mobile apps. soFrida+ recognizes the mobile operating system of the connected device and automatically generates hooking scripts based on it. Security analysts can track the parameters and return values of common functions as well as cloud SDKs in real-time and reduce the time spent analyzing vulnerabilities.<P>
<p align="center">To see our research, please visit: https://sofrida.github.io<P>


  <p align="center">
    <a href="LICENSE">
      <img src="https://img.shields.io/badge/license-GPLv3-blue.svg" />
    </a>
    <a href="https://frida.re">
    	<img src="https://img.shields.io/badge/Powered%20by-Frida-red" />
    </a>
    <a href="https://github.com/SeleniumHQ/selenium">
      <img src="https://img.shields.io/badge/built%20with-Selenium-yellow.svg" />
    </a>
    <a href="https://www.python.org/">
    	<img src="https://img.shields.io/badge/built%20with-Python3-red.svg" />
    </a>
    <a href="https://socket.io">
    	<img src="https://img.shields.io/badge/Logging%20with-socketio-orange.svg" />
    </a>
  </p>
</p>


## Table of Contents
- [How to install and run soFrida+]
  * [Requirements for Analysis](#requirements)
  * [Installing soFrida+](#installing-sofrida)
  * [Guides and tutorials]
    * [Video tutorials](#video-tutorials)
- [Main Features]
    * [Main Features > Getting Ready](#main-features--getting-ready)
    * [Main Features > Analysis of Vulnerabilities (Android App)](#main-features--analysis-of-vulnerabilities-android-app)
    * [Main Features > Analysis of Vulnerabilities (iOS App)](#main-features--analysis-of-vulnerabilities-ios-app)
- [Authors](#authors)
- [Disclaimer](#disclaimer)
- [LICENSE](#license)


## Requirements
* Rooted Android mobile phone or Jailbroken iPhone for hooking process
* Web browser without AD-Block plugins
* [Chrome](https://chromedriver.chromium.org/downloads) or [Firfox](https://github.com/mozilla/geckodriver/releases) driver 
* Support OS : MacOS, Windows, Ubuntu (Tested)
* Only works with higher Python3.6
* Ethical mind 👍


## Installing soFrida+
```python3 -m pip install -r requirements.sf```

That's it. You're ready to hack Cloud-backend 😎

```python3 app.py```

Open your favorite browser and connect to http://127.0.0.1:8888
You can change port by modifying app.py (End of the code)


## Video Tutorials
- We're preparing new video tutorials of soFrida+. See our previous tutorial video for reference.
[![soFrida Video Tutorials](https://img.youtube.com/vi/l8B3vrJg7zk/0.jpg)](https://youtu.be/l8B3vrJg7zk "Click on to watch tutorials")


## Main Features > Getting Ready
- ```Select Device : Select a target device. soFrida+ automatically detects devices.```
<img src = 'static/README_Images/select_device.png'>


- ```Download - Playstore : Download APK Files from Google Play```
<img src = 'static/README_Images/apk_download.png'>


- ```Pull - Device : Pull APK Files from mobile phone and check cloud SDK```
<img src = 'static/README_Images/pull_device.png'>


## Main Features > Analysis of Vulnerabilities (Android App)
- ```Analysis - Cloud : Automated analysis for cloud SDK misconfiguration. Select a target appliation and click on "Analyze" button.```
<img src = 'static/README_Images/analysis_cloud_select.png'>


- ```Analysis - Manual : You can select speific target class and methods to hook. soFrida+ will automatically generate hooking script based on your choice.```
<img src = 'static/README_Images/select_class.png'>

<img src = 'static/README_Images/select_method.png'>

<img src = 'static/README_Images/code_modification.png'>

## Main Features > Analysis of Vulnerabilities (iOS App)
- ```Analysis - iOS Manual : You can select speific target object and methods to hook. soFrida+ will automatically generate hooking script based on your choice.```
<img src = 'static/README_Images/iOS_Manual.png'>

<img src = 'static/README_Images/iOS_Object.png'>

<img src = 'static/README_Images/iOS_hook.png'>


## Make Your Own Preset
- ```You can save and load a hooking script. Once you SET a preset script, it will be loaded in the background. This will be very useful when you try bypass security mitigations.```
<img src = 'static/README_Images/preset_save.png'>

<img src = 'static/README_Images/preset_load.png'>

## Authors
**Hyunjun Park** - Hyunjun Park is a senior engineer of Samsung SDS in South Korea and a graduate student of SANE Lab in Korea University (Supervisor : Seungjoo Gabriel Kim). His daily job is pentesting a broad range of Samsung products including smart phone, smart TV, wearable devices, etc. He also serves as a main staff of Kimchicon Security Conference in South Korea.

**Soyeon Kim** - Soyeon Kim is a security researcher of Samsung SDS in South Korea. She mainly doing a security assessment of Samsung IoT products. She is interested in analyzing Android apps and IOS apps using Frida.

**Seungjoo (Gabriel) Kim** - Seungjoo (Gabriel) Kim is a professor of Graduate School of Information Security at Korea University from 2011. For the past 7 years he was an associate professor of Sungkyunkwan University and have 5 years of back ground of team leader of Cryptographic Technology Team and also IT Security Evaluation Team of KISA(Korea Internet & Security Agency). In addition to being a professor, he is positioning a director of CHAOS(Center for High-Assurance Operating Systems), a head of SANE(Security Analysis aNd Evaluation) Lab, an adviser of hacking club ‘CyKor(two-times champion of DEF CON CTF 2015 & 2018)’ of Korea University, and a founder/advisory director of an international security & hacking conference ‘SECUINSIDE’. 

**Yeongjin Jang** - Yeongjin Jang is an assistant professor of Computer Science at Oregon State University. He hacks CPU, OS, iPhone, IoT devices, and anything that is operated by computers, and wish to make systems secure against the vulnerabilities discovered. He is a two-times champion of DEF CON CTF (DEFKOR and DEFKOR00T). Biography

## Disclaimer
Please Note that this is a research project. We are by no means responsible for any usage of this tool. Use on your own behalf. We're not also not responsible if your accounts get banned due to extensive use of this tool.


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

